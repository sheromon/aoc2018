import numpy as np

CHAR_TO_INT = {'.': 0, 'E': 1, 'G': 2, '#': 3}
INT_TO_CHAR = {val: key for key, val in CHAR_TO_INT.items()}
OFFSETS = np.array([[-1, 0], [0, -1], [0, 1], [1, 0]])


class Battle:
    def __init__(self, grid, elf_power=3):
        self.round = 0
        self.grid = grid
        elf_inds = np.where(grid == CHAR_TO_INT['E'])
        self.elf_list = [Elf(position, self, elf_power) for position in zip(*elf_inds)]
        goblin_inds = np.where(grid == CHAR_TO_INT['G'])
        self.goblin_list = [Goblin(position, self) for position in zip(*goblin_inds)]
        self.elf_deaths = 0

    def __repr__(self):
        str = 'Round %d\n' % self.round
        creature_list = self.sort_creatures()
        creats_seen = 0
        for row in self.grid:
            str += ''.join([INT_TO_CHAR[val] for val in row]) + '   '
            num_creats = np.sum((row == CHAR_TO_INT['E']) |
                               (row == CHAR_TO_INT['G']))
            if num_creats:
                creats = creature_list[creats_seen:creats_seen + num_creats]
                str += ', '.join([creat.__repr__() for creat in creats])
            creats_seen += num_creats
            str += '\n'
        return str

    def execute_round(self):
        creature_list = self.sort_creatures()
        for creature in creature_list:
            if creature.hit_points <= 0:
                continue
            if self.done:
                return
            next_position = creature.get_next_move()
            if next_position:
                creature.move(next_position)
            target = creature.get_attack_target()
            if target:
                creature.attack(target)
        # if self.done:
        #     return
        self.round += 1

    @property
    def done(self):
        return not self.elf_list or not self.goblin_list

    @property
    def outcome(self):
        total_hit_points = np.sum([creature.hit_points for creature in
                                   self.sort_creatures()])
        return self.round * total_hit_points

    def sort_creatures(self):
        all_creatures = self.elf_list + self.goblin_list
        positions = np.array([creat.position for creat in all_creatures])
        return [all_creatures[ind] for ind in position_argsort(positions)]


def position_argsort(positions):
    sort_vals = positions[:, 0] * np.max(positions) + positions[:, 1]
    return np.argsort(sort_vals)

def position_argmin(positions):
    sort_vals = positions[:, 0] * np.max(positions) + positions[:, 1]
    return np.argmin(sort_vals)


class Creature:
    def __init__(self, position, battle, power=3):
        self.value = None
        self.hit_points = 200
        self.power = power
        assert len(position) == 2
        assert isinstance(position, tuple)
        self.position = position

        self.battle = battle

    def __repr__(self):
        return "%s(%d)" % (INT_TO_CHAR[self.value], self.hit_points)

    def get_attack_target(self):
        if isinstance(self, Elf):
            targets = self.battle.goblin_list
        else:
            targets = self.battle.elf_list
        target_value = targets[0].value
        target_cells = get_adjacent_cells(self.battle.grid, self.position, target_value)
        if not target_cells:
            return None
        attack_candidates = []
        for target in targets:
            if target.position in target_cells:
                attack_candidates += [target]
        if not attack_candidates:
            raise RuntimeError("Couldn't find target at position %s" % str(target_cells[0]))
        hit_points_list = [target.hit_points for target in attack_candidates]
        ind = np.argmin(hit_points_list)
        return attack_candidates[ind]

    def attack(self, target):
        target.hit_points -= self.power
        if target.hit_points <= 0:
            target.die()

    def move(self, new_pos):
        assert self.battle.grid[new_pos] == 0
        self.battle.grid[new_pos] = self.battle.grid[self.position]
        self.battle.grid[self.position] = 0
        self.position = new_pos

    def die(self):
        if isinstance(self, Elf):
            self.battle.elf_list.remove(self)
            self.battle.elf_deaths += 1
        else:
            self.battle.goblin_list.remove(self)
        self.battle.grid[self.position] = 0

    def get_next_move(self):
        if isinstance(self, Elf):
            targets = self.battle.goblin_list
        else:
            targets = self.battle.elf_list
        # check to see if we are already adjacent to a target
        target_value = targets[0].value
        target_cells = get_adjacent_cells(self.battle.grid, self.position, target_value)
        if target_cells:
            return None  # if we're adjacent, don't move
        # otherwise, find all cells adjacent to targets and plan a move
        in_range = set()
        for target in targets:
            new_cells = get_adjacent_cells(self.battle.grid, target.position)
            in_range |= set(new_cells)
        return self.step_and_plan(in_range)

    def step_and_plan(self, destination_cells):
        adjacent_cells = get_adjacent_cells(self.battle.grid, self.position)
        if not adjacent_cells:
            return None
        results = ()
        for cell in adjacent_cells:
            results += (self.plan_path(cell, destination_cells),)
        shortest_ind = np.argmin([distance for cells, distance in results])
        if np.isinf(results[shortest_ind][1]):
            return None
        else:
            return adjacent_cells[shortest_ind]

    def plan_path(self, position, destination_cells):
        distance = 0
        if position in destination_cells:
            return position, distance
        current_cells = {(position,)}
        visited_cells = set()
        while True:
            visited_cells |= current_cells
            distance += 1
            next_cells = set()  # new starting positions after taking a step
            all_reachable_cells = set()
            for position in current_cells:
                adjacent_cells = get_adjacent_cells(self.battle.grid, position)
                if not adjacent_cells:
                    continue
                reachable_cells = set(adjacent_cells) & destination_cells
                if reachable_cells:
                    all_reachable_cells |= reachable_cells
                next_cells |= set(adjacent_cells)
            next_cells -= visited_cells
            if all_reachable_cells:
                return all_reachable_cells, distance  # found a way to get there
            if not next_cells:
                return set(), np.inf  # no path to cell in range of target
            current_cells = next_cells


