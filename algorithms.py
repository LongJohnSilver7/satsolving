from cnfparser import Parser
from helper import evaluate_clause, get_current_assignment, clause_to_dict, prop_occurencetype_in_clause
import os

def enumeration_algorithm(clauses, proposition_list, default_value):
    # collection of indices of unassigned propositions
    #unassigned_propositions = [i for i in range(len(proposition_list))]
    unassigned_propositions = [prop for prop in proposition_list]
    trailstack = []
    #default_value = 0
    while True:
        if unassigned_propositions:
            # get last index on unassigned prop list
            #ind = unassigned_propositions.pop()
            proposition = unassigned_propositions.pop()
            #proposition_list[ind].assign(default_value, False)
            proposition.assign(default_value, False)
            # trailstack.append(proposition_list[ind])
            trailstack.append(proposition)
        else:
            satisfied = True
            for clause in clauses:
                if evaluate_clause(clause) == False:
                    satisfied = False
                    break
            if satisfied == True:
                return get_current_assignment(proposition_list)
            while True:
                if trailstack:
                    last_assigned_proposition = trailstack.pop()
                    if last_assigned_proposition.is_flippable() == True:
                        last_assigned_proposition.flip()
                        last_assigned_proposition.set_flippable(False)
                        trailstack.append(last_assigned_proposition)
                        break
                    else:
                        last_assigned_proposition.unassign()
                        unassigned_propositions.append(last_assigned_proposition)
                else:
                    return False

class DPLL:

    def __init__(self, default_value):
        self.default_value = default_value
        self.trailstack = []

    def dpll_algorithm(self, clauses, proposition_list):
        self.trailstack = []
        if not self.BCP(clauses, proposition_list):
            return False
        while True:
            if not self.decide(clauses, proposition_list):
                return get_current_assignment(proposition_list)    
            while not self.BCP(clauses, proposition_list):
                if not self.backtrack(clauses, proposition_list):
                    return False



    def BCP(self, clauses, proposition_list):
        # update all states, check immediately for the state. If it is unsatisfied, return False immediately
        for clause in clauses:
            clause.update_state()
            # push proposition from a unit clause on trail
            if clause.state == Parser.CLAUSESTATE.UNIT:
                self.trailstack.append(clause.missing_proposition)
                clause.missing_proposition.set_decided(True)
                clause.missing_proposition.assign(clause.implied_unitvalue)
            elif clause.state == Parser.CLAUSESTATE.UNSATISFIED:
                return False
        
        # only returns True, if there are no unsatisfied clauses
        return True

    def decide(self,clauses, proposition_list):
        for prop in proposition_list:
            if prop.assigned == False and prop.decided == False:
                prop.assign(self.default_value)
                prop.set_decided(False)
                self.trailstack.append(prop)
                return True
        
        for cl in clauses:
            cl.update_state()
        return False
    
    def backtrack(self, clauses, proposition_list):
        while True:
            if not self.trailstack:
                return False
            prop_from_unit = self.trailstack.pop()
            if not prop_from_unit.decided:
                self.trailstack.append(prop_from_unit)
                prop_from_unit.flip()
                prop_from_unit.set_decided(True)
                return True
            else:
                prop_from_unit.unassign()

                
            
