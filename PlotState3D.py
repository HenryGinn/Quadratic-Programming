import matplotlib.pyplot as plt
import numpy as np
from Poly import Poly

class PlotState3D():

    plot_size = 1

    def __init__(self, problem):
        self.problem = problem
        self.create_base_polytope()

    def create_base_polytope(self):
        self.matrix = np.concatenate((self.problem.constraint_matrix,
                                      -1 * np.eye(3)))
        self.limits = np.concatenate((self.problem.constraint_vector,
                                      np.zeros(3)))

    def plot(self):
        if self.problem.option_plot_state:
            self.do_plot()

    def do_plot(self):
        self.setup_plot()
        self.draw_state_components()
        plt.show()

    def setup_plot(self):
        self.setup_axes()
        self.set_axis_limits()
        self.set_axis_details()

    def setup_axes(self):
        self.fig = plt.figure(figsize=(20, 15))
        self.ax = plt.axes(projection='3d',computed_zorder=False)
        self.fig.add_axes(self.ax)
        self.ax.view_init(elev=14, azim=11, roll=0)

    def set_axis_limits(self):
        self.ax.set_box_aspect([1,1,1])
        self.ax.set_xlim3d([0, self.plot_size])
        self.ax.set_ylim3d([0, self.plot_size])
        self.ax.set_zlim3d([0, self.plot_size])

    def set_axis_details(self):
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.set_zlabel("z")
        blank = (1, 1, 1, 0)
        #self.ax.xaxis.line.set_color(blank)
        #self.ax.yaxis.line.set_color(blank)
        #self.ax.zaxis.line.set_color(blank)
        #self.ax.tick_params(color=blank, labelcolor=blank)

    def draw_state_components(self):
        self.draw_polytopes()
        #self.draw_quadratic_objective_function()
        self.draw_nodes()

    def draw_polytopes(self):
        self.draw_lower_polytope()
        self.draw_upper_polytope()

    def draw_lower_polytope(self):
        matrix_lower = np.concatenate((self.matrix,
                                       np.array([self.problem.profit_vector[:3]])))
        limits_lower = np.concatenate((self.limits, np.array([1])))
        Poly(matrix_lower, limits_lower, self.ax, zorder=1).plot_polytope()

    def draw_upper_polytope(self):
        matrix_upper = np.concatenate((self.matrix,
                                       -1 * np.array([self.problem.profit_vector[:3]])))
        limits_upper = np.concatenate((self.limits, np.array([-1])))
        Poly(matrix_upper, limits_upper, self.ax, zorder=4,
             facecolors="blueviolet", edgecolors="black", alpha=0.3).plot_polytope()

    def draw_quadratic_objective_function(self):
        r = self.problem.profit
        N = 300
        theta, phi = np.mgrid[0:0.5*np.pi:N*1j, 0:0.5*np.pi:N*1j]
        x = r*np.sin(theta) * np.cos(phi)
        y = r*np.sin(theta) * np.sin(phi)
        z = r*np.cos(theta)
        dot_product = self.problem.profit_vector[0]*x + self.problem.profit_vector[1]*y + self.problem.profit_vector[2]*z
        dot_product_limit = 1
        below_plane = dot_product < dot_product_limit

        x_above = np.where(below_plane, np.nan, x)
        y_above = np.where(below_plane, np.nan, y)
        z_above = np.where(below_plane, np.nan, z)
        self.ax.plot_surface(x_above, y_above, z_above, color="red", alpha=0.5, zorder=3)

    def draw_nodes(self):
        for tableau in self.problem.tableaux:
            plt.plot(*tableau.partial_position, "*k", markersize=10)
