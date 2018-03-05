import os
import re
from enum import Enum
import time
class Parser:
    comments = []
    problem = []
    clauses_as_str = []
    numberoflines = 0
    #clauses = []
    #propositions = []

    proposition_count = None
    clause_count = None



    def __init__(self,filepath):
        with open(filepath) as f:
            lines = f.readlines()
        for id, l in enumerate(lines):
            lines[id] = l.strip('\n')

        linegenerator = self._g_pop(lines)
        self._parselines(linegenerator)

       
    
    '''
    returns list linewise
    ''' 
    def _g_pop(self, itemlist):
        num = len(itemlist)
        self.numberoflines = num
        #yield num
        for i in range(num):
            try:
                yield itemlist.pop(0)
            except Exception as exc:
                continue
        
    def _parselines(self, linegenerator):
        # get all clauses
        for k in linegenerator:
            try:
                if k[0] != 'c' and k[0] != 'p':
                    clause = k
                    if clause[-1] != '0':
                        #multiline clause
                        while clause[-1] != '0':
                            nl = next(linegenerator)
                            if nl[0] != 'c' and nl[0] != 'p':
                                sep = ' ' if clause[-1] != ' ' else ''
                                clause = clause + sep + nl  
                                # catch if a multiline is ending with x0, where x is any number
                                if clause[-2] != ' ':
                                    break
                            else:
                                print(f'Error while parsing multiline-clause for clause {nl}')
                                break
                       
                    clause = clause[:-1]
                    self.clauses_as_str.append(clause)
                elif k[0] == 'c':
                    
                    self.comments.append(k)
                elif k[0] == 'p':
                    self.problem.append(k)
                

            except Exception as exc:
                continue
        
        # get the number of clauses parsed by this unit. If it differs from the expected value, everything is over :(

        problem_parsed = self._get_number_list_from_string(self.problem[0])
        try:
            self.proposition_count = int(problem_parsed[0])
        except:
            print('Problem missing')

        # create number of neccessary propositions
        self.propositions = [self.Proposition(str(ind)) for ind,p in enumerate(range(self.proposition_count), 0)]
        

        # create useable clause objects for each clause we parsed from the cnf file
        self.clauses = [self.cnf_to_clause(self.propositions, c_as_str) for c_as_str in self.clauses_as_str]
        
        self.clause_count = len(self.clauses)

    
    def _get_number_list_from_string(self, string_containing_numbers):
        return re.findall(r'[-]?\d+', string_containing_numbers)

    # creates a clause, mapping the corresponding propositions onto it    
    def cnf_to_clause(self, proposition_list, clause_as_string):
        l_propositions = self._get_number_list_from_string(clause_as_string)
        resulting_clause = Parser.Clause()

        for p in l_propositions:
            # iterating over every proposition
            ind = None
            if int(p) < 0:
                # proposition is negated:
                ind = abs(int(p))-1
                resulting_clause.add_neg_prop(proposition_list[ind])
            if int(p) > 0:
                
                ind = int(p)-1
                # proposition is not negated
                resulting_clause.add_pos_prop(proposition_list[ind])   

        

        
        resulting_clause.propositions =  resulting_clause.pos_propositions + resulting_clause.neg_propositions
        



        return resulting_clause

    class CLAUSESTATE(Enum):
        SATISFIED = 1
        UNSATISFIED = 2
        UNRESOLVED = 3
        UNIT = 4


    '''
    Careful: missing_proposition just points to any unassigned proposition. Always check state for unit, when checking for unit
    '''
    class Clause:

        def __init__(self, *args):
            self.id = None
            self.proposition_count = 0
            self.pos_propositions = []
            self.neg_propositions = []
            self.propositions = []
            self.state = Parser.CLAUSESTATE.UNRESOLVED
            self.missing_proposition = None
            self.implied_unitvalue = None
            self.flag = False
            self.current_watches = []
            self.assigned_watches = []

            #for proposition in args:
                #self.propositions.append(proposition)
                #self.proposition_count += 1
            #self._calculate_state()
        
        def set_id(self, newid):
            self.id = newid

        def set_flag(self, value):
            self.flag = value

        def add_neg_prop(self, prop):
            self.neg_propositions.append(prop)
            self.propositions.append(prop)
            prop.contained_in_clauses.append(self)
            self.proposition_count += 1
            self._calculate_state
        
        def add_pos_prop(self, prop):
            self.pos_propositions.append(prop)
            self.propositions.append(prop)
            prop.contained_in_clauses.append(self)
            self.proposition_count += 1
            self._calculate_state()




        def _check_neg_for_literal(self, literal):
            if literal in self.neg_propositions:
                return True
            else:
                return False

        def _check_pos_for_literal(self, literal):
            if literal in self.pos_propositions:
                return True
            else:
                return False

        #def _get_new_watch(self):

        def _search_watch(self, current_watches):
            already_known_watch = None
            for prop in self.neg_propositions:
                if prop.assigned == False:
                    if prop not in self.current_watches:
                        return prop
                    else:
                        already_known_watch = prop
            
            for prop in self.pos_propositions:
                if prop.assigned == False:
                    if prop not in self.current_watches:
                        return prop
                    else:
                        already_known_watch = prop

            return already_known_watch
        
        def update_state(self, watchlist = None):
            self._calculate_state(watchlist)

        def _calculate_state(self, watchlist = None):
            if watchlist is None:
                self._calculate_state_nowl()
                return
            
            # we are using a watchlist, which means we only check literals in the given watchlist
            watches = watchlist.watchlist[self.id]
            counter_watches = len(watches)
            found_assigned = 0
            
            if counter_watches == 0:
                print('error, no watches for this clause')
                return

            # trick: we know literal that was decided and forced this function call is in this clause, so we only need to check neg or pos literal list to check for satisfied
            # if we do not hit it, in the correct list, we still obtain information about it
            # while iterating over this: remember a possible literal that we can add to our watchlist

         
            unassigned_literal = None
            unassigned_literal_neg = None
            unassigned_literal_pos = None
            print(f'-------------------------------------------------------------------')
            print(f'Start iterating over watchlist for clause {self}')
            print(f'Clause contains propositions: {self.propositions}')
            print(f'Clause contains watches: {self.current_watches}')
            for ind_outer, watch in enumerate(watches):
                print(f'########## Checking watch: {watch}')
                indicator_clause_true = False

                # remember one unassigned literal, if there was one
 
                if watch.assigned == True:
                    print(f'Found an assigned watch while checking watches: {watch}. Value is: {watch.value}')
                    print(self.propositions)
                    # we reach here, if we assigned a watch. Note: Only one watch can be assigned per call of this function
                    # kind of useless probably. Only adds literals that were watches. Well whatever, maybe it becomes useful later on
                    self.assigned_watches.append(watch)
                    #print(f'current lit value: {literal.value}')
                    if watch.value == 0:
                        for ind, neg_lit in enumerate(self.neg_propositions):
                            if neg_lit == watch:
                                print('check2')
                                print(f'removing watch: {neg_lit}')
                                print(f'from: {self.current_watches}')
                                del watchlist.watchlist[self.id][ind_outer]
                                print(f'result: {watchlist.watchlist[self.id]}')
                                print(f'{self.current_watches}')
                                self.state = Parser.CLAUSESTATE.SATISFIED
                                indicator_clause_true == True
                                return

                    elif watch.value == 1:
                        for ind, pos_lit in enumerate(self.pos_propositions):
                            if pos_lit == watch:
                                print(f'check {ind_outer}')
                                print(f'removing watch: {pos_lit}')
                                print(f'from: {self.current_watches}')
                                del watchlist.watchlist[self.id][ind_outer]
                                print(f'result: {watchlist.watchlist[self.id]}')
                                print(f'{self.current_watches}')
                                self.state = Parser.CLAUSESTATE.SATISFIED
                                indicator_clause_true == True
                                return

                    
                    if indicator_clause_true == False:   
                        print(f'Clause was not satisfied by watch. Remove watch with index {ind_outer} from Watchlist. Other watch is guaranteed to still be unassigned')
                        print(f'Propositions in this clause are: {self.propositions}')
                        print(self.current_watches)
                        print(ind_outer)
                        del watchlist.watchlist[self.id][ind_outer]
                        #print(self.current_watches)
                        #del self.current_watches[ind]
         
                    
                        # we did not get a satisfied clause from the assignment of our watch, so the clause is still 
                        # unresolved, a unit, or there was only one watch to begin with
                        new_watch = self._search_watch(watchlist.watchlist[self.id])
                        print(f'Searching a new watch yielded result: {new_watch}' )
                        if new_watch is not None and new_watch not in watchlist.watchlist[self.id]:
                            # append it to our watchlist
                            watchlist.watchlist[self.id].append(new_watch)
                        else:
                            self.missing_proposition = new_watch
                            if new_watch in self.pos_propositions:
                                self.implied_unitvalue = 1
                            else:
                                self.implied_unitvalue = 0

                        print(f'Updated Watchlist: {self.current_watches}')
                        if len(watchlist.watchlist[self.id]) == 1:
                            self.state = Parser.CLAUSESTATE.UNIT
                            print(f'Only one watch and no other unassigned variable. Conclusion: UNIT')
                      
                            
                        if len(watchlist.watchlist[self.id]) == 2:   
                            # we again have 2 watches, both being unassigned 
                            self.state = Parser.CLAUSESTATE.UNRESOLVED
                    # found an assigned watch. No need to continue
                    break
                        

            

            
            

        def _calculate_state_nowl(self):
            if not self.neg_propositions and not self.pos_propositions:
                return
            #print(f'state at beginning of update function: {self.state}')
            found_unassigned = False

            #print(self.neg_propositions)
            for prop in self.neg_propositions:
                if prop.value == 0:
                    self.state = Parser.CLAUSESTATE.SATISFIED
                    #print(f'state at end of update function: {self.state}')
                    return
                elif prop.assigned == False:
                    if found_unassigned == False:
                        found_unassigned = True
                        self.missing_proposition = prop
                        self.implied_unitvalue = 0
                    else:
                        # found a second unassigned literal
                        self.state = Parser.CLAUSESTATE.UNRESOLVED
                        return
 
            for prop in self.pos_propositions:
                #print(prop.value)
                if prop.value == 1:
                    self.state = Parser.CLAUSESTATE.SATISFIED
                    #print(f'state at end of update function: {self.state}')
                    return
                elif prop.assigned == False:
                    if found_unassigned == False:
                        found_unassigned = True
                        self.missing_proposition = prop
                        self.implied_unitvalue = 1
                    else:
                        # found a second unassigned literal
                        self.state = Parser.CLAUSESTATE.UNRESOLVED
                        return
            # we reached here. So we either found one unassigned proposition or the clause is unsatisfied
            
            if found_unassigned == True:
                self.state = Parser.CLAUSESTATE.UNIT
                # code the antecedent, maybe not so clean, because classes interact with each other in the background
                self.missing_proposition.antecedent.append(self)
            else:

                self.state = Parser.CLAUSESTATE.UNSATISFIED

            #print(f'state at end of update function: {self.state}')
            




        
        #self.pos_propositions.append()
            

    class Proposition:
        #value = None
        #assigned = False
        #value_not_flippable = False
        #identifier = None

        def __init__(self, identifier=None):
            self.value = None
            self.assigned = False
            self.value_not_flippable = False
            self.decided = False
            self.antecedent = []
            self.label = None
            self.contained_in_clauses = []
            if identifier is not None:
                self.identifier = identifier

        def set_label(self, label):
            self.label = label

        def remove_label(self, value, decisionlevel):
            self.label = None

        def assign(self, value, b=False, antecedent_reset = False):
            self.value = value
            self.assigned = True
            self.value_not_flippable = b
            if antecedent_reset == True:
                self.antecedent = []
        
        def unassign(self, antecedent_reset = False):
            self.value = None
            self.assigned = False
            self.value_not_flippable = False
            self.set_decided(False)
            if antecedent_reset == True:
                self.antecedent = []
       
        def set_flippable(self, b):
            self.value_not_flippable = not b

        def is_flippable(self):
            return not self.value_not_flippable

        def remove_antecedent(self, clause):
            try:
                self.antecedent.remove(clause)
            except:
                pass

        def flip(self, b=False):
            if self.assigned == True:
                if self.value == 0:
                    self.assigned = True
                    self.value = 1
                    return
                if self.value == 1:
                    self.assigned = True
                    self.value = 0
                    return
        
        def set_decided(self, b):
            self.decided = b




    






if __name__ == "__main__":
    cnf = Parser(os.path.abspath('test.cnf'))

    # cleanly obtain a list of propositions, that we can assign
    propositions = cnf.propositions
    # cleanly obtain a list of clause objects, where each clause reacts to an assignment we make for our propositions
    clauses = cnf.clauses
    print('done')