# CyCompile: Democratizing Performance
`CyCompile` is a Python package designed to help developers bring native C/C++ level performance to Python functions with just a simple decorator.
## About This Project

`CyCompile` is a decorator-based tool for Python developers who want native performance without sacrificing the simplicity and flexibility of pure Python. Built on top of **Cython**, it compiles individual Python functions into binary modules with a one-time performance cost, then seamlessly reuses them via intelligent caching for future calls.

This project was born out of a desire to **democratize performance optimization**. Too often, speeding up Python code means diving into Cython-specific syntax, manually restructuring your logic, or switching to a different language altogether. `CyCompile` aims to change that by making it as easy as adding a decorator.

Unlike `Numba's` njit, which may implicitly compile all helper functions and dependencies, and `Cython's` cython.compile(), which can be used for function-level compilation but is more commonly applied in full-module or .pyx workflows, `CyCompile's` cycompile is designed specifically for precise, **function-by-function optimization**.

It enables **targeted acceleration** of individual functions, making it especially well-suited for **notebooks**, **rapid prototyping**, or **production environments** where **precise performance improvements** are needed without impacting the rest of the codebase.

At its core, this project is about **lowering the barrier** between Python's elegance and C-level speed, empowering more developers to harness performance when they need it, without becoming compiler experts.

Where it stands out:

- **Non-invasive design** &mdash; requires no changes to your existing project structure or imports, just add a decorator.
- **Understands standard Python type hints** &mdash; avoiding the need for Cython-specific rewrites.
- **Handles recursive functions** &mdash; overcoming a common limitation in traditional function-level compilation tools.
- **Supports user-defined objects** and custom logic more gracefully than many static compilers.
- **Offers fine-grained control** over Cython directives and compiler flags for advanced users.
- **Intelligent source-based caching** &mdash; automatically avoids unnecessary recompilation by detecting source changes.
- **Includes a manual cache cleanup option** &mdash; giving developers control over the binary cache when desired.

**Note:** Throughout this README, you'll see `CyCompile` used as the name of the project, reflecting the branding and overall mission of the tool. When referring to the actual Python package or the module itself, I use cycompile in lowercase, which is the official package name on PyPI.

**Note:** This project includes C++ components and requires the ability to compile both C++ and Python code. While the required Python components are automatically included during installation, you must ensure you have a C++ compiler installed to build the necessary C++ files. Please refer to the build requirements below for more information.

