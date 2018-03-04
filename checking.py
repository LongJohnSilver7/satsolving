from cnfparser import Parser
from helper import evaluate_clause, get_current_assignment, clause_to_dict, prop_occurencetype_in_clause
import os
from algorithms import *
from decisionheuristics import *
import time


if __name__ == "__main__":
    cnf = Parser(os.path.abspath('test.cnf'))
    start = time.time()
    print(f'SAT-Check started. No visualisation yet :(')

    #print(jersolow_wang_method(cnf.clauses, cnf.propositions))
    #print(dynamic_largest_individual_sum(cnf.clauses, cnf.propositions))

    dpll_backtracking = DPLL.Backtracking(0)
    #dpll_implicationgraph = DPLL.Informationgraph(0)
    print(dpll_backtracking.dpll_algorithm(cnf.clauses, cnf.propositions))
    #print(dpll_implicationgraph.)
    #for pr in cnf.clauses:
    #    print(pr.state)
    #print(dpll.trailstack)
    #print(enumeration_algorithm(cnf.clauses, cnf.propositions, 0))
    fin = time.time()
    delta = fin - start
    print(f'Time in seconds: {delta}')
    
    #print('starting enumeration_algorithm')
    #print(Algorithms.enumeration_algorithm(cnf.clauses, cnf.propositions, 0))

  