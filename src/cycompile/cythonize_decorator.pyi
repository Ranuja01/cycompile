from collections import OrderedDict
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, Final, List, Literal, Tuple, TypeVar

from typing_extensions import ParamSpec, TypeAlias

_T = TypeVar('_T')
_P = ParamSpec('_P')

OptimizationProfile: TypeAlias = Literal['safe', 'fast', 'custom']

compiled_func_cache: OrderedDict[str, Callable[..., Any]]

MAX_CACHE_SIZE: Final[Literal[500]]
CACHE_DIR: Final[Path]
IS_WINDOWS: Final[bool]

def clear_cache() -> None: ...
def generate_cython_sources(func: Callable[..., Any]) -> str: ...
def extract_all_imports(
    func: Callable[..., Any], exclude: Tuple[str, ...] = ('cythonize_decorator', 'cycompile')
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
    opt: OptimizationProfile = 'safe',
    extra_compile_args: List[str] | None = None,
    compiler_directives: Dict[str, Any] | None = None,
) -> None: ...
def cycompile(
    opt: OptimizationProfile = 'safe',
    extra_compile_args: List[str] | None = None,
    compiler_directives: Dict[str, Any] | None = None,
    verbose: bool = False,
) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]: ...
