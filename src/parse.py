import argparse
from typing import TypeAlias, Union

num: TypeAlias = Union[int, float]

class ParseWrapper:
    valid: dict[str, tuple[num, num]] = {
        'd': (3, 10),
        'b': (1, 9),
        'C': (1, 5),
        'c': (5, 50),
        'w': (0, 50),
        'r': (1, 100),
        'e': (10, 1000),
        'A': (0.5, 2.0),
        'E': (0.01, 0.25),
        'G': (0.9, 1.0),
        'N': (1, 10)
    }
    valid_long: dict[str, tuple[num, num]] = {
        'grid_dimensions': (3, 10),
        'bomb_range': (1, 9),
        'max_crate_count': (1, 5),
        'crate_density': (5, 50),
        'wall_density': (0, 50),
        'repetitions': (1, 100),
        'episodes': (10, 1000),
        'alpha': (0.5, 2.0),
        'epsilon': (0.01, 0.25),
        'gamma': (0.9, 1.0),
        'n_planning_updates': (1, 10)
    }

    def __init__(self, parser: argparse.ArgumentParser) -> None:

        parser.add_argument('-d', '--grid_dimensions', type=int, default=5,
                            help=("dimensions of the environment " +
                            f"[{self.valid['d'][0]}-{self.valid['d'][1]}] "))
        parser.add_argument('-b', '--bomb_range', type=int, default=1,
                            help=("explosion range for bombs " +
                            f"[{self.valid['b'][0]}-{self.valid['b'][1]}] "))
        parser.add_argument('-C', '--max_crate_count', type=int, default=5,
                            help=("largest number of crates on the board the agent should try to solve " +
                            f"[{self.valid['C'][0]}-{self.valid['C'][1]}]"))
        parser.add_argument('-c', '--crate_density', type=int, default=45,
                            help=("determines the percentage of crates on the board " +
                            f"[{self.valid['c'][0]}-{self.valid['c'][1]}]" +
                            " !! only relevant for human player !!"))
        parser.add_argument('-w', '--wall_density', type=int, default=18,
                            help=("determines the amount of walls on the board " +
                            f"[{self.valid['w'][0]}-{self.valid['w'][1]}]"))
        parser.add_argument('-r', '--repetitions', type=int, default=10,
                            help=("number of repetitions the agent should play for each crate count " +
                            f"[{self.valid['r'][0]}-{self.valid['r'][1]}]"))
        parser.add_argument('-e', '--episodes', type=int, default=100,
                            help=("number of episodes one repetition should consist of " +
                            f"[{self.valid['e'][0]}-{self.valid['e'][1]}]"))
        parser.add_argument('-A', '--alpha', type=float, default=1.0,
                            help=("learning rate " +
                            f"[{self.valid['A'][0]}-{self.valid['A'][1]}]"))
        parser.add_argument('-G', '--gamma', type=float, default=0.99,
                            help=("discount rate " +
                            f"[{self.valid['G'][0]}-{self.valid['G'][1]}]"))
        parser.add_argument('-E', '--epsilon', type=float, default=0.05,
                            help=("learning rate " +
                            f"[{self.valid['E'][0]}-{self.valid['E'][1]}]"))
        parser.add_argument('-N', '--n_planning_updates', type=int, default=5,
                            help=("number of planning updates " +
                            f"[{self.valid['E'][0]}-{self.valid['E'][1]}]"))
        parser.add_argument('-o', '--output', type=str, default='placeholder',
                            help=f"name of output plot file (don't put .png)")

        self.args = parser.parse_args()
        self.argdict = vars(self.args)
        self.check_validity()

    def __call__(self) -> tuple[int, int, int, int, int, int, float, float, float, int, str]:
        print('\nExperiment will be ran with the following parameters:')
        for arg, value in self.argdict.items():
            print(f'{arg:>20}|{value}')
        return tuple(self.argdict.values())

    def check_validity(self) -> None:
        for arg, value in self.argdict.items():
            if value is None: continue
            if type(value) == str: continue
            if value < self.valid_long[arg][0] or value > self.valid_long[arg][1]:
                raise ValueError(f'Invalid value for argument "{arg}": {value}\n' +
                                 f"Please choose between {self.valid_long[arg][0]} and {self.valid_long[arg][1]}")
