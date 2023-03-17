import matplotlib.pyplot as plt
import numpy as np
from Constraint import Constraint

class PlotState():

    x_min = -1
    y_min = -1
    x_max = 13
    y_max = 13

    def __init__(self, problem):
        self.problem = problem
        self.create_constraints()

    def if_plot(self):
        if self.problem.option_plot_state:
            if self.problem.space_dimensions == 2:
                return True
        return False

    def create_constraints(self):
        if self.if_plot():
            self.set_constraint_objects()
            self.add_spatial_constraints()

    def set_constraint_objects(self):
        constraint_data = zip(self.problem.constraint_matrix,
                              self.problem.constraint_vector)
        self.constraint_objects = [Constraint(self, constraint, value)
                                   for constraint, value in constraint_data]

    def add_spatial_constraints(self):
        x_constraint = Constraint(self, np.array([-1, 0]), 0)
        y_constraint = Constraint(self, np.array([0, -1]), 0)
        self.constraint_objects.append(x_constraint)
        self.constraint_objects.append(y_constraint)

    def plot(self):
        if self.if_plot():
            self.do_plot()

    def do_plot(self):
        plt.figure()
        self.draw_state_components()
        self.set_axes()
        self.set_plot_labels()
        plt.show()

    def draw_state_components(self):
        self.draw_constraints()
        self.draw_vertex_positions()
        self.draw_quadratic_profit_function()
        self.draw_linear_profit_function()

    def draw_constraints(self):
        for constraint in self.constraint_objects:
            plt.fill(constraint.x_values, constraint.y_values, 'skyblue')
        
    def draw_vertex_positions(self):
        vertex_positions = [tableau.get_vertex_position()
                            for tableau in self.problem.tableaux]
        x_values = [position[0] for position in vertex_positions]
        y_values = [position[1] for position in vertex_positions]
        plt.plot(x_values, y_values, '*b')

    def draw_quadratic_profit_function(self):
        radius = self.problem.profit
        profit_function = plt.Circle((0, 0), radius=radius, color='r', fill=False)
        plt.gca().add_artist(profit_function)

    def draw_linear_profit_function(self):
        potential_positions = [tableau.partial_position
                               for tableau in self.problem.tableaux]
        x_values = [position[0] for position in potential_positions]
        y_values = [position[1] for position in potential_positions]
        plt.plot(x_values, y_values, '-k')

    def set_axes(self):
        plt.gca().set_aspect(1)
        plt.xlim((self.x_min, self.x_max))
        plt.ylim((self.y_min, self.y_max))

    def set_plot_labels(self):
        plt.title("Quadratic Programming Algorithm", fontsize = 20)
        plt.xlabel("x", fontsize = 15)
        plt.ylabel("y", fontsize = 15)
