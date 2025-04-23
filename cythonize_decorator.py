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

# Define cache of functions compiled within the same session
compiled_func_cache = OrderedDict()
MAX_CACHE_SIZE = 500

# Directory for cython and compiled binary files
CACHE_DIR = Path.cwd() / '.cycache'

# Create the directory if it doesn't exist
if not CACHE_DIR.exists():
    CACHE_DIR.mkdir(parents=True)

# Windows has a separate (.pyd) extension
IS_WINDOWS = platform.system() == "Windows"

def generate_cython_source(func):

    # Extract imports from the original Python file
    imports = extract_all_imports(func)

    # Get the function's source code without decorators
    source_code = remove_decorators(func)

    # Add imports to the Cython file source code
    cython_source_code = f"{imports}\n\n{source_code}"

    return cython_source_code

def extract_all_imports(func, exclude=("cythonize_decorator", "cycompile")):
    """
    Extracts all import statements and the functions being used within the provided function.
    It also adds the necessary imports for functions defined in the same module that are being called.
    """

    # Step 1: Get the current module where the function is defined
    current_module = inspect.getmodule(func)
    function_names = get_function_names(current_module)

    # Remove the function being compiled from the list of available functions
    if func.__name__ in function_names:
        function_names.remove(func.__name__)

    # Get the source code of the function to check which functions it calls
    func_source = inspect.getsource(func)

    # Step 2: Extract the names of functions being called inside the function
    called_functions = get_called_functions(func_source, function_names)
    # Step 3: Filter out the excluded function names from the called functions list
    called_functions = [name for name in called_functions if name not in exclude]
    
    # Import statements for other functions in the same module that are called within the function
    user_func_imports = "\n".join(
        [f"from {current_module.__name__} import {name}" for name in called_functions]
    )

    # Step 3: Extract top-level imports from the source file (ignoring excluded ones)
    source_file = inspect.getfile(func)
    script_imports = []

    with open(source_file, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith(("import", "from")):
                if not any(excluded in stripped for excluded in exclude):
                    script_imports.append(line.rstrip())

    script_imports = "\n".join(script_imports)

    # Combine the imports from the file and the imports for functions called within the function
    return f"{script_imports}\n{user_func_imports}"

def get_function_names(module):
    """
    Get a list of function names defined in the same module.
    """
    return [name for name, obj in inspect.getmembers(module, inspect.isfunction)]

def get_called_functions(func_source, available_functions):
    """
    Extracts function names that are called inside the function's source code.
    Uses the Abstract Syntax Tree (AST) to safely parse the code and detect
    actual function calls, ignoring other uses of function names.
    """
    # Parse the source code into an AST
    tree = ast.parse(func_source)
    
    called = set()

    # Traverse the AST
    for node in ast.walk(tree):
        # Check if the node is a function call
        if isinstance(node, ast.Call):
            # Get the name of the function being called (node.func can be a name or an attribute)
            if isinstance(node.func, ast.Name):  # direct function call, e.g., func()
                called.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):  # attribute-based call, e.g., obj.func()
                if isinstance(node.func.value, ast.Name):  # only consider the function if it's part of a class or object
                    called.add(node.func.attr)
    
    # Filter out any functions not in the available functions list
    called = [name for name in called if name in available_functions]
    
    return called

def remove_decorators(func):
    """
    Removes all decorators except @staticmethod, @classmethod, and @property,
    including multi-line decorators (e.g., @cycompile(...)).
    """
    source = inspect.getsource(func)
    lines = source.splitlines()
    stripped_lines = []

    keep_decorators = ("@staticmethod", "@classmethod", "@property")
    
    in_decorator = False

    for line in lines:
        stripped = line.strip()

        if in_decorator:
            # Continue skipping lines until we find a line ending with a closing paren
            if stripped.endswith(")"):
                in_decorator = False
            continue

        if stripped.startswith("@"):
            if any(stripped.startswith(decorator) for decorator in keep_decorators):
                stripped_lines.append(line)
            elif not stripped.endswith(")"):
                in_decorator = True  # Start skipping a multi-line decorator
            # Else skip single-line decorator
        else:
            stripped_lines.append(line)

    return "\n".join(stripped_lines)

