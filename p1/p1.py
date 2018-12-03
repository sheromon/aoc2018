import numpy as np


def p1a(int_list):
    return np.sum(int_list)

def p1b(int_list):
    current_val = 0
    seen_vals = set()
    while True:
        for val in int_list:
            current_val += val
            if current_val in seen_vals:
                return current_val
            seen_vals.add(current_val)


def read_p1_input(fname):
    return np.loadtxt(fname, dtype=np.int32)


if __name__ == '__main__':
    int_list = read_p1_input("p1_input.txt")
    print("p1a:", p1a(int_list))
    print("p1b:", p1b(int_list))
