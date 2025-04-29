# @author: Ranuja Pinnaduwage
# File: method_and_classes_examples.py
# Example usage of the cycompile package, demonstrating its flexibility with object-oriented programming,
# including support for object creation and the ability to handle passed objects.
# Licensed under the Apache License, Version 2.0.


from cycompile import cycompile
import cython

# --- Functions using cycompile ---

@cycompile()
def simple_function():    
    print("[cycompile] This is a simple function.")

@cycompile()
def object_integration_function(obj):
    obj.instance_method_2()
    print("[cycompile] Called method from passed object.")

@cycompile()
def object_creation_function():
    obj = MyClass()
    obj.instance_method_2()
    print("[cycompile] Create object and call a method from it.")

class MyClass:
    @classmethod
    @cycompile()
    def class_method(cls):
        print("[cycompile] This is a class method.")

    @cycompile()
    def instance_method(self):
        print("[cycompile] This is an instance method.")
        
    def instance_method_2(self):
        print("[regular] This is an instance method too.")

@cycompile()
def outer_function():    
    def inner_function():
        print("[cycompile] This is a nested function.")
    inner_function()

# --------------------------
# Cython.compile Comparison
# --------------------------

@cython.compile
def simple_function_cython():    
    print("[cython] This is a simple function.")

@cython.compile
def object_integration_function_cython(obj):
    obj.instance_method_2()
    print("[cython] Called method from passed object.")

@cython.compile
def object_creation_function_cython():
    obj = MyClassCython()
    obj.instance_method_2()
    print("[cython] Create object and call a method from it.")

class MyClassCython:
    @classmethod
    @cython.compile
    def class_method(cls):
        print("[cython] This is a class method.")

    @cython.compile
    def instance_method(self):
        print("[cython] This is an instance method.")
        
    def instance_method_2(self):
        print("[regular] This is an instance method too.")

@cython.compile
def outer_function_cython():    
    def inner_function():
        print("[cython] This is a nested function.")
    inner_function()

# --- Tests ---
if __name__ == "__main__":
    print("Running cycompile test cases:\n")

    try:
        print("→ simple_function()")
        simple_function()
    except Exception as e:
        print(f"[ERROR] simple_function: {e}")

    try:
        print("\n→ object_integration_function(obj)")
        obj = MyClass()
        object_integration_function(obj)
    except Exception as e:
        print(f"[ERROR] object_integration_function: {e}")
        
    try:
        print("\n→ object_creation_function()")        
        object_creation_function()
    except Exception as e:
        print(f"[ERROR] object_creation_function: {e}")    

    try:
        print("\n→ MyClass.class_method()")
        MyClass.class_method()
    except Exception as e:
        print(f"[ERROR] class_method: {e}")

    try:
        print("\n→ obj.instance_method()")
        obj = MyClass()
        obj.instance_method()
    except Exception as e:
        print(f"[ERROR] instance_method: {e}")

    try:
        print("\n→ outer_function()")
        outer_function()
    except Exception as e:
        print(f"[ERROR] outer_function: {e}")

    # Cython compile comparison
    print("\n---------------------Running Cython compile test cases-----------------------------\n")

    try:
        print("→ simple_function_cython()")
        simple_function_cython()
    except Exception as e:
        print(f"[ERROR] simple_function_cython: {e}")

    try:
        print("\n→ object_integration_function_cython(obj)")
        c_obj = MyClassCython()
        object_integration_function_cython(c_obj)
    except Exception as e:
        print(f"[ERROR] object_integration_function_cython: {e}")

    try:
        print("\n→ object_creation_function_cython()")        
        object_creation_function_cython()
    except Exception as e:
        print(f"[ERROR] object_creation_function_cython: {e}")

    try:
        print("\n→ MyClassCython.class_method()")
        MyClassCython.class_method()
    except Exception as e:
        print(f"[ERROR] class_method_cython: {e}")

    try:
        print("\n→ obj.instance_method()")
        c_obj = MyClassCython()
        c_obj.instance_method()
    except Exception as e:
        print(f"[ERROR] instance_method_cython: {e}")

    try:
        print("\n→ outer_function_cython()")
        outer_function_cython()
    except Exception as e:
        print(f"[ERROR] outer_function_cython: {e}")
