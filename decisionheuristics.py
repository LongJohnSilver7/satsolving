from cnfparser import Parser
from helper import evaluate_clause, get_current_assignment, clause_to_dict, prop_occurencetype_in_clause
import os

def dynamic_largest_individual_sum(clauses, propositions):
    neg_max = None
    pos_max = None
    value_neg_max = 0
    value_pos_max = 0

        
    for proposition in propositions:
        occurences_pos = 0
        occurences_neg = 0
        for clause in clauses:
            countit = prop_occurencetype_in_clause(clause, proposition)
            occurences_neg += countit[1]
            occurences_pos += countit[0]
        if occurences_neg > value_neg_max:
            value_neg_max = occurences_neg
            neg_max = proposition
            
        if occurences_pos > value_pos_max:
            value_pos_max = occurences_pos
            pos_max = proposition
        
    if neg_max is None and pos_max is None:
        return False
        
    if value_pos_max > value_neg_max:
        pos_max.assign(1) 
        return pos_max
    else:
        neg_max.assign(0)
        return neg_max


def jersolow_wang_method(clauses, propositions):
    sums = []
    for prop in propositions:
        prop_sum = 0
        for clause in clauses:
            clause_len = 0
            found_prop = False
            for p in clause.propositions:
                clause_len += 1
                if p is prop:
                    found_prop = True
            if found_prop == True:
                prop_sum += 2**(-clause_len)
        sums.append(prop_sum)
        
    maxel = max(sums)
    index = sums.index(maxel)
    res_proposition = propositions[index]
    return (res_proposition, index)