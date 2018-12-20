import parse
import pdb
import numpy as np


class Grid:
    def __init__(self, veins, bounds):
        self.veins = veins
        self.bounds = bounds
        self.grid = np.empty(0)
        self.set_up_grid()

    def __repr__(self):
        string = ''
        for row in self.grid[-120:, :200].T:
            string += ''.join(row)
            string += '\n'
        return string

    def set_up_grid(self):
        grid_size = (self.bounds['x'][1] - self.bounds['x'][0] + 4,
                     self.bounds['y'][1] + 1)
        grid = np.empty(grid_size, dtype=np.str)
        grid[:] = '.'
        spring_loc = (self.adjust_x(500), 0)
        grid[spring_loc] = '+'
        for vein in self.veins:
            x_start = self.adjust_x(vein['x'][0])
            x_stop = self.adjust_x(vein['x'][1])
            y_start = vein['y'][0]
            y_stop = vein['y'][1]
            grid[x_start:x_stop, y_start:y_stop] = '#'
        self.grid = grid

    def adjust_x(self, x):
        return x - self.bounds['x'][0] + 2

    def fill(self):
        inds = np.where(self.grid == '+')
        x, y = inds[0][0], inds[1][0]
        x, y = self.fall(x, y)
        self.fill_up(x, y)

    def fall(self, x, y):
        self.grid[x, y] = '|'
        while y < self.bounds['y'][1] - 1:
            y += 1
            this_char = self.grid[x, y]
            next_char = self.grid[x, y + 1]
            if (next_char == '#') or (this_char == '~'):
                return x, y
            self.grid[x, y] = '|'
        return x, y

    def fill_right(self, x, y):
        next_char = ''
        below_char = ''
        while (next_char != '#') and (below_char != '.') \
                and (below_char != '|') \
                and (x < self.adjust_x(self.bounds['x'][1])):
            self.grid[x, y] = '~'
            x += 1
            next_char = self.grid[x, y]
            below_char = self.grid[x, y + 1]
        if (below_char == '.') or (below_char == '|'):
            self.fill_up(*self.fall(x, y))
            return False
        return next_char == '#'

    def fill_left(self, x, y):
        next_char = ''
        below_char = ''
        while (next_char != '#') and (below_char != '.') \
                and (below_char != '|') and (x > 0):
            self.grid[x, y] = '~'
            x -= 1
            next_char = self.grid[x, y]
            below_char = self.grid[x, y + 1]
        if (below_char == '.') or (below_char == '|'):
            self.fill_up(*self.fall(x, y))
            return False
        return next_char == '#'

    def fill_up(self, x, y):
        if y == self.bounds['y'][1] - 1:
            return
        wall_right = True
        wall_left = True
        while wall_right and wall_left and (y > 0):
            wall_right = self.fill_right(x, y)
            wall_left = self.fill_left(x, y)
            y -= 1

    def sum(self):
        return np.sum(self.grid[:, self.bounds['y'][0]:] == '~') + \
               np.sum(self.grid[:, self.bounds['y'][0]:] == '|')



def p17a(veins, bounds):
    grid = Grid(veins, bounds)
    grid.fill()
    pdb.set_trace()
    return grid.sum()


def parse_p17_input(fname):
    pattern = parse.compile('{dim1:w}={val:d}, {dim2:w}={start:d}..{stop:d}')
    veins = []
    bounds = {'x': [np.inf, -np.inf], 'y': [np.inf, -np.inf]}
    with open(fname) as fileobj:
        for line in fileobj:
            result = pattern.parse(line.strip())
            veins += [{
                result['dim1']: (result['val'], result['val'] + 1),
                result['dim2']: (result['start'], result['stop'] + 1),
            }]
            for dim in ('x', 'y'):
                bounds[dim][0] = np.minimum(bounds[dim][0], veins[-1][dim][0])
                bounds[dim][1] = np.maximum(bounds[dim][1], veins[-1][dim][1])
    for dim in ('x', 'y'):
        bounds[dim] = [int(bound) for bound in bounds[dim]]
    return veins, bounds


if __name__ == '__main__':
    test_inputs = parse_p17_input("p17_test_input.txt")
    assert p17a(*test_inputs) == 57
    inputs = parse_p17_input("p17_input.txt")
    print(p17a(*inputs))
