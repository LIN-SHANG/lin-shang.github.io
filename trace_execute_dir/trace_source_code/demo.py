# demo.py
import torch

def main():
    x = torch.tensor([1.0, 2.0, 3.0]) # @inspect x
    y = x * 2 # @inspect y
    z = y.sum() # @inspect z
    print("Result:", z)

main()