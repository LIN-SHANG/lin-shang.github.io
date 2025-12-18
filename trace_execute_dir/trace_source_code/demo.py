# demo.py
import torch

def main():
    x = torch.tensor([1.0, 2.0, 3.0])
    y = x * 2
    z = y.sum()
    print("Result:", z)

main()