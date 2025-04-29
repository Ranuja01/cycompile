"""
@author: Ranuja Pinnaduwage

This file is part of cycompile, a Python package for optimizing function performance via a Cython decorator.

Description:
This file defines the core logic of the tool.

Copyright (C) 2025 Ranuja Pinnaduwage  
Licensed under the Apache License, Version 2.0 (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software  
distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and  
limitations under the License.
"""

import os
import sys
import inspect
import platform
import hashlib
import time
import tempfile
import contextlib
import io
import ast
import shutil
from pathlib import Path
from functools import wraps
from Cython.Build import cythonize
from setuptools import Extension, setup
from collections import OrderedDict

# Define cache of functions compiled within the same session.
compiled_func_cache = OrderedDict()

# Max number of compiled functions to hold in memory during a single session.
MAX_CACHE_SIZE = 500

# Set the cache directory within the package's directory
package_dir = Path(os.path.dirname(__file__))  # Get the directory where the package is installed
CACHE_DIR = package_dir / 'cycache'  # Set 'cycache' folder within the package directory

# Determine if the platform is Windows.
IS_WINDOWS = platform.system() == "Windows"

def clear_cache():
    
    """
    Clears all files and folders from the cycompile cache directory.

    This function recursively deletes all contents of the cache directory used for
    storing compiled Cython extensions. If some files cannot be deleted (e.g., due to being
    in use), it logs a warning and lists the undeleted paths.

    Logs:
        - If the cache directory does not exist.
        - Status updates during and after the clearing process.
    
    Returns:
        None
    """
    
    path = Path(CACHE_DIR)
    if not path.exists():
        print(f"[cycompile-log] Cache directory does not exist: '{CACHE_DIR}'")
        return

    print(f"[cycompile-log] Clearing cache from: '{CACHE_DIR}'\n")
    undeleted_files = []

    for file in path.rglob("*"):
        try:
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                shutil.rmtree(file)
        except Exception:
            undeleted_files.append(file)

    if undeleted_files:
        print("[cycompile-log] Some files could not be deleted (possibly still in use):")
        for f in undeleted_files:
            print(f" - {f}")
        print("\n[cycompile-log] You may need to restart your Python session to release locked files.")
    else:
        print("[cycompile-log] Cache cleared successfully.")

def generate_cython_source(func):
    
    """
    Generate Cython source code for the given Python function.

    Parameters:
        func (function): The function to generate Cython code for.
    
    Returns:
        str: Cython-compatible source including imports.
    """
    
    # Extract necessary imports and the function's source code.
    imports = extract_all_imports(func)
    source_code = remove_decorators(func)

    # Combine imports and source code into the Cython source.
    cython_source_code = f"{imports}\n\n{source_code}"

    return cython_source_code


