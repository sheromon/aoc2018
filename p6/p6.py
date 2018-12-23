import numpy as np
from shapely.geometry import MultiPoint, Point


def get_cells(center, distance, grid_shape):
    seq = np.arange(distance + 1).reshape([-1, 1])
    deltas_pos = np.hstack((seq, seq[::-1]))
    deltas = np.vstack((deltas_pos, -deltas_pos, deltas_pos * [-1, 1],
                        deltas_pos * [1, -1]))
    cells = center + deltas
    ok_inds = np.all((cells < grid_shape) & (cells >= 0), axis=1)
    cells = cells[ok_inds]
    cells = np.unique(cells, axis=0)
    return cells, np.any(~ok_inds)


class Grid:
    def __init__(self, coords, point_ind, buffer):
        grid_shape = np.max(coords, axis=0) + 2 * buffer
        values = np.zeros(np.prod(grid_shape), dtype=np.uint16)
        inds = np.ravel_multi_index(coords.T, grid_shape)
        values[inds] = np.arange(coords.shape[0]) + 1
        self.grid = np.reshape(values, grid_shape)

        self.point = coords[point_ind]
        self.value = point_ind + 1
        self.coords = np.concatenate((coords[:point_ind],
                                      coords[point_ind + 1:]), axis=0)
        self.fill_area()

    def __repr__(self):
        return str(self.grid.T)

    def fill_area(self):
        for distance in range(1, self.grid.shape[0]):
            cells_to_check, hit_max = get_cells(self.point, distance, self.grid.shape)
            if hit_max:
                self.grid[:] = 0
                return
            any_belong = False
            for cell in cells_to_check:
                deltas = self.coords - cell
                other_distances = np.sum(np.abs(deltas), axis=1)
                this_cell_belongs = np.all(other_distances > distance)
                any_belong = any_belong or this_cell_belongs
                if this_cell_belongs:
                    self.grid[tuple(cell)] = self.value
            if not any_belong:
                break

    def count_area(self):
        return np.sum(self.grid == self.value)


def get_candidate_point_indices(coords):
    convex_hull = MultiPoint([coord for coord in coords]).convex_hull
    ok_inds = []
    for point_ind, point in enumerate(coords):
        shapely_point = Point(point)
        if shapely_point.within(convex_hull):
            ok_inds.append(point_ind)
    return ok_inds


def p6a(coords):
    # ensure there is at least a minimum border of empty cells
    # around the outermost points in case part of the area for
    # the largest region extends past
    buffer = np.max(np.max(coords, axis=0) - np.min(coords, axis=0)) // 2

    max_area = 0
    for point_ind in get_candidate_point_indices(coords):
        # subtract offset from raw coordinates to account for buffer
        offset = np.min(coords, axis=0) - buffer
        # make the grid and populate with center points
        grid = Grid(coords - offset, point_ind, buffer=buffer)
        area = grid.count_area()
        if area > max_area:
            max_area = area
    return max_area


def p6b(coords, max_distance):
    coords -= np.min(coords, axis=0)
    max_x, max_y = np.max(coords, axis=0)
    x, y = np.meshgrid(np.arange(max_x), np.arange(max_y))
    all_cells = np.stack((x, y), axis=-1).reshape([-1, 2, 1])
    cells_tiled = np.tile(all_cells, (1, 1, coords.shape[0]))
    n_cells = all_cells.shape[0]
    coords_tiled = np.tile(np.expand_dims(coords, -1), (1, 1, n_cells))
    deltas = cells_tiled - coords_tiled.T
    total_distances = np.sum(np.abs(deltas), axis=(1, 2))
    return np.sum(total_distances < max_distance)


def parse_p6_input(fname):
    output = np.loadtxt(fname, dtype=np.int32, delimiter=',')
    return output


if __name__ == '__main__':
    test_input = parse_p6_input("p6_test_input.txt")
    assert p6a(test_input) == 17
    p6_input = parse_p6_input("p6_input.txt")
    print("p6a:", p6a(p6_input))
    assert p6b(test_input, 32) == 16
    print("p6b:", p6b(p6_input, 10000))
