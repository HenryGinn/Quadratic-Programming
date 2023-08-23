# Quadratic-Programming

## CONTENTS

1. [Overview](#overview)
1. [Terminology](#terminology)
1. [How Basic Variables Define a Vertex](#how-basic-variables-define-a-vertex)
1. [How The Quadratic Algorithm Works](#how-the-quadratic-algorithm-works)
1. [Computation of New Linear Profit Function](#computation-of-new-linear-profit-function)
1. [Choosing The Profit Row](#choosing-the-profit-row)
1. [Convergence and Non-Uniqueness](#convergence-and-non-uniqueness)
1. [Discussion of Degenerative Situations](#discussion-of-degenerative-situations)
1. [Linear Algebra Implementation of Simplex](#linear-algebra-implementation-of-simplex)
1. [Determining Uniqueness of Solutions](#determining-uniqueness-of-solutions)

## Overview

Implementation of a modified simplex algorithm to maximise x^Tx subject to Ax <= b. All variables are also non negative.

The profit function is described by a hyperplane which is defined in terms of several points, one for each spatial dimension. This function changes as the points move around the region, and when all the points converge the algorithm terminates.

### Formulation Issues
- If the positivity constraint on a variable, x, is undesired it can be rewritten as x = x_plus - x_minus. This should be done before next step as expanding (x_plus - x_minus)^2 will introduce a cross term, 2 * x_plus * x_minus.
- All positive definite quadratic programming problems can be translated, rotated, and rescaled into the correct form for this algorithm to work.
- If a constraint is required to hold as an equality it can be written as two inequalities as follows. c^Tx = b becomes c^Tx <= b and -c^Tx <= -b.

## Terminology

### Variable Types
- Space/spacial: these are variables like x, y, and z. There is one for each dimension of space we are working in. This will be referred to as n.
- Slack/constraint: these are the variables that are associated with a constraint. They are what make up the difference in an inequality. If x + 2y <= 4, then s = 4 - x - 2y so that x + 2y + s = 4 is now an equality.
- Basic: these are the variables that are not necessarily 0 that define which constraints are not necessarily active. The equations are written so that the value of these variables can be read off immediately (there is a bijection between equations and the basic variables, and the coefficient of the basic variables is 1). With this definition it can be seen that if the tableaux is restricted to the columns of the basic variables, it will be a permutation matrix.
- Non-basic: these are the variables that are not basic variables. The constraints associated with non-basic variables hold with equality.

### Problem Dimensions
- Space_dimension: this is the dimension of the space we are working in. It is the number of variables like x, y, z. It is also equal to the number of non basic variables there are.
- Slack_dimension: this is the number of slack variables (equivalently constraints) there are. it is also equal to the number of basic variables
- Total_dimension: this is the sum of space_dimension and slack_dimension - the total number of variables

### Other Terms
- Feasible region: this is the set of points that satisfy all the constraints. It is a convex polytope (if it is unbounded then there is no global maximum)
- Vertices: the corners of the feasible region.
- Exiting variable: this is a basic variable that is becoming a non-basic variable. It is the variable given by the pivot column
- Entering variable: this is a non-basic variable that is becoming a basic variable. It is the variable given by the pivot row.

## How Basic Variables Define a Vertex

Every slack variable has a constraint associated with it. We can also associate a constraint with the spatial variables in the following way: for the variable $x$, we have the constraint $x \ge 0$. If a variable is non-zero, that means we are at a point where that constraint does not hold with equality - the variable has to be non zero to take up the slack. If a variable is non-basic, that means it is necessarily 0, and we are at a point on the constraint associated with that variable.

In a 2D problem we start at $(x, y) = (0, 0)$. At this point, we are touching the lines $x = 0$ and $ = 0$. If we were not touching the constraint $x \ge 0$ for example, then the variable $x$ would necessarily be non-zero. The non-basic variables in this case are $x$ and $y$. Warning: just because a constraint holds with equality, it does not mean the variable associated with it is non-basic. For example if there was a constraint given by $x - y \le 0$ we would still be starting at $(0, 0)$ with $x$ and $y$ as non-basic variables. Writing the constraint in equation form with a slack variable, $x - y + s = 0$, we can see that at the origin $s = 0$ holds. This means that if the non-basic variables were $x$ and $s$ or $y$ and $s$, we would also be at $(0, 0)$. This happens when three or more constraints intersect at a point (or along a line, or in general, on a facet).

## How The Quadratic Algorithm Works

We start off at the origin with a profit function given by the sum of all spatial variables. If the simplex algorithm was to be applied, there would be a choice of n different columns to have as the pivot column (one for each spatial dimension). This is because the profit is increased at the same rate for each of the variables. We split the problem into n, and initialise each of the new tableaux by picking a different pivot column. This is the same as asking the points to point in the directions of the different axes.

Each of the new tableau compute how far they can increase the chosen variable before the linear objective function hits each of the constraints given by the non-basic variables. If that distance is negative it can be ignored because that constraint is in the wrong direction. Out of the positive distances, the minimum is chosen - this is so that the point stays within the feasible region. This will define a new point and we can compute the value at that point given by the quadratic profit function. We want all the points to remain feasible, so we need to choose the value that gives the smallest quadratic profit. If the profit was to be increased more than this, then there would be a point that would have to leave the feasible region to match that profit if it were to continue increasing along it's current direction.

Note that this minimum distance might be 0, and we don't move any of the points at all. This would happen when two points hit vertices at the same time for example. We would have still made progress however, as even though the points have not moved, one of the points will have had it's basic and non-basic variables updated - this is telling it to move along a different line next iteration. When this happens we do not need to update the hyperplane, and if it happens at the start, the hyperplane may in fact not be defined so it couldn't be updated anyway.

Each of the points has a current direction they are moving in given by the pivot column. The line the point is trying to move along can be found, and the intersection of this line with the quadratic profit function can be computed. This intersection must be a feasible point because we chose to increase the profit hypersphere until it hit the closest of the vertices along the different directions the points were moving in. These points define a hyperplane - this is the new linear profit function. Note that the simplex tableaux do not need to be updated for the other points as they have not had their basic and non-basic variables updated. Any points who's intersection point lies on their next vertex will have their basic and non-basic variables updated to those vertices in the next iterations.

The process described in the previous two paragraphs is then repeated. When any pair of points have the same spatial coordinates and are going in the same direction, they have converged to each other. Note that being in the same point in space is not the same as having the same basic variables, and that moving in the same direction is not the same as having the same pivot column. They can be treated as one point from then on. Note that the angle at the origin between any pair of points is non-increasing - this implies that the solid angle is also non-increasing.

Below is an overview of the algorithm
Initialisation:
1. Objective function is defined as the hyperplane with the normal vector with all it's components equal to 1.
1. n points are defined where all spatial coordinates are non-basic (this describes the origin).
1. The pivot column of each point is prescribed to point along one of the axes.

Iteration:
1. The reference and direction vector are set for each tableau
1. Check if any points have converged to each other and merge these points.
1. For all points, determine which vertex the linear objective function will hit next.
1. Determine which point is going to be updated by finding which one increases the quadratic profit the least if it were to be moved to it's next vertex.
1. Update the basic and non-basic variables of the chosen point.
    - If the point moved
        - Compute partial positions of all points
        - Compute new linear objective function
        - Update all pivot columns
    - If the point didn't move
    	- Update pivot column of updated point

## Computation of New Linear Profit Function

### Finding the Line Each Point is Moving on

A line is defined by 2 vectors: a position vector, and a direction vector. A position vector can be found immediately by the position of the vertex where the point lies, and this is found by value of the spatial variables. These variables are either non-basic variables in which case they are 0, or they are basic variables and their values can be read directly off the tableau for that point.

For the direction vector, we construct a matrix where the rows are the coefficients of the constraints that define the line. When a point moves from one vertex to another, one of the basic variables becomes non-basic, and one of the non-basic variables becomes basic. The non-basic variables that were not changed correspond to the constraints that define the line that the point moves along as it goes from the old vertex to the new vertex. The number of non-basic variables is equal to the number of spatial variables, so this matrix will be of size n-1 by n (the constraints are originally defined in terms of the n spatial variables). The constraints should all be linearly independent, so this leaves a null space of dimension 1 which gives us our direction vector.

### Intersection of a Line and The Hypersphere $P = x^Tx$

We can write the line as r = v_1 + s*v_2 where v_1 and v_2 are the position and direction vectors respectively. Substituting into r dot r = P gives a quadratic in the parameter s which can be solved to give s = (-v_1 dot v_2 +- sqrt((v_1 dot v_2)^2 - |v_1|^2 * |v_2|^2 + |v_2|^2 * P))/|v_2|^2. The plus minus ambiguity comes from the fact that a line intersects a hypersphere in two places. We choose the one in the region where all the spatial variables are non negative (note that this is well defined)

### Defining The Hyperplane

In an $N$ dimensional space, a hyperplane has dimension $N-1$. All hyperplanes can be described by a linear combination of spatial variables equalling a constant. We need to find a hyperplane that passes through all of our points, i.e. each of the points satisfy the hyperplane equation. Each point gives a linear equations, and we can describe this system with a matrix. Once points have merged together or their potential positions are the same, then the system will be underdefined - this is the situation where the hyperplane spans fewer than $n-1$ dimensions and has become degenerate. We remove any duplicate potential positions, and solve the system using the pseudoinverse. As we have $n$ degrees of freedom and may have fewer than $n$ equations, using the pseudoinverse corresponds to choosing one of the hyperplanes that works. Without loss of generality we choose the constant of the hyperplane to be 1 for the purposes of finding the hyperplane, as all this does is fix a scaling for the linear combination. As the matrix is never overdetermined we can always solve this system, although we need to ensure that all the points defining the hyperplane are distinct. The pseudoinverse is given by $A^+ = A^T (A A^T)^{-1}$ which means the system we need to solve is ${v = A^+ 1 = A^T (A A^T)^{-1} 1}$. If we set ${w = (A A^T)^{-1} 1}$ then $w$ is the solution to ${(A A^T) 1}$, and we have ${v = A^T w}$.

We note that we will also have a lower rank matrix if there exist triples of co-linear points. We expect that this should not happen if the points have been properly merged once convergence has been detected, but it is not known whether this is the case or not.

## Choosing The Profit Row

The pivot row is the row of the basic variable that is going to leave the set of basic variables. The pivot column decides the non-basic variable that is going to enter the set of basic variables, and this determines the direction that the point is going to move along. When we move along this direction, we will intersect with the other constraints at various points as we go, and we want to stop at the first constraint so we do not leave the feasible region. To do this, we compute a value we call theta for each of the basic variables (rows of the tableau)

Simply, the theta column of the tableau is given by the value column divided by the pivot column (not including the profit row), but there are some special cases to consider. If a value is 0 this means that constraint is already holding with equality, and the point would not move any distance as this point describes the same vertex. Moving to the vertex could still get us closer to optimality if the value in the pivot column is positive however, so we need to keep track of whether it is a positive 0 or a negative 0.

Floating point numbers are intervals, and we have to deal with the fact that 0 is the interval $(-\epsilon, \epsilon)$ (in the class we refer to $\epsilon$ with a class attribute called "zero"). We sum up which values of theta are valid in the table below where 0 means invalid and 1 means valid.

                Values
            0  +1  -1
Pivot    0  0   0   0
column  +1  1   1   0
        -1  0   0   1

## Convergence and Non-Uniqueness

If any of the points have all non-negative entries in the profit row then the problem has converged. This follows from the strict convexity of $x^T x$, and it will also be the case that all other points will have all non-negative entries in the profit row. This fits nicely with the optimality conditions of the simplex algorithm, and it is also consistent with the fact that choosing a pivot column for such a point is now undefined.

Convergence does not imply that all points have merged into one. It is possible for there to be multiple solutions to a quadratic maximisation problem, for example a problem with the single constraint $x + y \le 10$ will have solutions (10, 0) and (0, 10). In this situation the algorithm will terminate and both of these will be given as optimal points.

We conjecture that the algorithm will show multiple optimal points if and only if they are adjacent to each other, that is, connected by single constraint. This is similar to non-uniqueness for the simplex algorithm where if the intersection of constraints forms a facet that overlaps with the objective function then all points within the facet are optimal points (this set is convex). The algorithm can have points that lie on optimal points but it does not necessarily terminate and can continue iterating.

## Discussion of Degenerative Situations

Suppose at the start of the algorithm there are several constraints that pass through the origin. In this case the first step of the algorithm will choose one of the points that is constrained by one of those constraints and update it's basic and non-basic variables. Spatially nothing has happened however, and it seems that some of the next stages may be poorly defined. In this section we describe what happens in this situation.

If no points have changed location, a new objective function does not need to be found. The only difference has happened under the hood via a change in basic and non-basic variables, so it makes sense that we use the same objective function in the next iteration as geometrically nothing has changed.

We consider the 2D problem where we have $x \le 1$, $y \le 0$ and non-negativity constraints. The $y \le 0$ constraint effectively reduces this problem into 1 dimension, so we expect the algorithm to realise this and merge the two points into one. We will refer to the points moving in the $x$ and $y$ directions as point $X$ and point $Y$ respectively.

In the first step of the algorithm, point $Y$ is chosen as the first point to be updated as the most it can move is 0 before hitting a constraint. It's basic and non-basic variables update, and as no change has been made spatially, we keep the same objective function. As we have the same objective function, we do not need to update the direction of point $X$, and we only need to choose a new direction for point $Y$.

The objective function would have been initialised as $P = x + y$, so point $Y$ will be chosen to increase along the $y \le 0$ constraint. Both points are now at the origin and moving towards the right - these are exactly our conditions for points to have converged to each other, so one of the points can be deleted. We now have 1 point left and the computed objective function will have it's normal given by the coordinates of that point. The algorithm will terminate on the next step at (1, 0).

## Linear Algebra Implementation of Simplex

Once the slack variables are added we have a system of equations, ${Ax = b}$. We can write $x_B$ and $x_N$ have components equal to the basic and non-basic variables respectively. Similarly we define the matrices $A_B$ and $A_N$ which have the columns of the indices of the basic and non-basic variables respectively. In these new variables the system ${Ax = b}$ turns into ${A_B x_B + A_N x_N = b}$, and similarly the objective function can be written as ${c_B^T x_B + c_N^T x_N}$.

This can be rearranged as the following:
${x_B = A_B^{-1} b - A_B^{-1} A_N x_N}$
${z = c_B^T A_B^{-1} b + (c_N^T - c_B^T A_B^{-1} A_N) x_N}$
These describe the relevant parts of the tableau and the profit row respectively.

We never find the inverse of $A_B$. Instead we compute it's LU factorisation and use it to solve linear systems. This is because it is faster, saves memory, and is more stable.

The tableau is ${x_B = A_B^{-1} b - A_B^{-1} A_N x_N}$. The components of $x_N$ are 0, so the first term here , $A_B^{-1} b$, gives the value of $x_B$ (the numbers in the value column of the tableau). The second term forms the non-basic part of the tableau, and we use this to find the pivot column. We write $A_i$ for the column of $A_N$ corresponding to the i'th non-basic variable, and ${A_B^{-1} A_i}$ gives the value of the column in the tableau. We can find this by solving the linear system ${A_B v = A_i}$ for $v$.

Similarly we can extract information from the profit row. The profit is given by ${c_B^T A_B^{-1} b}$, and we note that this is the same as finding the dot product of $c_B$ with the values of the basic variables found above. ${c_N^T - c_B^T A_B^{-1} A_N}$ gives the non-basic values in the profit row. Taking the transpose of this gives ${c_N - A_N^T A_B^{-T} c_B}$. We can find the value of ${A_B^{-T} c_B}$ by solving the linear system ${A_B^T v = c_B}$, and then substitute this in to find the profit row. We note that once the LU factorisation of $A$ has been found, the LU factorisation of $A^T$ is also given as ${A^T = (LU)^T = U^T L^T}$ and $U^T$, $L^T$ are lower and upper triangular matrices respectively.

## Determining Uniqueness of Solutions

If we have a quadratic programming problem to maximise $x^T x$ subject to ${Ax \le b}$ then we can construct a new quadratic programming problem that tells us whether the solution is unique. We attempt to solve two problems at once while also maximising the different between them.

If we have two vectors, $x$ and $y$, which satisfy ${Ax \le b}$ and ${Ay \le b}$ then we can describe their difference with ${(x-y)^T (x-y)}$. If we maximise this difference and it is 0 then we know the solution is unique, although we need to ensure that we are not affecting the value of ${x^T x}$ and ${y^T y}$.

We want a profit function that maximises the original objective function while also maximising the difference. If the maximum of ${x^T x}$ subject to ${Ax \le b}$ is equal to $P$, we want it to be the case that if ${x^T x}$ or ${y^T y < P}$ then our new profit function would be lower than if ${x^T x = P = y^T y}$, even if we have maximised the difference in the first case.

We conjecture that this cannot always be guaranteed, but if we restrict to the case where we know the coordinates of any optimal point will have components equal to 0 or 1 then we can. The maximum value of the difference is equal to the number of variables in the original problem, so we consider the profit function given by ${(len(x) + 1) \dot (x^T x + y^T y) + (x-y)^T (x-y)}$.

In this situation if the original problems are any less than the maximim then we have ${x^T x + y^T y \le 2P - 1}$ and the maximum profit will occur when ${(x-y)^T (x-y)}$ is maximised. This gives us $P \le (len(x) + 1) \dot (2P-1) + len(x) = 2P \dot len(x) + 2P - len(x) - 1 + len(x) = 2P \dot len(x) + 2P - 1$. Alternatively if ${x^T x}$ and ${y^T y}$ are maximised, then we will have $P = (len(x) + 1) \dot 2P + (x-y)^T (x-y) \ge (len(x) + 1) \dot 2P = 2P \dot len(x) + 2P > 2P \dot len(x) + 2P - 1$, and we see that the profit is strictly greater than in the first case.

This new problem is not in the correct form for this algorithm, but it can be put into the right form as outlined in the overview section. We also note that if there are many variables then this may lead to poor conditioning of the problem.
