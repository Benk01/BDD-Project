# Ben Kaufmann
# 11/21/2021
# CptS 350 Project

import pyeda
from pyeda.inter import *
from functools import reduce


# Converts a number to an array of boolean valeus
def convert_to_bool_array(num):
    return [bool(num >> n & 1) for n in range(4, -1, -1)]

# Takes a list of tuples [(bddvar, valueinbinary)] and converts to And(5 bddvars).
# The bddvar are either True or False depending on the corresponding valueinbinary
def create_expr(var_val):
    ret = []
    for var, val in var_val:
        if val:
            ret.append(var)
        else:
            ret.append(~var)
    return reduce(lambda x,y: x & y, ret)

# Takes two BDD's and 
def compose2(BDD1, BDD2):
    x = bddvars('x', 5) 
    y = bddvars('y', 5)
    z = bddvars('z', 5)
    A = BDD1.compose({x[0] : z[0], x[1]: z[1], x[2]: z[2], x[3] : z[3], x[4] : z[4]})
    B = BDD2.compose({y[0] : z[0], y[1]: z[1], y[2]: z[2], y[3] : z[3], y[4] : z[4]})
    return (A & B)



def main():
    # Creating the Graph (G) and Array of edges (R)
    G = {}
    R = []
    for node in range(0, 32):
        G[node] = []
    for i in range(0, 32):
        for j in range(0, 32):
            if ((i+3)%32 == j%32) or ((i+8)%32 == j%32):
                R.append((i, j))
                G[i].append(j)
    # Creating PRIME and EVEN arrays
    primeList = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    evenList = []
    for n in range(0, 31):
        if n%2==0: evenList.append(n)

    # Converting Arrays into BDD's
    # BDD variables
    # x = [x[0], x[1], x[2], x[3], x[4]]
    # y = [y[0], y[1], y[2], y[3], y[4]]
    x = bddvars('x', 5) 
    y = bddvars('y', 5)
    z = bddvars('z', 5)

    bdd_expr = []
    for i, j in R:
        # var_val is a list of tuples such that (bddvar, boolean value)
        # EX: x_var_val when i = 3 is [(x[0], 0), (x[1], 0), (x[2], 0), (x[3], 1), (x[4], 1)]
        x_var_val = zip(x, convert_to_bool_array(i))
        y_var_val = zip(y, convert_to_bool_array(j))
        edge = create_expr(x_var_val) & create_expr(y_var_val)
        bdd_expr.append(edge)


    # bdd_expr is a list of And(10 bddvars) for each edge in R
    # BDD_RR converts the list to an Or statement containing each of the And(10 bddvars) for each edge in R
    # Couldn't find a differnt way to compute BDD_PRIME and BDD_EVEN, so it is hardcoded
    BDD_RR = reduce(lambda a,b: a | b, bdd_expr)
    BDD_PRIME = expr2bdd(expr("(~x[0] & ~x[1] & ~x[2] & x[3] & x[4]) | (~x[0] & ~x[1] & x[2] & ~x[3] & x[4]) | (~x[0] & ~x[1] & x[2] & x[3] & x[4]) | (~x[0] & x[1] & ~x[2] & x[3] & x[4]) | (~x[0] & x[1] & x[2] & ~x[3] & x[4]) | (x[0] & ~x[1] & ~x[2] & ~x[3] & x[4]) | (x[0] & ~x[1] & ~x[2] & x[3] & x[4]) | (x[0] & ~x[1] & x[2] & x[3] & x[4]) | (x[0] & x[1] & x[2] & ~x[3] & x[4]) | (x[0] & x[1] & x[2] & x[3] & x[4])"))
    BDD_EVEN = expr2bdd(expr("(~y[0] & ~y[1] & ~y[2] & ~y[3] & ~y[4]) | (~y[0] & ~y[1] & ~y[2] & y[3] & ~y[4]) | (~y[0] & ~y[1] & y[2] & ~y[3] & ~y[4]) | (~y[0] & ~y[1] & y[2] & y[3] & ~y[4]) | (~y[0] & y[1] & ~y[2] & ~y[3] & ~y[4]) | (~y[0] & y[1] & ~y[2] & y[3] & ~y[4]) | (~y[0] & y[1] & y[2] & ~y[3] & ~y[4]) | (~y[0] & y[1] & y[2] & y[3] & ~y[4]) | (y[0] & ~y[1] & ~y[2] & ~y[3] & ~y[4]) | (y[0] & ~y[1] & ~y[2] & y[3] & ~y[4]) | (y[0] & ~y[1] & y[2] & ~y[3] & ~y[4]) | (y[0] & ~y[1] & y[2] & y[3] & ~y[4]) | (y[0] & y[1] & ~y[2] & ~y[3] & ~y[4]) | (y[0] & y[1] & ~y[2] & y[3] & ~y[4]) | (y[0] & y[1] & y[2] & ~y[3] & ~y[4]) | (y[0] & y[1] & y[2] & y[3] & ~y[4])"))


    # BDD_RR2 encodes the set of node pairs that can be reached in two steps
    BDD_RR2 = compose2(BDD_RR, BDD_RR).smoothing(z)

    #BDD_Rstar encodes the transitive closure of the graph
    H = BDD_RR2
    while True:
        H2 = H
        H = H2 | compose2(H2, BDD_RR2)
        if H.equivalent(H2):
            break
    BDD_RRstar = H

    #BDD_PE is a culmination of the previous 3 steps
    BDD_PE = BDD_RRstar & BDD_PRIME & BDD_EVEN

    if BDD_PE.smoothing():
        print("Since BDD_PE = ", BDD_PE.smoothing(x).smoothing(y), ", then for each node u in [prime], there is a node v in [even] such that u can reach v in even number of steps.")
    else:
        print("Since BDD_PE = ", BDD_PE.smoothing(x).smoothing(y), ", then there exists a node u in [prime], that does not have a node v in [even] such that u cannot reach v in even number of steps.")

main()