from cnfparser import Parser
from helper import evaluate_clause, get_current_assignment, clause_to_dict, prop_occurencetype_in_clause
import os
from algorithms import *
from decisionheuristics import *
import time


if __name__ == "__main__":
    # parse input file
    cnf = Parser(os.path.abspath('test.cnf'))
    start = time.time()
    print(f'SAT-Check started. No visualisation yet :(')

    dpll_backtracking = DPLL.Backtracking(0)
    dpll_implicationgraph = DPLL.Implicationgraph(0)
    print(dpll_backtracking.dpll_algorithm(cnf.clauses, cnf.propositions))
    
    #print(dpll_implicationgraph.cdcl_algorithm(cnf.clauses, cnf.propositions))
    

    fin = time.time()
    delta = fin - start
    print(f'Time in seconds: {delta}')
