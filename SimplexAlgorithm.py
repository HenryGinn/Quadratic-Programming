import numpy as np

np.set_printoptions(suppress=True)

class LinearProblem():
    
    """
    Each object is a linear programming problem of the form Ax <= b
    where the objective is to maximise c^T x
    """
    
    display_rounding = 4
    output_rounding = 3
    display_tableau_bool = True
    display_basic_variables_bool = True
    ntive_zero = -0.0000001
    ptive_zero =  0.0000001

    def __init__(self, matrix, b, c, B=None):
        "Initialising all variables"
        self.non_num = len(c)
        self.bas_num = len(b)
        self.var_num = self.non_num + self.bas_num
        self.N, self.B = self.get_B_and_N(B)
        self.matrix = matrix
        self.A = np.concatenate((matrix, np.identity(self.bas_num)), axis = 1)
        self.A_N = self.get_matrix_I(self.A, self.N)
        self.A_B = self.get_matrix_I(self.A, self.B)
        self.A_B_inverse = np.linalg.inv(self.A_B)
        self.A_prod = np.matmul(self.A_B_inverse, self.A_N)
        self.c = c
        c_full = np.concatenate((c, np.zeros(self.bas_num)))
        self.c_N = self.get_vector_I(c_full, self.N)
        self.c_B = self.get_vector_I(c_full, self.B)
        self.b = b
        self.update_values()
        self.update_profit_and_profit_row()
        self.problem_status = "Unsolved"

    def get_B_and_N(self, B):
        if type(B) == type(None):
            N = np.array(range(self.non_num))
            B = np.array(range(self.bas_num)) + self.non_num
        else:
            N = np.array(list(set(range(self.var_num)) - set(B)))
        return N, B

    def get_matrix_I(self, matrix, I):
        """
        Returns a matrix where the columns are given by an indexing set, I.
        For example if I = (1, 3, 4), we have
        matrix = (2, 3, 4, 1, 0)    matrix_I = (2, 4, 1)
                 (5, 6, 7, 0, 1)               (5, 7, 0)
        """
        columns = [matrix[:, i] for i in I]
        matrix_I = np.stack(columns, axis = 1)
        return matrix_I

    def get_vector_I(self, vector, I):
        """
        Returns a vector where the entries are given by an indexing set, I.
        For example if I = (1, 3, 4), we have
        vector = (2, 3, 4, 1, 0)    vector_I = (2, 4, 1)
        """
        vector_I = np.array([vector[i] for i in I])
        return vector_I

    def solve(self):
        """
        Returns the solution of the linear programming problem.
        First does dual simplex steps if it is outside the feasible region,
        then simplex steps if it is non optimal
        """
        self.display()
        while self.problem_status == "Unsolved":
            outside_feasible_region = np.any(self.values < self.ntive_zero)
            problem_non_optimal = np.any(self.profit_row_non_trivial > self.ptive_zero)
            if outside_feasible_region:
                self.dual_simplex_step()
            elif problem_non_optimal:
                self.primal_simplex_step()
            else:
                self.problem_status = "Optimal"

    def primal_simplex_step(self):
        "Performs a primal pivot of the tableau"
        pivot_index_of_N = np.argmax(self.profit_row_non_trivial)
        #pivot_index_of_N = int(input(f"{self.profit_row_non_trivial}: "))
        pivot_column = self.A_prod[:, pivot_index_of_N]
        if np.all(pivot_column <= -0.0000001):
            self.problem_status = "Unbounded"
        else:
            exiting = self.N[pivot_index_of_N]
            entering = self.get_pivot_index_of_B(pivot_column)
            self.update(exiting, entering)
            self.display()

    def get_pivot_index_of_B(self, pivot_column):
        "Returns the entering variable of a primal pivot"
        pivot_col_positive_filter = (pivot_column > self.ptive_zero)
        values_filtered = self.values[pivot_col_positive_filter]
        A_prod_filtered = pivot_column[pivot_col_positive_filter]
        B_filtered = self.B[pivot_col_positive_filter]
        theta = values_filtered / A_prod_filtered
        B_filtered_index = np.argmin(theta)
        entering_variable = B_filtered[B_filtered_index]
        return entering_variable

    def dual_simplex_step(self):
        "Performs a dual pivot of the tableau"
        pivot_index_of_B = np.argmin(self.values)
        pivot_row = self.A_prod[pivot_index_of_B, :]
        if np.all(pivot_row > self.ptive_zero):
            self.problem_status = "Infeasible"
        else:
            exiting = self.B[pivot_index_of_B]
            entering = self.get_pivot_index_of_N(pivot_row)
            self.update(entering, exiting)
            self.display()

    def get_pivot_index_of_N(self, pivot_row):
        "Returns the entering variable of a dual pivot"
        pivot_row_positive_filter = (pivot_row < self.ntive_zero)
        profits_filtered = self.c_N[pivot_row_positive_filter]
        A_prod_filtered = pivot_row[pivot_row_positive_filter]
        N_filtered = self.N[pivot_row_positive_filter]
        theta = profits_filtered / A_prod_filtered
        N_filtered_index = np.argmax(theta)
        entering_variable = N_filtered[N_filtered_index]
        return entering_variable

    def update(self, entering, exiting):
        """
        Updates N, B, A_N, A_B, A_B_inverse, c_N, c_B, values, profit
        For example, N = (0, 1, 2), B = (3, 4, 5)
        entering variable = 2 (the variable that is becoming basic)
        exiting variable = 4 (the variable that is no longer going to be basic)
        The new N is (0, 1, 4) and the new B is (3, 2, 5)

        The other variables are updated using the entering and exiting indexes
        or directly from the previous updated variables
        """
        index_entering = np.where(self.N==entering)[0][0]
        index_exiting = np.where(self.B==exiting)[0][0]
        self.update_B_and_N(index_entering, index_exiting)
        self.update_matrices(index_entering, index_exiting)
        self.update_c(index_entering, index_exiting)
        self.update_values()
        self.update_profit_and_profit_row()

    def update_B_and_N(self, index_entering, index_exiting):
        "Swapping the entering and exiting variables between the non basic and basic variables"
        entering_value = self.N[index_entering]
        exiting_value = self.B[index_exiting]
        self.B[index_exiting] = entering_value
        self.N[index_entering] = exiting_value

    def update_matrices(self, index_entering, index_exiting):
        "Swapping a column between A_N and A_B. Also computing the new A_B_inverse"
        entering_column = np.copy(self.A_N[:, index_entering])
        exiting_column = np.copy(self.A_B[:, index_exiting])
        self.A_B[:, index_exiting] = entering_column
        self.A_N[:, index_entering] = exiting_column
        self.A_B_inverse = np.linalg.inv(self.A_B)
        self.A_prod = np.matmul(self.A_B_inverse, self.A_N)

    def update_c(self, index_entering, index_exiting):
        "Updates c_N and c_B so that they correspond to the new N and B after an iteration"
        entering_value = self.c_N[index_entering]
        exiting_value = self.c_B[index_exiting]
        self.c_B[index_exiting] = entering_value
        self.c_N[index_entering] = exiting_value

    def update_values(self):
        "Computing what the new values of the non basic variables are going to be"
        self.values = np.matmul(self.A_B_inverse, self.b)

    def update_profit_and_profit_row(self):
        "Computing the new profit now that the non basic variables have changed"
        self.profit = np.dot(self.c_B, self.values)
        intermediate_matrix = np.matmul(np.transpose(self.c_B), self.A_prod)
        self.profit_row_non_trivial = self.c_N - intermediate_matrix

    def get_tableau_body(self):
        "Returns the body of the tableau where the columns are ordered with I = B, N"
        columns = [np.matmul(self.A_B_inverse, self.A[:, i]) for i in range(self.var_num)]
        tableau_body = np.stack((columns), axis = 1)
        tableau_body = tableau_body.round(15)
        return tableau_body

    def get_profit_row(self):
        "Returns the profit row of the tableau where the columns are ordered with I = B, N"
        profit_row_with_zeros = np.concatenate((self.profit_row_non_trivial,
                                                np.zeros(self.bas_num)))
        N_and_B = np.concatenate((self.N, self.B))
        profit_row_tuples = np.array(list(zip(profit_row_with_zeros, N_and_B)))
        profit_row_tuples = sorted(profit_row_tuples, key = lambda k: k[1])
        profit_row = [i[0] for i in profit_row_tuples]
        return profit_row

    def get_point(self):
        "Returns the coordinates of the current point in terms of the original variables"
        point = np.zeros(self.non_num)
        for basic_variable, value in zip(self.B, self.values):
            if basic_variable < self.non_num:
                point[basic_variable] = value
        return point

    def compute_profit(self, point):
        "Returns the profit given by the objective function at a point"
        profit = np.dot(self.c, point)
        return profit

    def display(self):
        if self.display_tableau_bool:
            self.display_tableau()
        if self.display_basic_variables_bool:
            self.display_basic_variables()
    
    def display_tableau(self):
        "Constructs the full tableau and prints it"
        tableau_body = self.get_tableau_body()
        profit_row = self.get_profit_row()
        values_reshaped = self.values.reshape((self.bas_num, 1))
        tableau_upper = np.concatenate((tableau_body, values_reshaped), axis = 1)
        tableau_lower = np.array([np.concatenate((profit_row, np.array([self.profit])))])
        tableau = np.concatenate((tableau_upper, tableau_lower), axis = 0)
        print("\n", tableau.round(self.display_rounding))

    def display_basic_variables(self):
        print(f"Basic variables: {self.B}")

    def output(self):
        "Prints core information about the solution"
        print("\n" + self.problem_status)
        for variable, value in zip(self.B, self.values):
            print(f"{variable}: {round(value, self.output_rounding)}")
        print(f"Profit: {round(self.profit, self.output_rounding)}")

A = np.array([[-3, 1],
              [3, 5],
              [1, -3],
              [9, 8]])
b = np.array([3, 90, 2, 180])
c = np.array([0.05561337, 0.0407022])
B = np.array([1, 0, 4, 2])

prob = LinearProblem(A, b, c, B)
prob.display()
prob.solve()
prob.output()
