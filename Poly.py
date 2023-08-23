from itertools import combinations

import numpy as np
from scipy.linalg import solve
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
from hgutilities import defaults

class Poly():

    def __init__(self, A, b, ax, **kwargs):
        self.A = np.array(A)
        self.b = np.array(b)
        self.ax = ax
        self.constraint_count = self.b.shape[0]
        defaults.kwargs(self, kwargs)
    
    def plot_polytope(self):
        for index in range(self.constraint_count):
            self.create_polygon(index)

    def create_polygon(self, index):
        other_indices = np.array([i for i in range(self.constraint_count)
                                  if i != index])
        intersections = self.get_intersections(index, other_indices)
        self.add_polygon(intersections, index)

    def get_intersections(self, index, other_indices):
        intersections = [self.get_intersection(index, index_1, index_2)
                         for index_1, index_2 in combinations(other_indices, 2)]
        intersections = [intersection for intersection in intersections if intersection is not None]
        intersections = [vertex for vertex in intersections
                         if np.all(np.dot(self.A, vertex) <= self.b + 0.001)]
        return intersections

    def get_intersection(self, index, index_1, index_2):
        indices = np.array([index, index_1, index_2])
        matrix = self.A[indices]
        vector = self.b[indices]
        intersection = self.solve_intersection(matrix, vector)
        return intersection

    def solve_intersection(self, matrix, vector):
        try:
            intersection = solve(matrix, vector)
        except:
            intersection = None
        return intersection

    def add_polygon(self, vertices, index):
        shifted_vertices = vertices - np.mean(vertices, axis=0)
        if np.any(np.array([np.linalg.norm(vertex) for vertex in shifted_vertices]) > 0.001):
            basis_vectors = self.get_basis_vectors(index, shifted_vertices)
            angles = self.get_angles(shifted_vertices, basis_vectors)
            _, vertices = zip(*sorted(zip(angles, vertices), key=lambda pair: pair[0]))
            self.ax.add_collection3d(Poly3DCollection([vertices], alpha=self.alpha, edgecolors=self.edgecolors,
                                                      linewidths=self.linewidths, facecolors=self.facecolors,
                                                      zorder=self.zorder))

    def get_basis_vectors(self, index, vertices):
        normal = self.A[index]
        vector_1 = [vertex for vertex in vertices
                    if np.linalg.norm(vertex) > 0.001][0]
        vector_2 = np.cross(normal, vector_1)
        basis_vectors = np.transpose(np.stack((vector_1, vector_2)))
        return basis_vectors

    def get_angles(self, shifted_vertices, basis_vectors):
        angles = [self.get_angle(vertex, basis_vectors)
                  for vertex in shifted_vertices]
        return angles

    def get_angle(self, vertex, basis_vectors):
        x, y = np.linalg.lstsq(basis_vectors, vertex, rcond=None)[0]
        x, y = round(x, 6), round(y, 6)
        if x > 0:
            return np.arctan(y/x)
        elif x < 0:
            if y >= 0:
                return np.arctan(y/x) + np.pi
            else:
                return np.arctan(y/x) - np.pi
        else:
            if y >= 0:
                return np.pi/2
            else:
                return -np.pi/2
        
defaults.load(Poly)
