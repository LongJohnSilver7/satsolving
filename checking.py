from cnfparser import Parser
from helper import evaluate_clause, get_current_assignment, clause_to_dict, prop_occurencetype_in_clause, ID_GEN
import os
from algorithms import *
from decisionheuristics import *
import time
import sys
import io
import contextlib


import contextlib
import sys

class DummyFile(object):
    def write(self, x): pass

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = open('trash', 'w')
    yield
    sys.stdout = save_stdout



if __name__ == "__main__":
    # parse input file

    cnf = Parser(os.path.abspath('pigeon_hole_6.cnf'))
    start = time.time()
    print(f'SAT-Check started. No visualisation yet :(')

    idgen = ID_GEN()

 
    
    dpll_backtracking = DPLL.Backtracking(0,cnf.clauses, cnf.propositions, idgen, decision_algorithm = True)
    
    #print(dpll_backtracking.watchlist.watchlist)
    #print(dpll_backtracking.watchlist.watchlist)
    with nostdout():
        print(dpll_backtracking.watchlist.watchlist)
        dpll_backtracking.dpll_algorithm(use_watchlist = True)
    

    print(get_current_assignment(cnf.propositions))

    #for p in cnf.propositions:
        #print(f'THIS ITEM IS CONTAINED IN {p.contained_in_clauses}')
    #dpll_backtracking = DPLL.Backtracking(0)
    #dpll_implicationgraph = DPLL.Implicationgraph(0)
    #print(dpll_backtracking.dpll_algorithm(cnf.clauses, cnf.propositions))
    
    #print(dpll_implicationgraph.cdcl_algorithm(cnf.clauses, cnf.propositions))
    

    fin = time.time()
    delta = fin - start
    print(f'Time in seconds: {delta}')
