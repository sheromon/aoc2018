import numpy as np
import matplotlib.pyplot as plt

CHAR_TO_INT = {'.': 0, 'E': 1, 'G': 2, '#': 3}


class CharacterList:
    def __init__(self):
        self.chars = []

    def append(self, new_chars):
        self.chars += new_chars

    def sort(self):
        positions = np.array([char.position for char in self.chars])
        sort_vals = positions[:, 0] * np.max(positions) + positions[:, 1]
        self.chars = [self.chars[ind] for ind in np.argsort(sort_vals)]

    def __getitem__(self, item):
        return self.chars[item]

    def __iter__(self):
        return iter(self.chars)

    # def __next__(self):
    #     if self.start >= len(self.end):
    #         raise StopIteration
    #     else:
    #         self.start += 1
    #         return self.end[self.start-1]


class Character:
    def __init__(self, position, grid):
        self.hit_points = 200
        self.power = 3
        assert len(position) == 2
        assert isinstance(position, tuple)
        self.position = position

        self.grid = grid
        # used to calculate cells in range
        self.offsets = np.array([[0, 1], [1, 0], [0, -1], [-1, 0]])

    def __repr__(self):
        return str(self.__dict__)

    def move(self, new_pos):
        self.grid[new_pos] = self.grid[self.position]
        self.grid[self.position] = 0
        self.position = new_pos

    def cells_in_range(self):
        return [coord for coord in self.position + self.offsets
                if self.grid[coord[0], coord[1]] == 0]


class Goblin(Character):
    pass


class Elf(Character):
    pass


def p15a(grid):
    char_list = CharacterList()
    elf_inds = np.where(grid == CHAR_TO_INT['E'])
    char_list.append([Elf(position, grid) for position in zip(*elf_inds)])
    gob_inds = np.where(grid == CHAR_TO_INT['G'])
    char_list.append([Goblin(position, grid) for position in zip(*gob_inds)])
    char_list.sort()
    for char in char_list:
        cells = char.cells_in_range()
        import pdb; pdb.set_trace()


def parse_p15_input(fname):
    grid = []
    with open(fname) as fileobj:
        for line in fileobj:
            row = [CHAR_TO_INT[char] for char in line.strip()]
            grid += [row]
    grid = np.array(grid)
    return grid


if __name__ == '__main__':
    test_grid = parse_p15_input("p15_test_input.txt")
    assert p15a(test_grid) == 27730
    # p15_input = parse_p15_input("p15_input.txt")
    # print("p15a:", p15a(p15_input))
    # assert p15b(test_input) == 4
    # print("p15b:", p15b(p15_input))