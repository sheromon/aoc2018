import numpy as np


class Node:
    def __init__(self, int_list):
        self.n_child = int_list.pop()
        self.n_meta = int_list.pop()
        self.children = []
        self.metadata = []
        for _ in range(self.n_child):
            self.children.append(Node(int_list))
        for _ in range(self.n_meta):
            self.metadata.append(int_list.pop())

    def sum_metadata(self):
        total = sum(self.metadata)
        for child in self.children:
            total += child.sum_metadata()
        return total

    def calculate_value(self):
        if not self.n_child:
            return sum(self.metadata)
        total = 0
        for child_ind in self.metadata:
            if 1 <= child_ind <= self.n_child:
                total += self.children[child_ind - 1].calculate_value()
        return total


def p8a(int_list):
    root_node = Node(int_list[::-1])
    return root_node.sum_metadata()


def p8b(int_list):
    root_node = Node(int_list[::-1])
    return root_node.calculate_value()


def parse_p8_input(fname):
    return np.loadtxt(fname, dtype=np.int16).tolist()


if __name__ == '__main__':
    test_input = parse_p8_input("p8_test_input.txt")
    assert p8a(test_input) == 138
    p8_input = parse_p8_input("p8_input.txt")
    print("p8a:", p8a(p8_input))
    assert p8b(test_input) == 66
    print("p8b:", p8b(p8_input))
