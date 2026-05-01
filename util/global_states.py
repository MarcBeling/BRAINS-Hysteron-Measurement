from typing import Union

class State:
    def __init__(self):
        self.EXPERIMENT_NAME: Union[str, None] = None

global_variables = State()  # shared instance imported everywhere