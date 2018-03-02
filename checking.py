from cnfparser import Parser
from helper import evaluate_clause, get_current_assignment, clause_to_dict
import os
class Decision():
    
    def __init__(self):
        print('test')
    def enumeration_algorithm(clauses, proposition_list):
        # collection of indices of unassigned propositions
        unassigned_propositions = [i for i in range(len(proposition_list))]
        trailstack = []
        print(clauses)
        default_value = 0
        while True:
            if unassigned_propositions:
                # get last index on unassigned prop list
                ind = unassigned_propositions.pop()
                proposition_list[ind].assign(default_value, False)
                trailstack.append(proposition_list[ind])
            else:
                satisfied = True
                for clause in clauses:
                    print(clause)
                    if evaluate_clause(clause) == False:
                        print(f'clause {clause} evaluated to flase')
                        satisfied = False
                        break 
                if satisfied == True:
                    print('no clause was false')
                    return get_current_assignment(proposition_list)
                
                while True:
                    if trailstack:
                        last_assigned = trailstack.pop()
                        if last_assigned.is_flippable() == True:
                            last_assigned.flip()
                            last_assigned.set_flippable(False)
                            break
                    else:
                        return False
                

if __name__ == "__main__":
    cnf = Parser(os.path.abspath('pigeon_hole_6.cnf'))
    print('starting enumeration_algorithm')
    print(Decision.enumeration_algorithm(cnf.clauses, cnf.propositions))

  