def run_cython_compile(pyx_path, output_dir, verbose, opt="safe",
                       extra_compile_args=None, compiler_directives=None):

    os.makedirs(output_dir, exist_ok=True)
    base_name = pyx_path.stem

    opt_profiles = {
    "safe": {
        "directives": {
            'language_level': 3,
        },
        "flags": [],
    },
    "fast": {
        "directives": {
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
            'nonecheck': False,
        },
        "flags": (
            ["/O2"] if IS_WINDOWS else  # MSVC: Optimize for speed
            ["-Ofast", "-march=native", "-flto", "-funroll-loops", "-ffast-math"]
        ),
    }
}

    # Resolve directives and flags
    if opt == "custom":
        directives = compiler_directives or {}
        flags = extra_compile_args or []
    else:
        profile = opt_profiles.get(opt.lower(), opt_profiles["safe"])
        # Merge in user overrides if provided
        directives = {**profile["directives"], **(compiler_directives or {})}
        flags = profile["flags"] + (extra_compile_args or [])

    with tempfile.TemporaryDirectory() as temp_build_dir:
        ext = Extension(
            name=base_name,
            sources=[str(pyx_path)],
            extra_compile_args=flags,
        )
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            setup(
                script_args=["build_ext", "--build-lib", output_dir, "--build-temp", temp_build_dir],
                ext_modules=cythonize([ext], compiler_directives=directives, quiet= not verbose),
            )

def cycompile(opt="safe", extra_compile_args=None, compiler_directives=None, verbose = False):
    
    compiled_func = None
    
    def decorator(func):
       
        @wraps(func)
        def wrapper(*args, **kwargs):            
            nonlocal compiled_func
            
            # Added this check to ensure the compiled function is only lazily loaded when needed, 
            # and avoid using incorrect or uncompiled wrappers during mutual recursion calls.

            if compiled_func is not None:
                return compiled_func(*args, **kwargs)
 
            
            params = (str(compiler_directives) if compiler_directives is not None else "") + \
                     (str(extra_compile_args) if extra_compile_args is not None else "") + \
                     str(opt)
            
            hash_key = "mod_" + hashlib.md5((params + inspect.getsource(func)).encode()).hexdigest()
         
            if IS_WINDOWS:
                extension = "pyd"
            else:
                extension = "so"
            
            # Look for any matching compiled file starting with the hash
            compiled_matches = list(CACHE_DIR.glob(f"{hash_key}*.{extension}"))
            
            if compiled_matches:
                
                if hash_key in compiled_func_cache:
                    if verbose:
                        print(f"Using cached compiled version for {func.__name__}.")
                    compiled_func = compiled_func_cache[hash_key]
                    return compiled_func(*args, **kwargs)    
            else:
                
                # Add the imports and source code to the .pyx file content
                source_code = generate_cython_source(func)
                if verbose:
                    print(f"Compiling {func.__name__} with options: {opt}")
                    print(f"Extra compile args: {extra_compile_args}")
                    print(f"Compiler directives: {compiler_directives}")
                    
                    start_time = time.time()
            
                # Write the .pyx source
                pyx_file = CACHE_DIR / f"{hash_key}.pyx"
                with open(pyx_file, "w") as f:
                    f.write(source_code)
            
                # Compile it
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
              
            # Add the cache directory to sys.path so Python can find the .so file
            sys.path.append(str(CACHE_DIR))
            
            try:
                # module_name = compiled_file.stem
                # Dynamically import the compiled .so file using the hash_key
                module = __import__(hash_key)
                compiled_func = getattr(module, func.__name__)               
                
                # Later when inserting:
                if len(compiled_func_cache) >= MAX_CACHE_SIZE:
                    compiled_func_cache.popitem(last=False)  # Remove the oldest
                compiled_func_cache[hash_key] = compiled_func
                                
                
            finally:
                sys.path.pop()
    
            return compiled_func(*args, **kwargs)
        
        return wrapper
    return decorator
