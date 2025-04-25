# @author: Ranuja Pinnaduwage
# File: tensorflow_compatability_demo.py
# Demonstrates compatability of cycompile package with the TensorFlow Library.
# Licensed under the Apache License, Version 2.0.

from tensorflow import keras
from cycompile import cycompile
import time


def time_function(func, *args):
    start_time = time.time()
    func(*args)
    end_time = time.time()
    return end_time - start_time

@cycompile(opt = "fast", verbose = True)
def train_and_evaluate_cycompile():
    """Loads MNIST, trains a simple neural network, and evaluates it."""
    
    # Load MNIST dataset
    mnist = keras.datasets.mnist
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    # Normalize the images to [0, 1] range
    x_train, x_test = x_train / 255.0, x_test / 255.0

    # Define the model
    model = keras.Sequential([
        keras.layers.Flatten(input_shape=(28, 28)),  # Flatten input images
        keras.layers.Dense(128, activation='relu'),  # Hidden layer
        keras.layers.Dense(10, activation='softmax') # Output layer
    ])

    # Compile the model
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    # Train the model
    model.fit(x_train, y_train, epochs=5, verbose=1)

    # Evaluate the model
    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    print(f'\nTest accuracy: {test_acc:.4f}')
    

def train_and_evaluate():
    """Loads MNIST, trains a simple neural network, and evaluates it."""
    
    # Load MNIST dataset
    mnist = keras.datasets.mnist
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    # Normalize the images to [0, 1] range
    x_train, x_test = x_train / 255.0, x_test / 255.0

    # Define the model
    model = keras.Sequential([
        keras.layers.Flatten(input_shape=(28, 28)),  # Flatten input images
        keras.layers.Dense(128, activation='relu'),  # Hidden layer
        keras.layers.Dense(10, activation='softmax') # Output layer
    ])

    # Compile the model
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    # Train the model
    model.fit(x_train, y_train, epochs=5, verbose=1)

    # Evaluate the model
    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    print(f'\nTest accuracy: {test_acc:.4f}')



print("[cycompile Timing]")
time_cc = time_function(train_and_evaluate_cycompile)
print(f"[cycompile] fib_loop: {time_cc:.6f} sec")

print("[Python Timing]")
time_python = time_function(train_and_evaluate)
print(f"[python] fib_loop: {time_python:.6f} sec —")