class Constraint():

    def __init__(self, plot, constraint, value):
        self.plot_obj = plot
        self.set_constraint_information(constraint, value)
        self.set_window_limits()
        self.set_points()
        self.set_x_and_y_values()

    def set_constraint_information(self, constraint, value):
        self.x_coefficient = constraint[0]
        self.y_coefficient = constraint[1]
        self.value = value

    def set_window_limits(self):
        self.x_min = self.plot_obj.x_min
        self.y_min = self.plot_obj.y_min
        self.x_max = self.plot_obj.x_max
        self.y_max = self.plot_obj.y_max

    def set_points(self):
        if self.x_coefficient == 0:
            self.set_points_horizontal()
        elif self.y_coefficient == 0:
            self.set_points_vertical()
        else:
            self.set_points_diagonal()

    def set_points_horizontal(self):
        self.point_1 = (self.x_min, self.value)
        self.point_2 = (self.x_max, self.value)

    def set_points_vertical(self):
        self.point_1 = (self.value, self.y_min)
        self.point_2 = (self.value, self.y_max)

    def set_points_diagonal(self):
        self.set_intercepts()
        if self.x_coefficient / self.y_coefficient < 0:
            self.set_points_positive_gradient()
        else:
            self.set_points_negative_gradient()

    def set_intercepts(self):
        self.x_intercept_min = (self.value - self.y_coefficient * self.y_min) / self.x_coefficient
        self.y_intercept_min = (self.value - self.x_coefficient * self.x_min) / self.y_coefficient
        self.x_intercept_max = (self.value - self.y_coefficient * self.y_max) / self.x_coefficient
        self.y_intercept_max = (self.value - self.x_coefficient * self.x_max) / self.y_coefficient

    def set_points_positive_gradient(self):
        self.set_point_1_positive_gradient()
        self.set_point_2_positive_gradient()

    def set_point_1_positive_gradient(self):
        if self.x_intercept_min > self.x_min:
            self.point_1 = (self.x_intercept_min, self.y_min)
        else:
            self.point_1 = (self.x_min, self.y_intercept_min)

    def set_point_2_positive_gradient(self):
        if self.x_intercept_max > self.x_max:
            self.point_2 = (self.x_max, self.y_intercept_max)
        else:
            self.point_2 = (self.x_intercept_max, self.y_max)

    def set_points_negative_gradient(self):
        self.set_point_1_negative_gradient()
        self.set_point_2_negative_gradient()

    def set_point_1_negative_gradient(self):
        if self.x_intercept_max > self.x_min:
            self.point_1 = (self.x_intercept_max, self.y_max)
        else:
            self.point_1 = (self.x_min, self.y_intercept_min)

    def set_point_2_negative_gradient(self):
        if self.x_intercept_min > self.x_max:
            self.point_2 = (self.x_max, self.y_intercept_max)
        else:
            self.point_2 = (self.x_intercept_min, self.y_min)

    def set_x_and_y_values(self):
        self.set_corners()
        self.x_values = (self.point_1[0], self.point_2[0], self.x_corner)
        self.y_values = (self.point_1[1], self.point_2[1], self.y_corner)

    def set_corners(self):
        self.set_x_corner()
        self.set_y_corner()
    
    def set_x_corner(self):
        if self.x_coefficient > 0:
            self.x_corner = self.x_max
        else:
            self.x_corner = self.x_min

    def set_y_corner(self):
        if self.y_coefficient > 0:
            self.y_corner = self.y_max
        else:
            self.y_corner = self.y_min

    def __str__(self):
        string = (f"X coefficient: {self.x_coefficient}\n"
                  f"Y coefficient: {self.y_coefficient}\n"
                  f"Value: {self.value}\n"
                  f"Point 1: {self.point_1}\n"
                  f"Point 2: {self.point_2}\n")
        return string
