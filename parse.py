import argparse

class ParseWrapper:
    valid: dict[str, tuple[int, int]] = {
        'd': (1, 5),
        'C': (1, 8),
        'c': (5, 25),
        'w': (0, 50),
        'r': (1, 10),
        'e': (10, 1000)
    }
    valid_long: dict[str, tuple[int, int]] = {
        'grid_dimensions': (1, 5),
        'max_crate_count': (1, 8),
        'crate_density': (5, 50),
        'wall_density': (0, 50),
        'repetitions': (1, 10),
        'episodes': (10, 1000)
    }

    def __init__(self, parser: argparse.ArgumentParser) -> None:

        parser.add_argument('-d', '--grid_dimensions', type=int, default=5,
                            help=("dimensions of the environment " +
                            f"[{self.valid['d'][0]}-{self.valid['d'][1]}] "))
        parser.add_argument('-C', '--max_crate_count', type=int, default=8,
                            help=("largest number of crates on the board the agent should try to solve " +
                            f"[{self.valid['C'][0]}-{self.valid['C'][1]}]"))
        parser.add_argument('-c', '--crate_density', type=int, default=45,
                            help=("determines the percentage of crates on the board " +
                            f"[{self.valid['c'][0]}-{self.valid['c'][1]}]" +
                            "!! only relevant for human player !!"))
        parser.add_argument('-w', '--wall_density', type=int, default=18,
                            help=("determines the amount of walls on the board " +
                            f"[{self.valid['w'][0]}-{self.valid['w'][1]}]"))
        parser.add_argument('-r', '--repetitions', type=int, default=10,
                            help=("number of repetitions the agent should play for each crate count " +
                            f"[{self.valid['r'][0]}-{self.valid['r'][1]}]"))
        parser.add_argument('-e', '--episodes', type=int, default=100,
                            help=("number of episodes one repetition should consist of " +
                            f"[{self.valid['e'][0]}-{self.valid['e'][1]}]"))
        parser.add_argument('-a', '--agent', action='store_true', default=False,
                            help=f"flag to set agent to RL agent")
        parser.add_argument('-f', '--fast', action='store_true', default=False,
                            help=f"flag to turn off rendering for speed boost")

        self.args = parser.parse_args()
        self.argdict = vars(self.args)
        self.check_validity()

    def __call__(self) -> tuple[int, int, int, int, int, int, bool]:
        print('\nExperiment will be ran with the following parameters:')
        for arg, value in self.argdict.items():
            print(f'{arg:>15}|{value}')
        return tuple(self.argdict.values())

    def check_validity(self) -> None:
        for arg, value in self.argdict.items():
            if value is None: continue
            if type(value) == bool: continue
            if value < self.valid_long[arg][0] or value > self.valid_long[arg][1]:
                raise ValueError(f'Invalid value for argument "{arg}": {value}\n' +
                                 f"Please choose between {self.valid_long[arg][0]} and {self.valid_long[arg][1]}")
        