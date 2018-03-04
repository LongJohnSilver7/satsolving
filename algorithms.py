from cnfparser import Parser
from helper import evaluate_clause, get_current_assignment, clause_to_dict, prop_occurencetype_in_clause
import os
#from implicationgraph import Implicationgraph

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

# davis-putnam-logemann-loveland algorithms
class DPLL:


    def __init__(self, default_value):
        pass


    class Backtracking:
        
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
       
            while True:
                found_something = False
                for clause in clauses:
                    clause.update_state()
                    # push proposition from a unit clause on trail
                    if clause.state == Parser.CLAUSESTATE.UNIT:
                        found_something = True
                        self.trailstack.append(clause.missing_proposition)
                        clause.missing_proposition.set_decided(True)
                        clause.missing_proposition.assign(clause.implied_unitvalue)
                    elif clause.state == Parser.CLAUSESTATE.UNSATISFIED:
                        return False
                if found_something == False:
                    break
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

    class Implicationgraph:

        def __init__(self, default_value):
            self.default_value = default_value
            self.decisionlevel = 0    
            self.nodes_on_level = {'0': []}
            self.vertices = []
            # holds tuples with format: starting_node, target_node, clause_label
            self.edges = []
            self.last_assigned_prop = None
            self.conflicting_clauses = []
            self.asserting_clauses = []
            self.last_decision = None
        
        def cdcl_algorithm(self, clauses, proposition_list):
            if not self.BCP(clauses, proposition_list):
                return False
            while True:
                if not self.decide(clauses, proposition_list):
                    return get_current_assignment(proposition_list)    
                while not self.BCP(clauses, proposition_list):
                    if not self.resolve_conflict(clauses, proposition_list):
                        return False   

        def resolve_conflict(self, clauses, proposition_list):
            if self.decisionlevel == 0:
                return False

            self.update_asserting_clauses()

            # we want to reverse our last decision, because that decision created implications leading to current conflict
            for node in self.nodes_on_level[str(self.decisionlevel)]:
                #print(node)
                # also reset antecedent, since we solve exactly that conflict
                node.unassign(True)
                self.vertices.remove(node)

            for e in self.edges:
                if e[1] in self.nodes_on_level[str(self.decisionlevel)]:
                    self.edges.remove(e)

            self.nodes_on_level[str(self.decisionlevel)] = []
            self.decisionlevel -= 1

            # now create new clauses from asserting clauses and add those to our clause pool
            
            
            return True

        def update_asserting_clauses(self):
            # with current implementation, only one conflicting clause should exist at every point in time
            for cl in self.conflicting_clauses:
                nodes_in_clause = 0
                # all nodes on current level
                for n in self.nodes_on_level[str(self.decisionlevel)]:
                    if n in cl.neg_propositions:
                        nodes_in_clause += 1
                      
                      # todo: create new clauses and add them to our pool
                       # new_clause = 
                
                if nodes_in_clause ==1:
                    self.asserting_clauses.append(cl)
                    continue
                else:
                    for n in self.nodes_on_level[str(self.decisionlevel)]:
                        if n in cl.pos_propositions:
                            nodes_in_clause +=1
                if nodes_in_clause > 0:
                    self.asserting_clauses.append(cl)
            
         
                


        def label_node(self, node, value):
            if node not in self.vertices:
                self.vertices.append(node)
            node.set_label((value, self.decisionlevel))  

        # this function is very expensive. kind of O(n^2), we safe a bit, because we ignore mirrored connections.
        # trying to minimize the damage, by keeping track of new nodes and new unit clauses
        def update_edges(self, set_of_new_assignments, set_of_new_unit_clauses):
            for ind, new_n1 in enumerate(set_of_new_assignments):
                for new_n2 in set_of_new_assignments[ind:]:
                    if new_n1 != new_n2:
                        for antecedent_n2 in new_n2.antecedent:
                            if new_n1.value == 1:
                                if new_n1 in antecedent_n2.neg_propositions:
                                    self.edges.append((new_n1, new_n2, antecedent_n2))
                            elif new_n1.value == 0:
                                if new_n1 in antecedent_n2.pos_propositions:
                                    self.edges.append((new_n1, new_n2, antecedent_n2))

            # at this point, the new props are interconnected. Only thing to do is, find connections from old nodes,
            # and append the new nodes to the old_nodes_list

            for old_n1 in self.vertices:
                for new_n2 in set_of_new_assignments:
                    #should never be the case, but check anyways..
                    if old_n1 != new_n2:
                        for antecedent_n2 in new_n2.antecedent:
                            if old_n1.value == 1:
                                if old_n1 in antecedent_n2.neg_propositions:
                                    self.edges.append((old_n1, new_n2, antecedent_n2))
                            elif old_n1.value == 0:
                                if old_n1 in antecedent_n2.pos_propositions:
                                    self.edges.append((old_n1, new_n2, antecedent_n2))

            for new in set_of_new_assignments:
                self.vertices.append(new)


                        

        
        def decide(self, clauses, proposition_list):
            for prop in proposition_list:
                if prop.assigned == False and prop.decided == False:
                    prop.assign(self.default_value)
                    prop.set_decided(False)
                    self.last_assigned_prop = prop
                    # first increase decisionlevel. Like this the current decided value is always on a new level.
                
                    self.decisionlevel += 1
                    # create new index, and create list with prop in it.pass
                    # in the BCP function, we will append to this list
                    self.nodes_on_level[str(self.decisionlevel)] = [prop]
                    self.vertices.append(prop)
                    prop.set_label((self.default_value, self.decisionlevel))
                    self.last_decision = prop
                    return True
            
            for cl in clauses:
                cl.update_state()
            return False

        def BCP(self, clauses, proposition_list):
            # update all states, check immediately for the state. If it is unsatisfied, return False immediately
            while True:
                found_something = False
                set_of_new_assignments = []
                set_of_new_unit_clauses = []
                for clause in clauses:
                    clause.update_state()
                    # push proposition from a unit clause on trail
                    if clause.state == Parser.CLAUSESTATE.UNIT:
                        #update implicationgraph
                        found_something = True
                        clause.missing_proposition.set_decided(True)
                        clause.missing_proposition.assign(clause.implied_unitvalue)
                        
                        # instantly add the correct label for node
                        self.label_node(clause.missing_proposition, clause.implied_unitvalue )

                    
                        self.nodes_on_level[str(self.decisionlevel)].append(clause.missing_proposition)
                        # do not add to assigned vertices list yet, we will do this in the update edge function
                        # self.vertices.append(clause.missing_proposition)
                        # add to the set of assignments for one iteration over the clauses
                        set_of_new_assignments.append(clause.missing_proposition)
                        set_of_new_unit_clauses.append(clause)

                    elif clause.state == Parser.CLAUSESTATE.UNSATISFIED:
                        self.conflicting_clauses.append(clause)
                        return False
                
                self.update_edges(set_of_new_assignments, set_of_new_unit_clauses)
     

                if found_something == False:
                    break
            
            # only returns True, if there are no unsatisfied clauses
            return True