**Note:** This project includes additional documentation that provides a deeper dive into various use cases. You can find the full write-up on Medium [here](https://medium.com/@ranuja.pinnaduwage/cycompile-practical-use-cases-for-function-level-optimization-68eb6300b225).

## Build Requirements
Ensure you have Python 3.8 or later installed on your system, along with an updated version of pip. All required Python dependencies will be automatically installed during package installation.

For full functionality, you must have a C++ compiler installed. If you do not already have one, follow the instructions below to install it.

### Windows  
- Download and install **Microsoft Visual C++ Build Tools 2022** or later from:  
  [https://visualstudio.microsoft.com/visual-cpp-build-tools/](https://visualstudio.microsoft.com/visual-cpp-build-tools/)  
- During installation, ensure you select the following:
  - **C++ CMake tools for Windows**
  - **MSVC compiler**
- To verify you have correctly installed the C++ compiler run this in the **Developer Command Prompt for Visual Studio** (not the regular command prompt):
  ```sh
  cl
  ```
- **Note** Simply installing MSVC build tools may not properly configure your system. You may need to set environment variables or update your system's PATH to include cl.exe.

### Linux  
- Install the necessary C++ compiler and build tools:
  - For Ubuntu: 
  ```sh
  sudo apt update && sudo apt install build-essential
  ```
  - For Fedora:
  ```sh
  sudo dnf install gcc-c++ make
  ```
- To verify you have correctly installed the C++ compiler run this in a terminal:
  ```sh
  g++ --version 
  ```

### For MacOS
- Install Apple's command-line developer tools (includes clang for C++):
  
  ```sh
  xcode-select --install
  ```
- To verify you have correctly installed the C++ compiler run this in a terminal:
  ```sh
  g++ --version 
  ``` 

## Download
To download this package, use the following instructions:
  ```sh
  pip install cycompile
  ```
If this does not work, then simply:
  ```sh
  pip install git+https://github.com/Ranuja01/cycompile.git
  ```
## Example Usage
To use the module, simply import cycompile:
```python
import cycompile
```
However, for cleaner and more direct code, it's recommended to import the decorator directly:
```python
from cycompile import cycompile
```
**Note:** The first execution of a tagged function compiles it into a C-based binary, meaning it will take longer than usual (a few seconds extra). After this, the speed improvements will be permanent as long as the cache is not emptied and the function or the compilation settings have not changed.

You can now bring C/C++ level performance to any function with a single decorator. Below are a few examples demonstrating the `CyCompile` tool in action. If you're looking for a deeper dive with performance comparisons, advanced configurations, and more complex use cases, check out the full walkthrough on [Medium](https://medium.com/@ranuja.pinnaduwage/cycompile-practical-use-cases-for-function-level-optimization-68eb6300b225).

The following examples are excerpts from the [examples folder](https://github.com/Ranuja01/cycompile/tree/main/examples) in this repository, with full walkthroughs available in the accompanying [Medium article](https://medium.com/@ranuja.pinnaduwage/cycompile-practical-use-cases-for-function-level-optimization-68eb6300b225).

### Basic Usage ###
Here's a simple demonstration of how to use `CyCompile's`cycompile decorator:
```python
from cycompile import cycompile

@cycompile()
def simple_function():    
    print("[cycompile] This is a simple function.")
```
The first time simple_function is called, it will be compiled into a binary. On subsequent calls, the cached binary will be reused bringing C-level performance with intelligent, collision-free caching. Compiled binaries are reused automatically, but can also be cleared manually when needed. The next example showcases `CyCompile's` ability to clear its compiled binary cache:
```python
from cycompile import clear_cache

clear_cache()
```
With this, the user can control how large the cache becomes on their system.

### Using User-Defined and Imported Functions ###
Now let's look at a more sophisticated example that incorporates a user-defined helper function and an imported library:
```python
from cycompile import cycompile
import numpy as np

# A regular Python function
def cube(n):
    return n ** 3

# A compiled function that calls both cube() and uses NumPy
@cycompile(verbose=True)
def sum_of_cubes(n):
    result = 0.0
    for i in range(1, n + 1):
        result += cube(i)
    return np.array(result)

# Demonstration
print(sum_of_cubes(10**4))
```
In this example, the decorated sum_of_cubes function is compiled, but its helper cube() remains a regular Python function. This showcases a key feature of cycompile: selective compilation. You can choose exactly which parts of your code should be accelerated, without refactoring or wrapping entire modules.

Additionally, this example highlights smooth compatibility with external libraries like NumPy, reinforcing how cycompile feels like regular Python, just faster. **As a bonus**, it also demonstrates the verbose=True option, which enables helpful output during compilation, ideal for debugging or understanding what's happening under the hood.

### Fine-Grained Performance Control ### 

While `CyCompile's` cycompile works out-of-the-box with zero configuration, it also gives you the ability to fine-tune how your functions are compiled. Whether you're aiming for safer defaults, maximum speed, or somewhere in between — you have options.

The core options you can customize:

- opt: Choose from predefined optimization levels like "safe", "fast", or "custom".
- compiler_directives: Pass any [Cython compiler directives](https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives)   to influence how code is translated.
- extra_compile_args: Add custom flags passed directly to the C++ compiler for deeper tuning.
  - [Here](https://caiorss.github.io/C-Cpp-Notes/compiler-flags-options.html) is a list of Unix based flags.
  - [Here](https://learn.microsoft.com/en-us/cpp/build/reference/compiler-options-listed-by-category?view=msvc-170) is a list of Windows based flags.

**Note:** The "fast" optimization option may not always provide the best results. It applies the most aggressive optimizations, but depending on the use case, this can lead to excessive overhead or be inappropriate for certain functions. Additionally, aggressive optimization may result in a loss of accuracy for applications requiring precision. For best results, consider using the 'custom' option with your own specified parameters.

Below are a few curated examples illustrating how to use these options effectively:

By default, no arguments are needed, the "safe" option will be applied. In this mode, no additional optimizations are used when compiling the binary:
```python
@cycompile()
def sum_of_squares_safe(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result
```

You can opt into more aggressive optimizations for more potential speed, at the potential cost of runtime safety (e.g. bounds checks):
```python
# Function decorated with cycompile (fast optimization)
@cycompile(opt="fast")
def sum_of_squares_fast(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result
```

You can selectively override any directive, for example, enabling bounds checking even in fast mode:
```python
# Function decorated with cycompile (overridden compiler directive)
@cycompile(
    opt="fast",
    compiler_directives={'boundscheck': True}
)
def sum_of_squares_override_directive(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result
```

Need full control of the underlying compilation? You can pass your own compile flags:
```python
# Function decorated with cycompile (overridden compiler flags)
@cycompile(
    opt="fast",
    extra_compile_args=["-fno-fast-math"]
)
def sum_of_squares_override_flags(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result
```
For complete customization, You can fully control both directives and compiler flags:
```python
# Function decorated with cycompile (custom settings)
@cycompile(
    opt="custom",
    compiler_directives={
        'language_level': 3,
        'boundscheck': False,
        'wraparound': False,
    },
    extra_compile_args=["-O3", "-mtune=native"]
)
def sum_of_squares_custom(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result
```
**Important**: When using the custom option, language_level is not automatically set. If omitted, Cython will default to Python 2 syntax and semantics. To ensure compatibility with modern Python code, it's highly recommended to explicitly include 'language_level': 3 in your custom directives as seen in the example above.

### Using Recursive Functions ### 
Many decorators, like `Cython's` cython.compile(), struggle with recursive functions, but `CyCompile's` cycompile excels at optimizing them, making it ideal for optimizing recursive logic. The following example demonstrates how you can use cycompile with a simple recursive function:
```python
from cycompile import cycompile

@cycompile()
def fib_recursive(n: int) -> int:
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)

fib_recursive(30)
```
In this case, cycompile compiles fib_recursive into a C-based binary. As a result, subsequent calls to the function will run with C-level speed. Additionally, this example illustrates how cycompile works seamlessly with static typing, ensuring compatibility without sacrificing performance. The next example demonstrates the usage of cycompile with mutually recursive functions, another scenario where cycompile shines:
```python
from cycompile import cycompile

# Determines if a number is even using mutual recursion
@cycompile()
def is_even(n):
    if n == 0:
        return True
    else:
        return is_odd(n - 1)

# Determines if a number is odd using mutual recursion
@cycompile()
def is_odd(n):
    if n == 0:
        return False
    else:
        return is_even(n - 1)

number = 5
print(f"Is {number} even? {is_even(number)}")
print(f"Is {number} odd? {is_odd(number)}")
```

### Using Classes and Objects ###
While full class and method decoration is not yet supported by the `CyCompile's` cycompile decorator, creating objects and passing them into compiled functions works seamlessly, as shown below:
```python
from cycompile import cycompile

@cycompile()
def object_integration_function(obj):
    obj.instance_method()
    print("[cycompile] Called method from passed object.")

@cycompile()
def object_creation_function():
    obj = MyClass()
    obj.instance_method()
    print("[cycompile] Created object and called its method.")

class MyClass:
    def instance_method(self):
        print("[regular] This is an instance method.")
```
These examples demonstrate that cycompile supports object-oriented programming workflows by allowing both the creation and usage of class instances within compiled functions, even if the classes themselves cannot be compiled using the decorator. Full class support is curently under development and hopefully will be available soon!

### Advanced Cases ###
`CyCompile` shines in optimizing performance-intensive sections of Python code, especially when dealing with custom operations or low-level tasks that can benefit from the power of C-level optimizations. Below are some examples showcasing how `CyCompile` integrates seamlessly into machine learning, numerical algorithms, and custom algorithm implementations.

**Machine Learning & Deep Learning (TensorFlow, Keras)**

While TensorFlow and Keras are already highly optimized for performance, there are still areas such as custom operations, data preprocessing, or post-processing steps which can benefit from `CyCompile's` cycompile. For example, the following example shows how cycompile integrates seamlessly into a training pipeline. Although cycompile may not significantly speed up the actual model training (since TensorFlow already handles that efficiently), it can optimize areas like data preparation or custom loss functions:

```python
@cycompile(opt="fast", verbose=True)
def train_and_evaluate_cycompile():
    # Your TensorFlow model training and evaluation code
    # Works seamlessly with cycompile
```
The key takeaway here is that cycompile can enhance other parts of the pipeline that TensorFlow might not optimize, like custom data transformations or post-processing steps.

**Numerical Algorithms**

`CyCompile's` cycompile provides an easy way to optimize common numerical operations that may not be optimized by existing libraries like NumPy. Below are a few examples from benchmark tests comparing `CyCompile` with Cython and pure Python implementations:
- Elementwise Square Operation: In the case of a simple elementwise operation like squaring the elements of an array, cycompile outperforms cython.compile and pure Python, showing its ability to optimize typical numeric operations:
  ```python
  @cycompile(opt="fast")
  def elementwise_square_optimized(arr):
      return np.array([x**2 for x in arr])
  ```
- Matrix Multiplication: For matrix multiplication using NumPy's np.dot(), which is already optimized in C, the performance improvement with cycompile is marginal. However, for custom operations or non-NumPy tasks, `CyCompile` provides noticeable performance benefits:
  ```python
  @cycompile(opt="fast")
  def matrix_multiplication_optimized(A, B):
      return np.dot(A, B)
  ```
- Summing Array Elements: In cases like summing array elements in a loop, cycompile demonstrates significant performance improvements over pure Python code, even when compared to cython.compile:
  ```python
  @cycompile(opt="fast")
  def sum_elements_optimized(arr):
      total = 0.0
      for x in arr:
          total += x
      return total
  ```

**Custom Algorithms & Simulations**

`CyCompile's` cycompile is also highly effective for custom algorithms that require extensive iterative computations. For example, the Euler Method, a numerical technique that relies on repeated calculations, is an excellent example of where `CyCompile` excels. By optimizing these iterative steps, `CyCompile` significantly reduces execution time, especially in simulation-based or complex calculation tasks:

```python
@cycompile(opt="fast")
def euler_method_optimized(f, y0, t0, t_end, dt):
    t = np.arange(t0, t_end, dt)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        y[i] = y[i-1] + dt * f(t[i-1], y[i-1])
    return y
```
This performance boost is especially useful in scenarios requiring large numbers of iterations or updates, such as in simulations or complex calculations.

By integrating `CyCompile` into your existing workflows, whether for machine learning, numerical algorithms, or custom algorithms, you can fine-tune specific code segments that aren't already optimized by libraries like TensorFlow or NumPy. This allows you to harness the power of C-level optimizations for areas of your code that are computationally expensive but still need custom handling.

For more detailed examples and performance benchmarks, see the full [Medium article](https://medium.com/@ranuja.pinnaduwage/cycompile-practical-use-cases-for-function-level-optimization-68eb6300b225).

## Conclusion
I am very proud of this project and its goal. I hope to bridge the performance gap between Python and C while still allowing users to write their Python code as normal. This project has several strengths, specifically in allowing users to control exactly which portions of their code get compiled and what parameters are used during compilation. This flexibility is huge, as it lets users design their code however they like without worrying that the entire call stack involved in a tagged function will be affected by its compilation rules.

As I mentioned a few times in the README, there are a few areas that need improvement, and I aim to address them in the future. Currently, classes are not fully supported and therefore cannot be directly converted using this project, though user-defined classes can still be used in tagged functions. Additionally, I have yet to test this package with asynchronous functions commonly used in network programming. If I had to guess, they might present some challenges, as transitioning from Python async functions to C doesn't seem like the smoothest process.

With future releases and feedback from the community, I'm excited to continue improving the package and addressing any issues that arise. Thanks for reading!  