def extract_all_imports(func, exclude=("cythonize_decorator", "cycompile")):
    
    """
    Extract all import statements used within the given function.
    
    It also adds the imports for functions and classes defined in the same module 
    that are called by the target function..

    Parameters:
        func (function): The function being analyzed.
        exclude (tuple): Names to exclude from the generated import statements.

    Returns:
        str: Import statements required for the generated Cython file.
    """
    
    # Get the current module where the function is defined.
    current_module = inspect.getmodule(func)
    
    # Get class and function names defined in the same module, excluding the target function itself.
    class_names = get_class_names(current_module)
    function_names = get_function_names(current_module)
    if func.__name__ in function_names:
        function_names.remove(func.__name__)
    
    # Combine the available function and class names.
    available_names = set(function_names + class_names)    
    
    # Get the source code of the function and extract called functions.
    func_source = inspect.getsource(func)
    called_functions = get_called_functions(func_source, available_names)
    called_functions = [name for name in called_functions if name not in exclude]
    
    # Generate import statements for the classes and functions required.
    user_func_imports = "\n".join(
        [f"from {current_module.__name__} import {name}" for name in called_functions]
    )

    # Extract top-level imports from the source file (ignoring excluded ones).
    source_file = inspect.getfile(func)
    script_imports = []

    with open(source_file, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith(("import", "from")):
                if not any(excluded in stripped for excluded in exclude):
                    script_imports.append(line.rstrip())

    script_imports = "\n".join(script_imports)

    # Combine the imports from the file and the imports for functions called within the function.
    return f"{script_imports}\n{user_func_imports}"


def get_class_names(module):
  
    """
    Get all class names defined in the given module.

    Parameters:
        module (module): The module containing the decorated function.

    Returns:
        list: Class names defined in the same module.
    """
    
    return [name for name, obj in inspect.getmembers(module, inspect.isclass)
            if obj.__module__ == module.__name__]


def get_function_names(module):
    
    """
    Get all function names defined in the given module.

    Parameters:
        module (module): The module containing the decorated function.
    
    Returns:
        list: Function names defined in the same module.
    """
    
    return [name for name, _ in inspect.getmembers(module, inspect.isfunction)]


def get_called_functions(func_source, available_functions):    
    
    """
    Extracts the names of functions and classes that are called within the source code
    of a given function. Uses the Abstract Syntax Tree (AST) to parse the code and safely
    detect function calls, distinguishing them from other uses of function and class names.

    Parameters:
        func_source (str): The source code of the function being analyzed.
        available_functions (list): A list of function and class names to check against.

    Returns:
        list: A list of names of user-defined functions and classes called within the provided function.
    """
    
    # Parse the source code into an Abstract Syntax Tree (AST).
    tree = ast.parse(func_source)
    
    called = set()

    # Traverse the AST to find all function call nodes.
    for node in ast.walk(tree):
        # Check if the node represents a function call.
        if isinstance(node, ast.Call):
            # If the function is directly called, e.g., func().
            if isinstance(node.func, ast.Name):
                called.add(node.func.id)
            # If the function is an attribute of an object, e.g., obj.func().
            elif isinstance(node.func, ast.Attribute):
                # Ensure that the function is part of an object or class, e.g., obj.func().
                if isinstance(node.func.value, ast.Name):
                    called.add(node.func.attr)

    # **Filter step**: Remove any functions that aren't part of the available functions in the module.
    # This includes removing functions that are built-ins, or any that are not defined within the module
    # (i.e., functions that are not listed in `available_functions`).
    called = [name for name in called if name in available_functions]
    
    return called


def remove_decorators(func):

    """
    Removes all decorators from a function except @staticmethod, @classmethod, and @property.
    Also strips multi-line decorators (e.g., @cycompile(...)).

    Parameters:
        func (function): The function being analyzed.

    Returns:
        str: The function source code with unwanted decorators stripped.
    """
    
    # Acquire the source code and split it into individual lines.
    source = inspect.getsource(func)
    lines = source.splitlines()
    stripped_lines = []

    # List of decorators to preserve.
    keep_decorators = ("@staticmethod", "@classmethod", "@property")
    
    # Track whether we're inside a multi-line decorator.
    in_decorator = False

    for line in lines:
        stripped = line.strip()

        if in_decorator:
            # If currently skipping a multi-line decorator, check if this is the closing line.
            if stripped.endswith(")"):
                in_decorator = False  # Stop skipping after this line.
            continue  # Skip this line regardless.

        if stripped.startswith("@"):
            if any(stripped.startswith(decorator) for decorator in keep_decorators):
                # Keep this line if it's a decorator we want to preserve.
                stripped_lines.append(line)
            elif not stripped.endswith(")"):
                # If it's a multi-line decorator, start skipping.
                in_decorator = True
            # Otherwise, it's a single-line decorator we want to skip — do nothing.
        else:
            # Not a decorator — it's part of the actual function, keep it.
            stripped_lines.append(line)

    return "\n".join(stripped_lines)


def run_cython_compile(pyx_path, output_dir, verbose, opt="safe",
                       extra_compile_args=None, compiler_directives=None):
    
    """
    Compiles a Cython file using the specified optimization profile.
    Supports custom compiler directives and flags, including profile overrides.

    Parameters:
        pyx_path (str): Path to the Cython (.pyx) file to compile.
        output_dir (str): Directory where the compiled file should be saved.
        verbose (bool): Whether to enable verbose output during compilation.
        opt (str): Optimization profile to use ("safe", "fast", or "custom").
        extra_compile_args (list, optional): Additional compiler flags (used for "custom" or to override profiles).
        compiler_directives (dict, optional): Cython compiler directives (used for "custom" or to override profiles).

    Returns:
        None
    """
    
    # Ensure output directory exists.
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract the base filename (without extension) for naming the compiled module.
    base_name = pyx_path.stem

    # Define supported optimization profiles.
    opt_profiles = {
        "safe": {
            "directives": {
                'language_level': 3,  # Python 3 compatibility.
            },
            "flags": [],
        },
        "fast": {
            "directives": {
                'language_level': 3,
                'boundscheck': False,  # Disable bounds checking for performance.
                'wraparound': False,   # Disable negative indexing.
                'cdivision': True,     # Use C-style division for speed.
                'nonecheck': False,    # Skip None-checking.
            },
            "flags": (
                ["/O2", "/fp:fast", "/GL", "/arch:AVX2"] if IS_WINDOWS else  # Optimize for speed (MSVC).
                ["-Ofast", "-march=native", "-flto", "-funroll-loops", "-ffast-math"]  # Aggressive GCC/Clang optimizations.
            ),
        }
    }

    # Determine the directives and flags to use based on the selected profile.
    if opt == "custom":
        # Custom profile: use only user-provided values.
        directives = compiler_directives or {}
        flags = extra_compile_args or []
    else:
        # Use predefined profile with optional user overrides.
        profile = opt_profiles.get(opt.lower(), opt_profiles["safe"])        
        directives = {**profile["directives"], **(compiler_directives or {})}
        flags = profile["flags"] + (extra_compile_args or [])

    # Add the cache directory to sys.path for the compilation process.
    sys.path.append(str(CACHE_DIR))  # Add cache path to sys.path

    try:
        # Use a temporary build directory to store intermediate build artifacts.
        with tempfile.TemporaryDirectory() as temp_build_dir:
            
            # Define the Cython extension module with compile-time settings.
            ext = Extension(
                name=base_name,
                sources=[str(pyx_path)],
                extra_compile_args=flags,
            )

            # Compile the Cython code using setuptools.
            # If verbose is True, display the full compiler output.
            # If verbose is False, suppress the stdout and stderr during compilation for a cleaner user experience.
            # The `quiet` flag for `cythonize()` also controls whether Cython outputs its internal messages.
            
            if verbose:
                # Verbose mode: Show full compiler output to the user.
                setup(
                    script_args=["build_ext", "--build-lib", output_dir, "--build-temp", temp_build_dir],
                    ext_modules=cythonize([ext], compiler_directives=directives, quiet=False),
                )
            else:
                # Quiet mode: Suppress all build output for a cleaner experience.
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    setup(
                        script_args=["build_ext", "--build-lib", output_dir, "--build-temp", temp_build_dir],
                        ext_modules=cythonize([ext], compiler_directives=directives, quiet=True),
                    )

    finally:
        # Remove the cache directory from sys.path after the function is loaded.
        sys.path.pop()


def cycompile(opt="safe", extra_compile_args=None, compiler_directives=None, verbose = False):
    
    """
    A decorator factory for compiling Python functions into optimized Cython extensions at runtime.
    
    Parameters:
        opt (str): Optimization profile to use ("safe", "fast", or "custom").
        extra_compile_args (list, optional): Additional compiler flags (used for "custom" or to override profiles).
        compiler_directives (dict, optional): Cython compiler directives (used for "custom" or to override profiles).
        verbose (bool): Whether to enable verbose output during tool usage.

    Returns:
        function: A decorator that compiles the wrapped function with the specified options.
    """
    
    # Create the directory if it doesn't exist.
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(parents=True)
    
    # Will store the compiled function once generated.
    compiled_func = None
    
    def decorator(func):
        
        """
        The actual decorator that wraps and compiles the target function.
        
        Parameters:
            func (function): The Python function to be compiled.
        
        Returns:
            callable: A wrapper that compiles the function on first call and caches it.
                      Subsequent calls use the compiled version for better performance
        """
        
        @wraps(func)
        def wrapper(*args, **kwargs):  
            
            """
            Wrapper function that calls the Cython-compiled version of the function after it has been compiled.
        
            Parameters:
                *args (tuple): Positional arguments to pass to the Cython-compiled function.
                **kwargs (dict): Keyword arguments to pass to the Cython-compiled function.
        
            Returns:
                Any: The result of calling the compiled version of the function.
            """
            
            nonlocal compiled_func
            
            # Check if the compiled function is already available. If it is, call it directly.
            # This ensures that the compiled function is lazily loaded when needed.
            if compiled_func is not None:
                return compiled_func(*args, **kwargs)
 
            # Prepare parameters for generating a unique hash key.
            params = (str(compiler_directives) if compiler_directives is not None else "") + \
                     (str(extra_compile_args) if extra_compile_args is not None else "") + \
                     str(opt)
            
            # Generate a unique hash key for this function and its parameters, which will be used to locate or create the compiled function.
            hash_key = "mod_" + hashlib.md5((params + inspect.getsource(func)).encode()).hexdigest()
         
            # Determine the correct extension based on the operating system (Windows or not).
            if IS_WINDOWS:
                extension = "pyd"
            else:
                extension = "so"
            
            # Check if a compiled version of the function already exists in the cache folder.
            compiled_matches = list(CACHE_DIR.glob(f"{hash_key}*.{extension}"))
            
            if compiled_matches:
                # If a match is found in the in-memory cache, use it.
                if hash_key in compiled_func_cache:
                    if verbose:
                        print(f"[cycompile-log] Using cached compiled version for {func.__name__} from this session.")
                    compiled_func = compiled_func_cache[hash_key]
                    return compiled_func(*args, **kwargs)
                else:
                    # If a match is found in the cache directory, use it.
                    if verbose:
                        print(f"[cycompile-log] Using cached compiled version for {func.__name__} from cache folder.")
            else:
                # If no matching compiled file is found, we proceed to compile the function.
                
                # Generate the Cython source code for the function (including imports and source code).
                source_code = generate_cython_source(func)
                
                # Print verbose messages if enabled, including compile options.
                if verbose:
                    print(f"[cycompile-log] Compiling {func.__name__} with options: {opt}")
                    print(f"[cycompile-log] Extra compile args: {extra_compile_args}")
                    print(f"[cycompile-log] Compiler directives: {compiler_directives}")
                    
                    start_time = time.time()
            
                # Write the generated source code to a temporary .pyx file.
                pyx_file = CACHE_DIR / f"{hash_key}.pyx"
                with open(pyx_file, "w") as f:
                    f.write(source_code)
                
                # Compile the Cython source into a shared object (.so or .pyd) file.
                run_cython_compile(
                    pyx_file,
                    CACHE_DIR,
                    verbose,
                    opt=opt,
                    extra_compile_args=extra_compile_args,
                    compiler_directives=compiler_directives
                )
                
                if verbose:
                    print(f"[cycompile-log] Compilation took {time.time() - start_time:.2f} seconds.")
              
            # Add the cache directory to sys.path so Python can find the .so file.
            sys.path.append(str(CACHE_DIR))
            
            try:
                # Dynamically import the compiled module using the hash key.
                module = __import__(hash_key)
                
                # Retrieve the function object from the compiled module.
                compiled_func = getattr(module, func.__name__)
                
                # If the cache exceeds the maximum size, remove the oldest cached function to free up space.
                if len(compiled_func_cache) >= MAX_CACHE_SIZE:
                    compiled_func_cache.popitem(last=False)
                
                # Cache the compiled function for future use.
                compiled_func_cache[hash_key] = compiled_func
            
            finally:
                # Remove the cache directory from sys.path after the function is loaded.
                sys.path.pop()
            
            # Call the compiled function and return its result.
            return compiled_func(*args, **kwargs)
        
        return wrapper
    return decorator
