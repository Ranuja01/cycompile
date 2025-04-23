from cythonize_decorator import cycompile

@cycompile()
def simple_function():    
    print("This is a simple function.")

@cycompile()
def object_integration_function(obj):
    # obj = MyClass()
    obj.instance_method_2()
    print("This is a simple function too.")

class MyClass:
    @classmethod
    @cycompile()
    def class_method(cls):
        print("This is a class method.")
    @cycompile()
    def instance_method(self):
        print("This is an instance method.")
        
    def instance_method_2(self):
        print("This is an instance method too.")

@cycompile()
def outer_function():    
    def inner_function():
        print("This is a nested function.")
    inner_function()

# Test cases
try:
    simple_function()  # Works fine
except Exception as e:
    print(f"Error in simple_function: {e}")
    
try:
    obj = MyClass()
    object_integration_function(obj)  # Works fine
except Exception as e:
    print(f"Error in simple_function: {e}")

try:
    MyClass.class_method()  # Raises error
except Exception as e:
    print(f"Error in MyClass.class_method: {e}")

try:
    obj = MyClass()
    obj.instance_method()  # Raises error
except Exception as e:
    print(f"Error in obj.instance_method: {e}")

try:
    outer_function()  # Works fine
except Exception as e:
    print(f"Error in outer_function: {e}")
