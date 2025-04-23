"""
@author: Ranuja Pinnaduwage

This file is part of cycompile, a Python package for optimizing function performance via a Cython decorator.

Description:
This file defines the initialization of the package.

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

# Create the directory if it doesn't exist.
if not CACHE_DIR.exists():
    CACHE_DIR.mkdir(parents=True)

# Determine if the platform is Windows.
IS_WINDOWS = platform.system() == "Windows"

def generate_cython_source(func):
    """
    Generates the Cython source code for the given function.

    Parameters:
    - func: The function to generate Cython code for.
    
    Returns:
    - A string containing the Cython source code.
    """
    
    # Extract necessary imports and the function's source code.
    imports = extract_all_imports(func)
    source_code = remove_decorators(func)

    # Combine imports and source code into the Cython source.
    cython_source_code = f"{imports}\n\n{source_code}"

    return cython_source_code


def extract_all_imports(func, exclude=("cythonize_decorator", "cycompile")):
    
    """
    Extracts all import statements and the functions being used within the provided function.
    It also adds the necessary imports for functions defined in the same module that are being called.

    Parameters:
    - func: A reference to the function being decorated.
    - exclude: A tuple holding imports to be exluded from the cython file.
    
    Returns:
    - string representing the import statements needed for the final file.
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
    Get a list of class names defined in the same module.

    Parameters:
    - module: A reference to the module where the decorated function is from.    
    
    Returns:
    - list of class names.
    """
    
    return [name for name, obj in inspect.getmembers(module, inspect.isclass)
            if obj.__module__ == module.__name__]


def get_function_names(module):
    """
    Get a list of function names defined in the same module.

    Parameters:
    - module: A reference to the module where the decorated function is from.
    
    Returns:
    - list of function names.
    """
    
    return [name for name, obj in inspect.getmembers(module, inspect.isfunction)]


def get_called_functions(func_source, available_functions):    
    
    """
    Extracts the names of functions and methods that are called inside the source code
    of a given function. Uses the Abstract Syntax Tree (AST) to parse the code and safely
    detect function calls, ignoring other uses of function names.

    Parameters:
    - func_source: The source code of the function being analyzed.
    - available_functions: A list of function and class names in the module to check against.

    Returns:
    - A list of names of functions and methods that are called within the function.
    """
    
    # Parse the source code into an Abstract Syntax Tree (AST).
    tree = ast.parse(func_source)
    
    called = set()

    # Traverse the AST to find function calls.
    for node in ast.walk(tree):
        # Check if the node is a function call.
        if isinstance(node, ast.Call):
            # If the function is directly called, e.g., func().
            if isinstance(node.func, ast.Name):
                called.add(node.func.id)
            # If the function is an attribute of an object, e.g., obj.func().
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):  # Ensure it's part of a class or object.
                    called.add(node.func.attr)
    
    # Filter out any functions not in the available functions list.
    called = [name for name in called if name in available_functions]
    
    return called


def remove_decorators(func):

    """
    Removes all decorators except @staticmethod, @classmethod, and @property.
    Also strips multi-line decorators (e.g., @cycompile(...)).


    Parameters:
    - func: A reference to the function being decorated.

    Returns:
    - The function source code with unwanted decorators stripped.
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
    Compiles the given Cython code using a selected optimization profile.
    Supports custom compiler directives and flags, including profile overrides.

    Parameters:
    - pyx_path: Path to the Cython (.pyx) file to compile.
    - output_dir: Directory where the compiled file should be saved.
    - verbose: Whether to enable verbose output during compilation.
    - opt: Optimization profile to use ("safe", "fast", or "custom").
    - extra_compile_args: Optional list of compiler flags (used for "custom" or to override profiles).
    - compiler_directives: Optional dictionary of Cython compiler directives (used for "custom" or to override profiles).
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
                ["/O2"] if IS_WINDOWS else  # Optimize for speed (MSVC).
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
    - opt: Optimization profile ('safe', 'fast', or 'custom').
    - extra_compile_args: Custom compiler flags (optional).
    - compiler_directives: Cython compiler directives (optional).
    - verbose: If True, prints detailed logs of the compilation process.

    Returns:
    - A decorator that compiles the wrapped function with the specified options.
    """
    
    # Will store the compiled function once generated.
    compiled_func = None
    
    def decorator(func):
        
        """
        Inner decorator that wraps the target function.
        
        Parameters:
        - func: A reference to the Python function to be compiled.
        
        Returns:
        - A callable that wraps the original function. On first call, it compiles the function using Cython and caches the result.
          Subsequent calls are dispatched directly to the compiled version for improved performance.
        """
        
        @wraps(func)
        def wrapper(*args, **kwargs):  
            
            """
            Wrapper function that calls the Cython-compiled version of the function after it has been compiled.
        
            Parameters:
            - *args: Positional arguments to pass to the Cython-compiled function.
            - **kwargs: Keyword arguments to pass to the Cython-compiled function.
        
            Returns:
            - The result of calling the Cython-compiled version of the function.
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
                        print(f"Using cached compiled version for {func.__name__} from this session.")
                    compiled_func = compiled_func_cache[hash_key]
                    return compiled_func(*args, **kwargs)
                else:
                    # If a match is found in the cache directory, use it.
                    if verbose:
                        print(f"Using cached compiled version for {func.__name__} from cache folder.")
            else:
                # If no matching compiled file is found, we proceed to compile the function.
                
                # Generate the Cython source code for the function (including imports and source code).
                source_code = generate_cython_source(func)
                
                # Print verbose messages if enabled, including compile options.
                if verbose:
                    print(f"Compiling {func.__name__} with options: {opt}")
                    print(f"Extra compile args: {extra_compile_args}")
                    print(f"Compiler directives: {compiler_directives}")
                    
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
                    print(f"Compilation took {time.time() - start_time:.2f} seconds.")
              
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