class Elf(Creature):
    def __init__(self, position, battle, power):
        super().__init__(position, battle, power)
        self.value = 1


class Goblin(Creature):
    def __init__(self, position, battle):
        super().__init__(position, battle)
        self.value = 2


def get_adjacent_cells(grid, position, occupancy=0):
    return [tuple(coord) for coord in position + OFFSETS
            if grid[coord[0], coord[1]] == occupancy]


def p15a(grid):
    battle = Battle(grid)
    while not battle.done:
        battle.execute_round()
    print(battle)
    print('Outcome:', battle.outcome)
    return outcome


def p15b(grid):
    min_elf_power = 4
    max_elf_power = 200
    elf_power = min_elf_power
    delta_power = np.inf
    best_outcome = None
    while delta_power:
        # print("Testing power", elf_power)
        battle = Battle(np.copy(grid), elf_power)
        while not battle.done:
            battle.execute_round()
            if battle.elf_deaths:
                break
        if battle.elf_deaths:
            new_elf_power = elf_power + int(0.5 * (max_elf_power - elf_power))
            min_elf_power = elf_power
        else:
            new_elf_power = min_elf_power + int(0.5 * (elf_power - min_elf_power))
            max_elf_power = elf_power
            best_outcome = battle.outcome
        delta_power = elf_power - new_elf_power
        elf_power = new_elf_power
        # print("Elf deaths:", battle.elf_deaths)
    print("Best outcome:", best_outcome)

    print("Elf power:", max_elf_power)
    battle = Battle(np.copy(grid), max_elf_power)
    while not battle.done:
        battle.execute_round()
    print(battle)
    return best_outcome


def parse_p15_input(fname):
    grid = []
    with open(fname) as fileobj:
        for line in fileobj:
            row = [CHAR_TO_INT[char] for char in line.strip()]
            grid += [row]
    grid = np.array(grid)
    return grid


if __name__ == '__main__':
    # for test_number, outcome in zip([1, 2, 3, 4, 6], [27730, 36334, 39514, 27755, 18740]):
    #     test_grid = parse_p15_input("p15_test_%d.txt" % test_number)
    #     assert p15a(test_grid) == outcome
    # p15_input = parse_p15_input("p15_input.txt")
    # print("p15a:", p15a(p15_input))

    for test_number, outcome in zip([1, 3, 4, 6], [4988, 31284, 3478, 1140]):
        test_grid = parse_p15_input("p15_test_%d.txt" % test_number)
        assert p15b(test_grid) == outcome
    # print("p15b:", p15b(p15_input))
