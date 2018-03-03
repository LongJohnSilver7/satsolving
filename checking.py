from cnfparser import Parser
from helper import evaluate_clause, get_current_assignment, clause_to_dict, prop_occurencetype_in_clause
import os
from algorithms import *
from decisionheuristics import *
# class Decisionheuristics:
    
#     def dynamic_largest_individual_sum(self, clauses, propositions):
#         neg_max = None
#         pos_max = None
#         value_neg_max = 0
#         value_pos_max = 0

        
#         for proposition in propositions:
#             occurences_pos = 0
#             occurences_neg = 0
#             for clause in clauses:
#                 countit = prop_occurencetype_in_clause(clause, proposition)
#                 occurences_neg += countit[1]
#                 occurences_pos += countit[0]
#             if occurences_neg > value_neg_max:
#                 value_neg_max = occurences_neg
#                 neg_max = proposition
            
#             if occurences_pos > value_pos_max:
#                 value_pos_max = occurences_pos
#                 pos_max = proposition
        
#         if neg_max is None and pos_max is None:
#             return False
        
#         if value_pos_max > value_neg_max:
#             pos_max.assign(1) 
#             return pos_max
#         else:
#             neg_max.assign(0)
#             return neg_max


#     def jersolow_wang_method(self, clauses, propositions):
#         sums = []
#         for prop in propositions:
#             prop_sum = 0
#             for clause in clauses:
#                 clause_len = 0
#                 found_prop = False
#                 for p in clause.propositions:
#                     clause_len += 1
#                     if p is prop:
#                         found_prop = True
#                 if found_prop == True:
#                     prop_sum += 2**(-clause_len)
#             sums.append(prop_sum)
        
#         maxel = max(sums)
#         index = sums.index(maxel)
#         res_proposition = propositions[index]
#         return (res_proposition, index)
        

            

# class Algorithms:
    
#     def enumeration_algorithm(self, clauses, proposition_list, default_value):
#         # collection of indices of unassigned propositions
#         #unassigned_propositions = [i for i in range(len(proposition_list))]
#         unassigned_propositions = [prop for prop in proposition_list]
#         trailstack = []
#         #default_value = 0
#         while True:
#             if unassigned_propositions:
#                 # get last index on unassigned prop list
#                 #ind = unassigned_propositions.pop()
#                 proposition = unassigned_propositions.pop()
#                 #proposition_list[ind].assign(default_value, False)
#                 proposition.assign(default_value, False)
#                 #trailstack.append(proposition_list[ind])
#                 trailstack.append(proposition)
#             else:
#                 satisfied = True
#                 for clause in clauses:
#                     if evaluate_clause(clause) == False:
#                         satisfied = False
#                         break 
#                 if satisfied == True:
#                     return get_current_assignment(proposition_list)
                
#                 while True:
#                     if trailstack:
#                         last_assigned_proposition = trailstack.pop()
#                         if last_assigned_proposition.is_flippable() == True:
#                             print(f'flipped{last_assigned_proposition}')
#                             last_assigned_proposition.flip()
#                             last_assigned_proposition.set_flippable(False)
#                             trailstack.append(last_assigned_proposition)
#                             break
#                         else:
#                             last_assigned_proposition.unassign()
#                             unassigned_propositions.append(last_assigned_proposition)
#                     else:
#                         return False
#     class DPLL:
#         def dpll_algorithm(self, clauses, proposition_list):
#             trailstack = []

if __name__ == "__main__":
    cnf = Parser(os.path.abspath('test.cnf'))


    #print(jersolow_wang_method(cnf.clauses, cnf.propositions))
    #print(dynamic_largest_individual_sum(cnf.clauses, cnf.propositions))

    dpll = DPLL(0)
    print(cnf.propositions[0].value)
    print(dpll)
    print(dpll.dpll_algorithm(cnf.clauses, cnf.propositions))
    #print(enumeration_algorithm(cnf.clauses, cnf.propositions, 0))
    #print('starting enumeration_algorithm')
    #print(Algorithms.enumeration_algorithm(cnf.clauses, cnf.propositions, 0))

  