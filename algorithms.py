from cnfparser import Parser
from helper import evaluate_clause, get_current_assignment, clause_to_dict, prop_occurencetype_in_clause, ID_GEN
import os
import time
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

class WATCHLIST:

    def __init__(self, clauses, idgen, watch_heuristic = None):
        # create a list of unique id's for each clause
        self.idgen = idgen
        self.watchlist = {}
        self.heuristic = watch_heuristic


        if self.heuristic is None:
            # no elaborate heuristic: take first two propositions
            print('Using standard watchlistheuristic')
            self.heuristic = self.default_heuristic

        for cl in clauses:
            # generate and set new id for clause
            clauseid = str(next(self.idgen.uniqueID()))
            cl.set_id(clauseid)
            
            # set watches for clause
            if clauseid in self.watchlist:
                self.watchlist[clauseid].append(self.heuristic(cl))
                
            else:
                self.watchlist[clauseid] = self.heuristic(cl) 
                # connect clauses current watches with our watchlist:
                cl.current_watches = self.watchlist[clauseid]



    def default_heuristic(self,clause):
        reslist = []
        for prop in clause.propositions:
            # greedily add unassigned literals
            if prop.assigned == False:
                reslist.append(prop)
            if len(reslist)==2:
                break

        return reslist
        

    # in case we create a new clause, append it to our watchlist
    def append_clause(self, clause):

        if clause.id is not None:
            if clause.id in self.watchlist:
                if self.watchlist[clause.id] != []:
                    print(f'clause already has a nonempty watchlist')
                else:
                    self.watchlist[clause.id].append(self.heuristic(clause))
            else:
                clauseid = str(next(self.idgen.uniqueID()))
                cl.set_id(clauseid)
                self.watchlist[clause.id] = self.heuristic(clause)
        else:
           # generate and set new id for clause
            clauseid = str(next(self.idgen.uniqueID()))
            cl.set_id(clauseid)
            # set watches for clause
            self.watchlist[clauseid] = self.heuristic(clause) 

        


# davis-putnam-logemann-loveland algorithms
class DPLL:


    def __init__(self):
        pass


    class Backtracking:
        
        def __init__(self, default_value, clauses, propositions, idgen, wl_algorithm=None):
            self.default_value = default_value
            self.trailstack = []
            self.clauses = clauses
            self.proposition_list = propositions
            self.idgen = idgen
            self.unitclauses = []
            self.last_set_literal = None

    
            self.watchlist = WATCHLIST(clauses, idgen, wl_algorithm)
            self.use_watchlist = False
            #print('Complete watchlist:')
            #print(self.watchlist.watchlist)

        def dpll_algorithm(self, use_watchlist = False):
            if use_watchlist == True:
                self.use_watchlist = True
            
            self.trailstack = []
            if not self.BCP(self.clauses, self.proposition_list):
                return False
            while True:
                if not self.decide(self.clauses, self.proposition_list):
                    return get_current_assignment(self.proposition_list)    
                while not self.BCP(self.clauses, self.proposition_list):
                    if not self.backtrack(self.clauses, self.proposition_list):
                        return False

        def BCP(self, clauses, proposition_list):
            
            
            # update all states, check immediately for the state. If it is unsatisfied, return False immediately

            print('=================================================================================')
            # this is ugly... will be called for every BCP call, but this if is only for the first call.. fix it at some point
            if self.last_set_literal is None:
                aggregated_literals = []
            else:
                aggregated_literals = [self.last_set_literal]
            
            #print(aggregated_literals)
            print(f'Propagating Constraints based on following assigned or implicated literals: {aggregated_literals}')
            while len(aggregated_literals)>0:
                
                cur_literal = aggregated_literals.pop()
        

                # get set of clauses that might change their status
                #print(cur_literal)
                clause_subset = cur_literal.contained_in_clauses
                #print(clause_subset)
                print(f'Following classes contain the literal: {clause_subset}')
                for clause in clause_subset:
                    
                    if self.use_watchlist == True:
                        clause.update_state(self.watchlist)
                    else:
                        clause.update_state()

                    # push proposition from a unit clause on trail
                    if clause.state == Parser.CLAUSESTATE.UNIT:
                        found_something = True
                        self.trailstack.append(clause.missing_proposition)
                        clause.missing_proposition.set_decided(True)
                        clause.missing_proposition.assign(clause.implied_unitvalue)
                        
                        aggregated_literals.append(clause.missing_proposition)
                        print(f'Implication for {clause.missing_proposition} by new Unit {clause}')

                    elif clause.state == Parser.CLAUSESTATE.UNSATISFIED:
                        print(f'Contradiction for clause: {clause}')
                        print(f'Current watches: {clause.current_watches}')
                        print(f'assigned watches: {clause.assigned_watches}')
                        return False
                        
            # only returns True, if there are no unsatisfied clauses
            print(f'No new implications, and no unsatisfied clauses for BCP.')
           # time.sleep(10)
            return True


        def decide(self,clauses, proposition_list):
            for prop in proposition_list:
                if prop.assigned == False and prop.decided == False:
                    prop.assign(self.default_value)
                    prop.set_decided(False)
                    self.trailstack.append(prop)
                    self.last_set_literal = prop
                    print(f'we decided {prop} with value {self.default_value}')
                    return True
            
            # no decision was possible. At this point we update clause states once more. to get an up to date representation of our solution or the unsatisfied state
            for cl in clauses:
                if self.use_watchlist == True:
                    cl.update_state(self.watchlist)
                else:
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
                    self.last_set_literal = prop_from_unit
                    print(f'backtracked to {prop_from_unit}')
                    print(f'Decision was changed to {prop_from_unit.value} ')
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

