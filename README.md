# Quadratic-Programming

################################### CONTENTS ###################################

1: OVERVIEW
2: TERMINOLOGY
3: HOW BASIC VARIABLES DEFINE A VERTEX
4: HOW THE QUADRATIC ALGORITHM WORKS
5: COMPUTATION OF NEW LINEAR PROFIT FUNCTION
6: CHOOSING THE PIVOT ROW

################################### OVERVIEW ###################################

Implementation of a modified simplex algorithm to maximise x^Tx subject to Ax <= b. All variables are also non negative.

The profit function is described by a hyperplane which is defined in terms of several points, one for each spatial dimension. This function changes as the points move around the region, and when all the points converge the algorithm terminates.

Formulation issues:
    1: If the positivity constraint on a variable, x, is undesired it can be rewritten as x = x_plus - x_minus. This should be done before next step as expanding (x_plus - x_minus)^2 will introduce a cross term, 2 * x_plus * x_minus.
    
    2: All positive definite quadratic programming problems can be translated, rotated, and rescaled into the correct form for this algorithm to work.

    3: If a constraint is required to hold as an equality it can be written as two inequalities as follows. c^Tx = b becomes c^Tx <= b and -c^Tx <= -b.

################################# TERMINOLOGY #################################

Variable types:
    Space/spacial: these are variables like x, y, and z. There is one for each dimension of space we are working in. This will be referred to as n.
    Slack/constraint: these are the variables that are associated with a constraint. They are what make up the difference in an inequality. If x + 2y <= 4, then s = 4 - x - 2y so that x + 2y + s = 4 is now an equality.
    Basic: these are the variables that are not necessarily 0 that define which constraints are not necessarily active. The equations are written so that the value of these variables can be read off immediately (there is a bijection between equations and the basic variables, and the coefficient of the basic variables is 1). With this definition it can be seen that if the tableaux is restricted to the columns of the basic variables, it will be a permutation matrix.
    Non-basic: these are the variables that are not basic variables. The constraints associated with non-basic variables hold with equality.

Problem dimensions:
    space_dimension: this is the dimension of the space we are working in. It is the number of variables like x, y, z. It is also equal to the number of non basic variables there are.
    slack_dimension: this is the number of slack variables (equivalently constraints) there are. it is also equal to the number of basic variables
    total_dimension: this is the sum of space_dimension and slack_dimension - the total number of variables

Other terms:
    Feasible region: this is the set of points that satisfy all the constraints. It is a convex polytope (if it is unbounded then there is no global maximum)
    Verticies: the corners of the feasible region.
    Exiting variable: this is a basic variable that is becoming a non-basic variable. It is the variable given by the pivot column
    Entering variable: this is a non-basic variable that is becoming a basic variable. It is the variable given by the pivot row.

##################### HOW BASIC VARIABLES DEFINE A VERTEX #####################

Every slack variable has a constraint associated with it. We can also associate a constraint with the spatial variables in the following way: for the variable x, we have the constraint x >= 0. If a variable is non-zero, that means we are at a point where that constraint does not hold with equality - the variable has to be non zero to take up the slack. If a variable is non-basic, that means it is necessarily 0, and we are at a point on the constraint associated with that variable.

In a 2D problem we start at (x, y) = (0, 0). At this point, we are touching the lines x=0 and y=0. If we were not touching the constraint x => 0 for example, then the variable x would necessarily be non-zero. The non-basic variables in this case are x and y. Warning: just because a constraint holds with equality, it does not mean the variable associated with it is non-basic. For example if there was a constraint given by x - y <= 0 we would still be starting at (0, 0) with x and y as non-basic variables. Writing the constraint in equation form with a slack variable, x - y + s = 0, we can see that at the origin s = 0 holds. This means that if the non-basic variables were x and s or y and s, we would also be at (0, 0). This happens when three or more constraints intersect at a point (or along a line, or in general, on a facet).

###################### HOW THE QUADRATIC ALGORITHM WORKS ######################

We start off at the origin with a profit function given by the sum of all spatial variables. If the simplex algorithm was to be applied, there would be a choice of n different columns to have as the pivot column (one for each spatial dimension). This is because the profit is increased at the same rate for each of the variables. We split the problem into n, and initialise each of the new tableaux by picking a different pivot column. This is the same as asking the points to point in the directions of the different axes.

Each of the new tableau compute how far they can increase the chosen variable before hitting each of the constraints given by the non basic variables. If that distance is negative it can be ignored because that constraint is in the wrong direction. Out of the positive distances, the minimum is chosen - this is so that the point stays within the feasible region. This will define a new point and we can compute the value at that point given by the current profit function. We want all the points to remain feasible, so we need to choose the value that increases this profit by the smallest amount. If the profit was to be increased more than this, then there would be a point that would have to leave the feasible region to match that profit if it were to continue increasing along it's current direction. Note: this new value might be 0, and we don't move any of the points at all. This would happen when two points hit verticies at the same time for example. We would have still made progress however, as even though the points have not moved, one of the problems will have had it's basic and non-basic variables updated - this is telling it to move along different facets next iteration.

