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

# Helper function to determine the OS and select file extension
def get_shared_lib_extension():
    if IS_WINDOWS:
        return ".pyd"
    else:  # Linux, Darwin
        return ".so"

# Check if the function is already compiled
def is_compiled(func):
    try:
        # Look for the compiled version of the function
        func.__module__  # Check if this attribute exists (this is usually available in compiled Cython modules)
        return True
    except AttributeError:
        return False

def remove_decorators(func):
    """
    This function strips decorators from the source code of a function,
    but avoids removing important decorators like @staticmethod, @classmethod, and @property.
    """
    source = inspect.getsource(func)
    lines = source.splitlines()
    stripped_lines = []
    
    # Flags to identify decorators that we need to keep
    keep_decorators = ("@staticmethod", "@classmethod", "@property")
    
    # Remove decorator lines, but keep the necessary ones
    for line in lines:
        if any(line.strip().startswith(decorator) for decorator in keep_decorators):
            stripped_lines.append(line)  # Keep these decorators
        elif not line.strip().startswith("@"):  # Don't keep non-function decorators
            stripped_lines.append(line)
    
    return "\n".join(stripped_lines)

def run_cython_compile(pyx_path, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    base_name = pyx_path.stem  # name without extension

    # Build inside a temporary directory to avoid weird path behavior
    with tempfile.TemporaryDirectory() as temp_build_dir:
        ext = Extension(
            name=base_name,
            sources=[str(pyx_path)],
        )

        setup(
            script_args=["build_ext", "--build-lib", output_dir, "--build-temp", temp_build_dir],
            ext_modules=cythonize([ext], compiler_directives={'language_level': "3"}),
        )
    

# Compile the function if necessary
def compile_func(func):
    """
    Compile the function into a .so/.pyd shared object if it's not already compiled.
    """
    source_code = inspect.getsource(func)
    shared_lib_ext = get_shared_lib_extension()

    # Generate a unique file name based on the function name
    pyx_file_path = f"~/.cycache/{func.__name__}.pyx"
    so_file_path = f"~/.cycache/{func.__name__}{shared_lib_ext}"

    # Only recompile if the source code has changed
    if not os.path.exists(so_file_path) or os.path.getmtime(pyx_file_path) < os.path.getmtime(so_file_path):
        # Create .pyx file with the function's source code
        with open(pyx_file_path, "w") as f:
            f.write(source_code)
        
        # Compile the .pyx to .so or .pyd using Cython
        compile.pyximport(pyx_file_path, force=True)

    # Replace the original function with the compiled version
    replace_with_compiled(func, so_file_path)

def replace_with_compiled(func, so_file_path):
    """
    Replace the function with its compiled version loaded from the shared object.
    """
    compiled_func = __import__(so_file_path)  # Import the compiled module
    setattr(func, compiled_func.__name__)

def cycompile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the function source code without decorators
        source_code = remove_decorators(func)
        hash_key = "mod_" + hashlib.md5(source_code.encode()).hexdigest()
        
        if IS_WINDOWS:
            extension = "pyd"
        else:
            extension = "so"
        
        # Look for any matching compiled file starting with the hash
        compiled_matches = list(CACHE_DIR.glob(f"{hash_key}*.{extension}"))
        
        if compiled_matches:
            compiled_file = compiled_matches[0]
            print(f"Using cached compiled version for {func.__name__}.")
        else:
            compiled_file = None
            print(f"Compiling {func.__name__}...")
            start_time = time.time()
        
            # Write the .pyx source
            pyx_file = CACHE_DIR / f"{hash_key}.pyx"
            with open(pyx_file, "w") as f:
                f.write(source_code)
        
            # Compile it
            run_cython_compile(pyx_file, CACHE_DIR)
        
            # After compile, find the resulting .pyd/.so
            compiled_matches = list(CACHE_DIR.glob(f"{hash_key}*.{extension}"))
            if not compiled_matches:
                raise FileNotFoundError(f"Compiled file not found after compiling {pyx_file}")
            
            compiled_file = compiled_matches[0]
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
