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
        for row in self.grid[-150:, :].T:
            string += ''.join(row)
            string += '\n'
        return string

    def print_region(self, x, y):
        string = ''
        x_start = max(x - 50, 0)
        y_start = max(y - 20, 0)
        for row in self.grid[x_start:x + 50, y_start:y + 20].T:
            string += ''.join(row)
            string += '\n'
        print(string)

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

    def flow(self):
        inds = np.where(self.grid == '+')
        x, y = inds[0][0], inds[1][0]
        self.fall(x, y)

    def fall(self, x, y):
        fall_inds = self.grid[x, y:] == '|'
        fall_ind = np.argmax(fall_inds) if np.any(fall_inds) \
            else len(fall_inds) - 1
        stop_inds = np.isin(self.grid[x, y:], ['#', '~'])
        stop_ind = np.argmax(stop_inds) if np.any(stop_inds) \
            else len(stop_inds) - 1
        end_ind = np.minimum(fall_ind, stop_ind)
        self.grid[x, y:y + end_ind] = '|'
        # if we find running water, this water will just join it,
        # so nothing else needs to happen
        if fall_ind <= stop_ind:
            return
        # if we find clay or still water, try to fill up the clay
        self.fill_up(x, y + end_ind - 1)

    def fill_up(self, x, y):
        wall_right = True
        wall_left = True
        while wall_right and wall_left:
            wall_right = self.fill_sideways(x, y, 1)
            wall_left = self.fill_sideways(x, y, -1)
            y -= 1
        if wall_right and not wall_left:
            self.fill_sideways(x, y + 1, 1, '|')
        if wall_left and not wall_right:
            self.fill_sideways(x, y + 1, -1, '|')

    def fill_sideways(self, x, y, direction, fill_char='~'):
        if direction == 1:
            start_ind = x
            end_ind = self.adjust_x(self.bounds['x'][1] - 1)
        else:
            start_ind = x
            end_ind = 0
        row = self.grid[start_ind:end_ind:direction, y]
        below = self.grid[start_ind:end_ind:direction, y + 1]
        wall_ind = np.argmax(row == '#')
        empty_inds = np.isin(below, ['.', '|'])
        empty_ind = np.argmax(empty_inds) if np.any(empty_inds) \
            else len(empty_inds) - 1
        if (wall_ind < empty_ind) and (row[wall_ind] == '#'):
            end_ind = start_ind + direction * wall_ind
            self.grid[start_ind:end_ind:direction, y] = fill_char
            return True
        pdb.set_trace()
        if below[empty_ind] == '.':
            end_ind = start_ind + direction * empty_ind
            self.grid[start_ind:end_ind:direction, y] = '|'
            next_x = x + direction * empty_ind
            self.fall(next_x, y)
        return False

    def sum(self):
        return np.sum(self.grid[:, self.bounds['y'][0]:] == '~') + \
               np.sum(self.grid[:, self.bounds['y'][0]:] == '|')



def p17a(veins, bounds):
    grid = Grid(veins, bounds)
    grid.flow()
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