The point that has been chosen to be updated is then moved to it's new location. The global profit is then computed - this is not the value of the linear profit function, it is the value of x^Tx. Each of the other points had a direction that they were attempting to move along. The intersection of the hypersphere given by P = x^Tx and each of these lines can be found. These points define a hyperplane - this is the new linear profit function. Note that the other simplex tableax do not need to be updated.

The process described in the previous two paragraphs is then repeated. When any pair of points has the same set of basic variables and has the same pivot column (going in the same direction), they have converged to each other. They can be treated at one point from then on. Note that the angle at the origin between any pair of points is non-increasing - this implies that the solid angle is also non-increasing. When all points have converged to each other, the whole problem has converged.

################## COMPUTATION OF NEW LINEAR PROFIT FUNCTION ##################

1: Finding the line each point is moving on
    A line is defined by 2 vectors: a position vector, and a direction vector. A position vector can be found immediately by the position of the vertex where the point lies, and this is found by value of the spatial variables. These variables are either non-basic variables in which case they are 0, or they are basic variables and their values can be read directly off the tableau for that point.

    For the direction vector, we construct a matrix where the rows are the coefficients of the constraints that define the line. When a point moves from one vertex to another, one of the basic variables becomes non-basic, and one of the non-basic variables becomes basic. The non-basic variables that were not changed correspond to the constraints that define the line that the point moves along as it goes from the old vertex to the new vertex. The number of non-basic variables is equal to the number of spatial variables, so this matrix will be of size n-1 by n (the constraints are originally defined in terms of the n spatial variables). The constraints should all be linearly independent, so this leaves a null space of dimension 1 which gives us our direction vector.

2: Intersection of a line and the hypersphere P = x^Tx
    We can write the line as r = v_1 + s*v_2 where v_1 and v_2 are the position and direction vectors respectively. Substituting into r dot r = P gives a quadratic in the parameter s which can be solved to give s = (-v_1 dot v_2 +- sqrt((v_1 dot v_2)^2 - |v_1|^2 * |v_1|^2 + |v_2|^2 * P))/|v_2|^2. The plus minus ambiguity comes from the fact that a line intersects a hypersphere in two places. We choose the one in the region where all the spatial variables are non negative (note that this is well defined)

3: Defining the hyperplane
    In an N dimensional space, a hyperplane has dimension N-1. All hyperplanes can be described by a linear combination of spatial variables equalling a constant. For each of the n points in our n dimensional space, we need them to lie in the hyperplane, i.e. satisfy the equation. We can describe this sytem of linear equations with a matrix. If a pair of points are equal then the system will be underdefined - this is the situation where the hyperplane spans fewer than n-1 dimensions and has become degenerate. This is not a problem and is in fact expected when the algorithm converges. We can solve the system using the pseudoinverse. Without loss of generality we choose the constant of the hyperplane to be 1 for the purposes of finding the hyperplane, all this does is fix a scaling for the linear combination. As the matrix is never overdetermined we can always solve this system.
    
    We note that we will also have a lower rank matrix if there exist triples of colinear points. We expect that this should not happen if the points have been properly merged once convergence has been detected, but it is not known whether this is the case or not.

############################ CHOOSING THE PIVOT ROW ############################

The pivot row is the row of the basic variable that is going to leave the set of basic variables. The pivot column decides the non-basic variable that is going to enter the set of basic variables, and this determines the direction that the point is going to move along. When we move along this direction, we will intersect with the other constraints at various points as we go, and we want to stop at the first constraint so we do not leave the feasible region. To do this, we compute a value we call theta for each of the basic variables (rows of the tableau)

Simply, the theta column of the tableau is given by the value column divided by the pivot column (not including the profit row), but there are some special cases to consider. If a value is 0 this means that constraint is already holding with equality, and the point would not move any distance as this point describes the same vertex. Moving to the vertex could still get us closer to optimality if the value in the pivot column is positive however, so we need to keep track of whether it is a positive 0 or a negative 0.

Floating point numbers are intervals, and we have to deal with the fact that 0 is the interval (-epsilon, epsilon) (in the class we refer to epsilon with a class attribute called "zero"). We sum up which values of theta are valid in the table below where 0 means invalid and 1 means valid.

                Values
            0  +1  -1
Pivot    0  0   0   0
column  +1  1   1   0
        -1  0   0   1