from experiments._experiment import Experiment
from equipment.RNPU import HardwareInterface

from util.setupmanager import SetupManager
from typing import List

import pygad


class AI_GENETIC(Experiment):
    """
    The goal of `AI_Genetic` is to operate a genetic algorithm for a fitness function for applications beyond the NIDAQs.
    It uses the genetic algorithm library `pygad` to find a suitable voltage configuration of the RNPU for hysteresis.
    The fittness function is defined through the `HardwareInterface` class in `equipment.RNPU`. 
    """

    def __init__(self) -> None:
        super().__init__()
        self.sm: SetupManager = SetupManager()
        self.hardware_interface = HardwareInterface()
        self.config = self.sm.get_config()

        # Initialize the genetic algorithm from values given in the experiments configuration file.
        self.ga_instance = pygad.GA(
            num_generations =    self.config['GA']['num_generations'],
            num_parents_mating = self.config['GA']['num_parents_mating'],
            fitness_func =       AI_GENETIC.fitness_func,
            sol_per_pop =        self.config['GA']['sol_per_pop'],
            num_genes  =         self.config['GA']['num_genes'],
            gene_space =         self.config['GA']['gene_space'],
            mutation_type =      self.config['GA']['mutation_type'],
            mutation_percent_genes = self.config['GA']['mutation_percent_genes'],
            mutation_num_genes= self.config['GA']['mutation_num_genes']
        )

    @staticmethod
    def fitness_func(ga_instance: pygad.GA, solution: List[float], solution_idx: int) -> float:
        """
        Function to calculate the fitness for a given solution.\n
        Because `pygad` requires a function with two parameters, `solution` and `solution_idx`,
        applying the solution on the RNPU and computing the fittness from the device's response had to be wrapped in a seperate class.
        See `HardwareInterface.apply_and_calc_fit` for more details 

        Args:
            solution (List[float]): Solution that should be applied onto the RNPU. A solution is the list of control voltages that are applied to the device.
            solution_idx (int): Describes which xth solution the genetic algorith is currently at.

        Returns:
            float: A value for the fitness for the applied solution.
        """        
        result = HardwareInterface().apply_and_calc_fit(solution, solution_idx)
        print(f"Solution {solution_idx} | Configuration {solution}\tFitness: {result}")
        return result # type: ignore
    

    @staticmethod
    def print_solution(best_solution: List[float], best_fitness: float, best_solution_idx: int) -> None:
        """
        Prints out a solution found by `pygad`.

        Args:
            best_solution (List[float]): The list of control voltages for the RNPU giving the best results.
            best_fitness (float): The greatest value of fitness that could be achieved. 
            best_solution_idx (int): Which xth solution gave the best fit.
        """        
        output_string = f" --- Final Solution ---\nBest configuration: {best_solution}\nBest fitness: {best_fitness}\nID Genome: {best_solution_idx}"
        print(output_string)

    def run(self) -> None:
        """
        Runs the genetic algorithm.
        """        
        self.ga_instance.run()
        best_solution, best_fitness, best_solution_idx = self.ga_instance.best_solution()[0]
        AI_GENETIC.print_solution(best_solution, best_fitness, best_solution_idx)

    def plot(self) -> None:
        pass

    def close(self):
        """
        Shutsdown all measurement equipment and turns all control voltages slowly to 0.
        """        
        self.hardware_interface.close()


