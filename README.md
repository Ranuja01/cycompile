# cycompile
A Python package for optimizing function performance via a Cython decorator.

## About This Project

`cycompile` is a decorator-based tool for Python developers who want native performance without sacrificing the simplicity and flexibility of pure Python. Built on top of **Cython**, it compiles individual Python functions into binary modules with a one-time performance cost, then seamlessly reuses them via intelligent caching for future calls.

This project was born out of a desire to **democratize performance optimization**. Too often, speeding up Python code means diving into Cython-specific syntax, manually restructuring your logic, or switching to a different language altogether. `cycompile` aims to change that by making it as easy as adding a decorator.

Unlike `cython.compile()`, which is great for scripts and modules, `cycompile` is built for **function-level optimization**, ideal for notebooks, prototyping, and **well-suited for production environments**. It allows for **selective performance boosts** without the need to alter your whole codebase.

At its core, this project is about **lowering the barrier** between Python’s elegance and C-level speed, empowering more developers to harness performance when they need it, without becoming compiler experts.

Where it stands out:

- **Handles recursive functions** &mdash; a common limitation in traditional function-level compilation tools.
- **Supports user-defined objects** and custom logic more gracefully than many static compilers.
- **Offers fine-grained control** over Cython directives and compiler flags for advanced users.
- **Manages and clears its own binary cache** &mdash; giving developers transparency and control.
- **Understands standard Python type hints** &mdash; avoiding the need for Cython-specific rewrites.
- **Non-invasive design** &mdash; requires no changes to your existing project structure or imports, just add a decorator.
- **Intelligent caching based on source** &mdash; minimizes unnecessary recompilation, with manual cache clearing available to avoid stale binaries.

**Note:** This project includes C++ components and requires the ability to compile both C++ and Python code. While the required Python components are automatically included during installation, you must ensure you have a C++ compiler installed to build the necessary C++ files. Please refer to the build requirements below for more information.

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
- **Note** Simply installing MSVC build tools may not properly configure your system. You may need to set environment variables or update your system’s PATH to include cl.exe.
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
To use the module, simply import facelock as seen below. Keep in mind that the first usage should generally take a few more seconds as the required models are being stored:
```python
import facelock
```
*Note:* This package requires access to a webcam to function properly. Currently, it returns a simple boolean indicating whether the face detected by the webcam matches a stored reference image. The facial recognition process takes approximately 2.5 seconds (slightly longer on first use) to complete. Below is an example demonstrating how to use the package:
```python
import facelock

img_path = "path_to_image.jpg"
is_match = facelock.get_authentication(img_path)

if is_match:
    print("User verified!")
else:
    print("Unauthorized user!")      
```
