import os
import sys
import inspect
import platform
import pyximport
import subprocess
import hashlib
import time
import shutil
import tempfile
import contextlib
import io
import pathlib
from pathlib import Path
from functools import wraps
from Cython.Build import cythonize
from setuptools import Extension, setup
from cython import compile

CACHE_DIR = Path.cwd() / '.cycache'

if not CACHE_DIR.exists():
    CACHE_DIR.mkdir(parents=True)

# Windows has a separate (.pyd) extension
IS_WINDOWS = platform.system() == "Windows"

def extract_all_imports(func, exclude=("cythonize_decorator", "cycompile")):

    # Step 1: Get the current module where the function is defined
    current_module = inspect.getmodule(func)
    function_names = get_function_names(current_module)

    # Remove the function being compiled
    if func.__name__ in function_names:
        function_names.remove(func.__name__)

    # Import statements for other functions in the same module
    user_func_imports = "\n".join(
        [f"from {current_module.__name__} import {name}" for name in function_names]
    )

    # Step 2: Extract top-level imports from the source file (ignoring excluded ones)
    source_file = inspect.getfile(func)
    script_imports = []

    with open(source_file, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith(("import", "from")):
                if not any(excluded in stripped for excluded in exclude):
                    script_imports.append(line.rstrip())

    script_imports = "\n".join(script_imports)

    # Combine both
    return f"{script_imports}\n{user_func_imports}"

def generate_cython_source(func):

    # Extract imports from the original Python file
    imports = extract_all_imports(func)

    # Get the function's source code without decorators
    source_code = remove_decorators(func)

    # Add imports to the Cython file source code
    cython_source_code = f"{imports}\n\n{source_code}"

    return cython_source_code

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

def get_function_names(module):
    """
    Get a list of function names defined in the same module.
    """
    return [name for name, obj in inspect.getmembers(module, inspect.isfunction)]

def run_cython_compile(pyx_path, output_dir, verbose, opt="safe",
                       extra_compile_args=None, compiler_directives=None):

    os.makedirs(output_dir, exist_ok=True)
    base_name = pyx_path.stem

    # Built-in profiles
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
            "flags": ["-Ofast", "-march=native", "-flto", "-funroll-loops", "-ffast-math"],
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
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            
            # Add the imports and source code to the .pyx file content
            source_code = generate_cython_source(func)
            
            params = (str(compiler_directives) if compiler_directives is not None else "") + \
                     (str(extra_compile_args) if extra_compile_args is not None else "") + \
                     str(opt)
            
            hash_key = "mod_" + hashlib.md5((params + source_code).encode()).hexdigest()
            
            if IS_WINDOWS:
                extension = "pyd"
            else:
                extension = "so"
            
            # Look for any matching compiled file starting with the hash
            compiled_matches = list(CACHE_DIR.glob(f"{hash_key}*.{extension}"))
            
            if compiled_matches:
                if verbose:
                    print(f"Using cached compiled version for {func.__name__}.")
            else:
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
                return compiled_func(*args, **kwargs)
            finally:
                # Clean up by removing the cache directory from sys.path
                sys.path.pop()
    
        return wrapper
    return decorator
