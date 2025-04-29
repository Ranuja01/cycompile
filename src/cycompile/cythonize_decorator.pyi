from collections import OrderedDict
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, Final, Iterable, List, Literal, Optional, TypeVar

from typing_extensions import ParamSpec

_T = TypeVar('_T')
_P = ParamSpec('_P')

compiled_func_cache: OrderedDict[str, Callable[..., Any]]

MAX_CACHE_SIZE: Final[Literal[500]]
CACHE_DIR: Final[Path]
IS_WINDOWS: Final[bool]

def clear_cache() -> None: ...
def generate_cython_sources(func: Callable[..., Any]) -> str: ...
def extract_all_imports(
    func: Callable[..., Any],
    # I don't think it's necessary to limit the type annotation strictly to a tuple,
    # as in reality any iterable yielding strings would be appropriate.
    exclude: Iterable[str] = ('cythonize_decorator', 'cycompile'),
) -> str: ...
def get_class_names(module: ModuleType) -> List[str]: ...
def get_function_names(module: ModuleType) -> List[str]: ...
def get_called_functions(func_source: str, available_functions: List[str]) -> List[str]: ...
def get_constant_names(module: ModuleType) -> List[str]: ...
def get_used_constants(func_source: str, available_constants: List[str]) -> List[str]: ...
def remove_decorators(func: Callable[..., Any]) -> str: ...
def run_cython_compile(
    pyx_path: str,
    output_dir: str,
    verbose: bool,
    opt: Literal['safe', 'fast', 'custom'] = 'safe',
    extra_compile_args: Optional[List[str]] = None,
    compiler_directives: Optional[Dict[str, Any]] = None,
) -> None: ...
def cycompile(
    opt: Literal['safe', 'fast', 'custom'] = 'safe',
    extra_compile_args: Optional[List[str]] = None,
    compiler_directives: Optional[Dict[str, Any]] = None,
    verbose: bool = False,
) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]: ...
