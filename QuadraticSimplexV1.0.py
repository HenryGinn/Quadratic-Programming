import numpy as np
import scipy as sc
import math
from copy import deepcopy
from Tableau import Tableau
from PlotState import PlotState

large_width = 400
np.set_printoptions(linewidth=large_width)

class QuadraticSimplex():

    """ Each object is an optimisation problem to maximise the objective
    function x^Tx subject to constraints Ax<=b. All variables must be
    positive and the origin must be a feasible point.

    For more details on the algorithm, implementation, and formulation
    of quadratic problems into this form see the README document. """

    option_plot_state = True

    def __init__(self, constraint_matrix, constraint_vector):
        self.constraint_matrix = constraint_matrix
        self.constraint_vector = constraint_vector
        self.set_dimensions()
        self.set_space_constraints()
        self.set_initial_tableaux()
        self.solved_status = "Unsolved"
        self.plot_obj = PlotState(self)
        
    def set_dimensions(self):
        self.space_dimensions = self.constraint_matrix.shape[1]
        self.slack_dimensions = self.constraint_matrix.shape[0]
        self.total_dimensions = self.space_dimensions + self.slack_dimensions

    def set_space_constraints(self):
        non_negativity_constraints = np.identity(self.space_dimensions)
        self.space_constraints = np.concatenate((non_negativity_constraints,
                                                 self.constraint_matrix),
                                                axis=0)

    def set_initial_tableaux(self):
        self.set_initial_profit_information()
        initial_tableau = Tableau(self, -1, self.profit_vector)
        self.tableaux = [self.create_tableau_dimension(initial_tableau, dimension)
                         for dimension in range(self.space_dimensions)]
        
    def set_initial_profit_information(self):
        profit_normal = np.ones(self.space_dimensions)
        self.set_profit_vector(profit_normal)
        self.profit = 0

    def set_profit_vector(self, normal):
        profit_vector_slack = np.zeros(self.slack_dimensions)
        self.profit_vector = np.concatenate((normal, profit_vector_slack), axis=0)

    def create_tableau_dimension(self, initial_tableau, dimension):
        tableau_dimension = deepcopy(initial_tableau)
        tableau_dimension.global_problem = self
        tableau_dimension.dimension = dimension
        tableau_dimension.pivot_column_index = dimension
        tableau_dimension.set_tableau_components()
        return tableau_dimension

    def solve(self):
        while self.solved_status == "Unsolved":
            self.iterate()
            self.output_tableaux()
            self.output_profit()
            self.plot_obj.plot()
            #input()
        print("Solved!")

    def iterate(self):
        self.set_lines_of_movement()
        self.merge_any_converged_pairs()
        self.set_updating_tableau()
        self.updating_tableau.pivot()
        self.update_global_problem()

    def set_lines_of_movement(self):
        for tableau in self.tableaux:
            tableau.set_line_of_movement()
            tableau

    def merge_any_converged_pairs(self):
        for tableau_index_1 in range(len(self.tableaux)):
            for tableau_index_2 in range(tableau_index_1 + 1, len(self.tableaux)):
                self.check_if_merged(tableau_index_1, tableau_index_2)

    def check_if_merged(self, tableau_index_1, tableau_index_2):
        tableau_1 = self.tableaux[tableau_index_1]
        tableau_2 = self.tableaux[tableau_index_2]
        if self.reference_vectors_match(tableau_1, tableau_2):
            if self.direction_vectors_match(tableau_1, tableau_2):
                print("Merging!")
                self.tableaux.pop(tableau_index_1)

    def reference_vectors_match(self, tableau_1, tableau_2):
        vector_1 = tableau_1.line_reference_vector
        vector_2 = tableau_2.line_reference_vector
        difference = abs(vector_1 - vector_2)
        vectors_match = (sum(difference) < 0.0001)
        return vectors_match

    def direction_vectors_match(self, tableau_1, tableau_2):
        vector_1 = tableau_1.line_direction_vector
        vector_2 = tableau_2.line_direction_vector
        cross_term = np.dot(vector_1, vector_2)*np.dot(vector_1, vector_2)
        abs_values = np.dot(vector_1, vector_1)*np.dot(vector_2, vector_2)
        vectors_match = (cross_term > abs_values*0.99999)
        return vectors_match

    def set_updating_tableau(self):
        potential_profit_list = [tableau.get_potential_profit()
                                 for tableau in self.tableaux]
        print(f"Potential profit list: {potential_profit_list}\n")
        updating_dimension = np.argmin(potential_profit_list)
        self.updating_tableau = self.tableaux[updating_dimension]

    def update_global_problem(self):
        old_profit = self.profit
        self.set_profit()
        if abs(old_profit - self.profit) > 0.0001:
            self.update_tableaux()
        else:
            self.update_updating_tableau()

    def set_profit(self):
        updating_tableau_vertex_position = self.updating_tableau.get_vertex_position()
        self.profit = math.sqrt(sum(updating_tableau_vertex_position**2))

    def update_tableaux(self):
        self.compute_partial_positions()
        self.compute_profit_vector()
        self.update_pivot_columns()

    def compute_partial_positions(self):
        for tableau in self.tableaux:
            if tableau != self.updating_tableau:
                tableau.find_hypersphere_intersection()
            else:
                tableau.partial_position = self.updating_tableau.get_vertex_position()

    def compute_profit_vector(self):
        positions = np.vstack([tableau.partial_position for tableau in self.tableaux])
        positions_transpose = np.transpose(positions)
        gram_matrix = np.matmul(positions, positions_transpose)
        intermediate_vector = sc.linalg.solve(gram_matrix, np.ones(len(self.tableaux)))
        profit_normal = np.dot(positions_transpose, intermediate_vector)
        self.set_profit_vector(profit_normal)

    def update_pivot_columns(self):
        for tableau in self.tableaux:
            tableau.set_pivot_column_index()

    def update_updating_tableau(self):
        self.updating_tableau.set_pivot_column_index()

    def output_problem_constraints(self):
        print("Problem constraints")
        print(self.constraint_matrix)
        print(self.constraint_vector)
        print("")

    def output_tableaux(self):
        for tableau in self.tableaux:
            print("#################### NEW DIMENSION ####################\n")
            tableau.output_all()

    def output_profit(self):
        print((f"Outputting global profit information\n"
               f"Profit: {round(self.profit, 3)}\n"
               f"Profit vector: {self.profit_vector}\n"))

    def output_partial_positions(self):
        print("Outputting partial positions")
        for tableau in self.tableaux:
            print(f"Dimension: {tableau.dimension}, position: {tableau.partial_position}")
        print("")

    def __str__(self):
        string = (f"Space dimensions: {self.space_dimensions}\n"
                  f"Slack dimensions: {self.slack_dimensions}\n"
                  f"Total dimensions: {self.total_dimensions}\n"
                  f"Solved status: {self.solved_status}/n")
        return string

"""
constraint_matrix = np.array([[3, 2],
                              [-12, 13],
                              [1, -3],
                              [6, 5]])
constraint_vector = np.array([55, 13, 2, 120])
"""
constraint_matrix = np.array([[-3, 1],
                              [3, 5],
                              [1, -3],
                              [9, 8]])
constraint_vector = np.array([3, 90, 2, 180])
"""
constraint_matrix = np.array([[-0.9, 1],
                              [1.1, -1],
                              [1, 1],
                              [1, 1.01]])
constraint_vector = np.array([5, 5, 20, 20.1])

constraint_matrix = np.array([[1, 0],
                              [0, 1]])
constraint_vector = np.array([1, 0])
"""

problem = QuadraticSimplex(constraint_matrix, constraint_vector)
problem.solve()
    
