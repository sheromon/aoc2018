import parse
import numpy as np
import pdb


class Step:
    def __init__(self, letter):
        self.letter = letter
        self.prereqs = []
        self.next = []

    def __repr__(self):
        return str(self.__dict__)

    def add_prereq(self, prereq):
        self.prereqs += [prereq]

    def add_next(self, next_step):
        self.next += [next_step]


def p7a(pairs):
    steps = build_dependencies(pairs)
    candidates = sorted(find_first_steps(steps))
    seq = ''
    while candidates:
        next_step = None
        for letter in candidates:
            step = steps[letter]
            if set(step.prereqs) <= set(seq):
                next_step = step
                break
        if not next_step:
            pdb.set_trace()
        candidates.remove(next_step.letter)
        seq += next_step.letter
        candidates = set(candidates) | set(next_step.next)
        candidates = sorted(list(candidates))
    return seq


def p7b(pairs, test=False):
    if test:
        n_workers = 2
        time_delta = -64
    else:
        n_workers = 5
        time_delta = -4
    steps = build_dependencies(pairs)
    candidates = sorted(find_first_steps(steps))
    seq = ''

    def assign_task(time, task, all_workers):
        for worker in all_workers:
            if not worker['task']:
                worker['task'] = task
                worker['finish_time'] = time + ord(task.letter) + time_delta
                return True
        return False

    def finish_task(all_workers):
        all_finish_times = [worker['finish_time'] for worker in all_workers]
        first_ind = np.argmin(all_finish_times)
        new_time = all_finish_times[first_ind]
        completed_letter = all_workers[first_ind]['task'].letter
        all_workers[first_ind] = {'task': '', 'finish_time': np.inf}
        return new_time, completed_letter

    current_time = 0
    workers = [{'task': '', 'finish_time': np.inf} for _ in range(n_workers)]
    while candidates:
        for letter in candidates:
            step = steps[letter]
            if set(step.prereqs) <= set(seq):
                assign_task(current_time, step, workers)
        for worker in workers:
            if worker['task']:
                if worker['task'].letter in candidates:
                    candidates.remove(worker['task'].letter)
        current_time, letter = finish_task(workers)
        seq += letter
        # print('Time:', current_time, 'Seq:', seq)
        candidates = set(candidates) | set(steps[letter].next)
        candidates = sorted(list(candidates))
    return current_time


def build_dependencies(pairs):
    steps = dict()
    for pair in pairs:
        step = steps.get(pair['step'], Step(pair['step']))
        step.add_prereq(pair['prereq'])
        steps[pair['step']] = step

        prereq = steps.get(pair['prereq'], Step(pair['prereq']))
        prereq.add_next(pair['step'])
        steps[pair['prereq']] = prereq
    return steps


def find_first_steps(steps):
    return [step.letter for step in steps.values() if not step.prereqs]


def parse_p7_input(fname):
    parse_pattern = parse.compile(
        'Step {prereq:w} must be finished before step {step:w} can begin.')
    step_prereq_pairs = []
    with open(fname) as fileobj:
        for line in fileobj:
            result = parse_pattern.parse(line)
            step_prereq_pairs.append(result)
    return step_prereq_pairs


if __name__ == '__main__':
    test_input = parse_p7_input("p7_test_input.txt")
    assert p7a(test_input) == 'CABDFE'
    p7_input = parse_p7_input("p7_input.txt")
    print("p7a:", p7a(p7_input))
    assert p7b(test_input, test=True) == 15
    print("p7b:", p7b(p7_input))
