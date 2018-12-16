import numpy as np

CHAR_TO_INT = {'.': 0, 'E': 1, 'G': 2, '#': 3}
INT_TO_CHAR = {val: key for key, val in CHAR_TO_INT.items()}
OFFSETS = np.array([[-1, 0], [0, -1], [0, 1], [1, 0]])


class Battle:
    def __init__(self, grid, elf_power=3, debug=False):
        self.debug = debug
        self.round = 0
        self.grid = np.copy(grid)
        elf_inds = np.where(grid == CHAR_TO_INT['E'])
        self.elf_list = [Elf(position, self, elf_power) for position in zip(*elf_inds)]
        goblin_inds = np.where(grid == CHAR_TO_INT['G'])
        self.goblin_list = [Goblin(position, self) for position in zip(*goblin_inds)]

        self.elf_deaths = 0

    def __repr__(self):
        str = 'Round %d\n' % self.round
        creature_list = sort_creatures(self.elf_list + self.goblin_list)
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
        if self.debug:
            print(self)
        creature_list = sort_creatures(self.elf_list + self.goblin_list)
        for ind, creature in enumerate(creature_list):
            if creature.hit_points <= 0:
                continue
            next_position = creature.get_next_move()
            if next_position:
                creature.move(next_position)
            target = creature.get_attack_target()
            if target:
                creature.attack(target)
            if self.done:
                break
        if ind == len(creature_list) - 1:
            self.round += 1

    @property
    def done(self):
        return not self.elf_list or not self.goblin_list

    @property
    def outcome(self):
        total_hit_points = np.sum([creature.hit_points for creature in
                                   self.elf_list + self.goblin_list])
        return self.round * total_hit_points


def sort_creatures(creatures):
    positions = np.array([creat.position for creat in creatures])
    return [creatures[ind] for ind in position_argsort(positions)]


def position_argsort(positions):
    sort_vals = positions[:, 0] * np.max(positions) + positions[:, 1]
    return np.argsort(sort_vals)

def position_argmin(positions):
    # positions = np.array(positions)
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
        cells = get_adjacent_cells(self.battle.grid, self.position, target_value)
        if not cells:
            return None
        attack_candidates = []
        for target in targets:
            if target.position in cells and target.hit_points > 0:
                attack_candidates += [target]
        if not attack_candidates:
            return None
        attack_candidates = sort_creatures(attack_candidates)
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
        distances = []
        closest_cells = ()
        for cell in adjacent_cells:
            reachable_cells, distance = self.plan_path(cell, destination_cells)
            distances += [distance]
            if not reachable_cells:
                closest_cells += (None,)
                continue
            reachable_cells = list(reachable_cells)
            first_cell_ind = position_argmin(np.array(reachable_cells))
            closest_cells += (reachable_cells[first_cell_ind],)
        min_dist = np.min(distances)
        if np.isinf(min_dist):
            return None

        candidates = zip(adjacent_cells, closest_cells, distances)
        candidates = filter(lambda tup: tup[-1] == min_dist, candidates)
        adjacent_cells, closest_cells, _ = zip(*candidates)
        ind = position_argmin(np.stack(closest_cells))
        return tuple(adjacent_cells[ind])

    def plan_path(self, position, destination_cells):
        distance = 0
        if position in destination_cells:
            return {position}, distance
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


def p15a(grid, debug=False):
    battle = Battle(grid, debug=debug)
    while not battle.done:
        battle.execute_round()
    print(battle)
    print('Outcome:', battle.outcome)
    return battle.outcome


def p15b(grid, debug=False):
    elf_power = 4
    while elf_power < 200:
        battle = Battle(grid, elf_power, debug)
        while not battle.done:
            battle.execute_round()
            if battle.elf_deaths:
                break
        if not battle.elf_deaths:
            break
        elf_power += 1

    if debug:
        battle = Battle(grid, elf_power, debug=debug)
        while not battle.done:
            battle.execute_round()
        print(battle)
        print("Elf power was", elf_power)
    return battle.outcome


def parse_p15_input(fname):
    grid = []
    with open(fname) as fileobj:
        for line in fileobj:
            row = [CHAR_TO_INT[char] for char in line.strip()]
            grid += [row]
    grid = np.array(grid)
    return grid


if __name__ == '__main__':
    part1_answers = [27730, 36334, 39514, 27755, 28944, 18740]
    for test_number, answer in zip(range(6), part1_answers):
        test_grid = parse_p15_input("p15_test_%d.txt" % test_number)
        assert p15a(test_grid) == answer
    p15_input = parse_p15_input("p15_input.txt")
    print("p15a:", p15a(p15_input))

    part2_answers = [4988, 31284, 3478, 6474, 1140]
    for test_number, answer in zip([0, 2, 3, 4, 5], part2_answers):
        test_grid = parse_p15_input("p15_test_%d.txt" % test_number)
        if p15b(test_grid) != answer:
            outcome = p15b(test_grid, debug=True)
            import pdb; pdb.set_trace()
            outcome = p15b(test_grid, debug=True)
    print("p15b:", p15b(p15_input))
