import numpy as np
import scipy as sc
import math
from copy import deepcopy
from Tableau import Tableau
from PlotState import PlotState
from PlotState3D import PlotState3D

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
        self.set_plot_state()
        
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
            self.output_partial_positions()
            self.output_profit()
            self.plot_obj.plot()
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
        updating_dimension = np.argmin(potential_profit_list)
        self.updating_tableau = self.tableaux[updating_dimension]

    def update_global_problem(self):
        old_profit = self.profit
        self.set_profit()
        if abs(old_profit - self.profit) > 0.0001:
            self.update_tableaux()
        self.updating_tableau.set_pivot_column_index()

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
        positions_transpose, gram_matrix = self.get_positions_transpose_and_gram_matrix()
        intermediate_vector = sc.linalg.solve(gram_matrix, np.ones(positions_transpose.shape[1]))
        profit_normal = np.dot(positions_transpose, intermediate_vector)
        self.set_profit_vector(profit_normal)

    def get_positions_transpose_and_gram_matrix(self):
        positions = self.get_positions_no_repeats()
        positions_transpose = np.transpose(positions)
        gram_matrix = np.matmul(positions, positions_transpose)
        return positions_transpose, gram_matrix

    def get_positions_no_repeats(self):
        positions = np.vstack([tableau.partial_position for tableau in self.tableaux])
        positions_rounded = np.round(positions, 6)
        positions_rounded, unique_indices = np.unique(positions_rounded, axis=0, return_index=True)
        positions = positions[unique_indices]
        return positions

    def update_pivot_columns(self):
        for tableau in self.tableaux:
            tableau.set_column_filtered_arrays()
            tableau.set_profit_row()
            #tableau.set_pivot_column_index()

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

    def set_plot_state(self):
        if self.space_dimensions == 3:
            self.plot_obj = PlotState3D(self)
        else:
            self.plot_obj = PlotState(self)

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

constraint_matrix = np.array([[-3, 1],
                              [3, 5],
                              [1, -3],
                              [9, 8]])
constraint_vector = np.array([3, 90, 2, 180])

constraint_matrix = np.array([[-0.9, 1],
                              [1.1, -1],
                              [1, 1],
                              [1, 1.01]])
constraint_vector = np.array([5, 5, 20, 20.1])

constraint_matrix = np.array([[-6, 1],
                              [1, 2],
                              [7, 4]])
constraint_vector = np.array([3, 20, 70])

constraint_matrix = np.array([[-1, 4],
                              [6, 5],
                              [7, 1],
                              [5, 2]])
constraint_vector = np.array([26, 76, 70, 53])

constraint_matrix = np.array([[-1, 0, 0],
                              [0, -1, 0],
                              [0, 0, -1],
                              [2, -1, 6],
                              [-2, 5, 1],
                              [4, 1, 1],
                              [0, 1, -1],
                              [2, 4, 1]])
constraint_vector = np.array([0, 0, 0, 4, 3, 3, 0.3, 3.4])
"""

N = 30
constraint_matrix = np.random.rand(N, 3)
constraint_matrix = constraint_matrix / np.linalg.norm(constraint_matrix, axis=1).reshape(N, 1)
print(constraint_matrix)
constraint_vector = np.random.rand(N)/3 + 0.7
print([list(i) for i in constraint_matrix])
print(list(constraint_vector))

#constraint_matrix = np.array([[2.926413872904681, 1.0847136814905383, 2.65372612696535], [1.010047566777689, 2.2462791285252677, 4.748971112601782], [4.798545379569625, 4.14918950180408, 1.3388303955334109], [3.082590600500611, 1.5090858187033056, 2.91709850939197], [3.272392402726407, 3.5066551643852395, 2.9176255867916283], [4.542156829387358, 3.556880418542365, 2.7985613655952033], [4.82038049991272, 1.257160247519029, 2.7119642579623435], [2.063304757871728, 3.955695578334879, 4.499038258378556], [4.309610027165567, 1.8911312122481907, 3.332005858908505], [3.6642966882466763, 1.0340221019201734, 2.1394287780346373], [1.014851808220519, 1.8168807108465514, 3.883964328563588], [1.0559007000964027, 1.701933005629093, 4.9182826704414655], [3.883308942682502, 3.805996296633884, 2.9713313483087926], [4.167135051945373, 1.8823515631981191, 1.516354493069138], [2.852462996322677, 4.47342716872487, 4.429356606112812], [2.0435177959479778, 1.3166593284856787, 1.7619991173755853], [2.967224091911079, 3.0903950572718277, 4.895934907903739], [2.966119422928603, 1.220940718855811, 4.356514199778456], [1.177340038021614, 4.463210521642405, 3.985493024379138], [2.684144746994798, 2.733646245071985, 3.7058208425984627], [5.038398927463475, 1.1763802476707526, 2.8907840845239794], [2.0141341956261236, 4.77849852577405, 2.8141825819117674], [4.471137237795851, 1.264758628504437, 1.0020975614116265], [3.9588226684345815, 2.83760546665806, 1.3290827434035477], [1.0745909977812547, 2.335077628973479, 1.8245336446131963], [1.8212198773994328, 4.421940329194557, 1.9705922281590664], [3.283927278525925, 4.718921989637628, 1.0012380509096905], [3.5817659713503645, 1.278798480789799, 3.85579045842465], [2.8182982420802043, 2.4807610347562536, 5.024702882471913], [4.6598919682507045, 2.3824918019147843, 4.465548809483165]])
#constraint_vector = np.array([4.005876511974748, 4.5601698553771435, 4.892958745505702, 4.6515505987598615, 4.572133578580334, 4.22227557784988, 4.2294811157263865, 4.260472871923132, 4.504618693247361, 4.323804367613552, 4.7004356148818625, 4.941191362557812, 4.655570286406181, 4.726885287084638, 4.0098422750508265, 4.859185624508852, 4.111818181259705, 4.426269329620348, 4.568103811718706, 4.658405651228994, 4.551612721515293, 4.64463158692862, 4.696130121097248, 4.21398616987616, 4.105247533779582, 4.425841631305803, 4.9091435812852815, 4.633946559576172, 4.881592837256371, 4.992296003219178])

problem = QuadraticSimplex(constraint_matrix, constraint_vector)
problem.solve()
    
