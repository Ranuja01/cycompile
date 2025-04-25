# @author: Ranuja Pinnaduwage
# File: simple_demo.py
# Demonstrates basic usage of the package.
# Licensed under the Apache License, Version 2.0.

from cycompile import cycompile, clear_cache

@cycompile()
def simple_function():    
    print("[cycompile] This is a simple function.")
    
simple_function()  
clear_cache()