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
            self.watches_at_last_decision = []
    

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
        
        def _check_satisfied(self):
            for p in self.pos_propositions:
                #print(p.value)
                if p.value == 1:
                    return True
            
            for p in self.neg_propositions:
                if p.value == 0:
                    return True
            
            return False
        def _fill_watches(self):
            #print('filling watches')
            for lit in self.propositions:
                if len(self.current_watches)==2:
                    return
                if lit.assigned == False:
                    if lit not in self.current_watches:
                        self.current_watches.append(lit)

        def _calculate_state(self, watchlist = None):
            if watchlist is None:
                self._calculate_state_nowl()
                return
            #print('watches before filling:')
            #print(self.current_watches)
            # obtain new watches
            #print('FILLING WATCHES')
            self._fill_watches()
            # find newly assigned watches since last update, save old ones
            previous_watches = self.current_watches[:]
            print(f'Update Clause: {int(self.id)+1}')
            #print(f'Propositions: {n.identifier for n in self.propositions}')
            #print(f'Previous Watches: {previous_watches}')
            
            b_satisfied = False
            #print(f'neg prop: {self.neg_propositions}')
            #print(f'pos prop: {self.pos_propositions}')
            
            for prev in self.current_watches:
               # print(f'item: {prev}')
               # print(f'value: {prev.value}')
              #  print(f'assigned: {prev.assigned}')

                if prev.value == 0:
                    if prev in self.neg_propositions:
                      #  print('found sat in neg list')
                        b_satisfied = True
                elif prev.value == 1: 
                    if prev in self.pos_propositions:
                      #  print('found sat in pos list')
                        b_satisfied = True

            #if previous watch assignement made clause satisfied, return immediately
            if b_satisfied == True:
                print('SATISFIED')
                self.state = Parser.CLAUSESTATE.SATISFIED
                return

            self.assigned_watches = []
            for watch in self.current_watches:
                if watch.assigned == True:
                    self.assigned_watches.append(watch)
            
            # remove newly assigned watches from watchlist
            for watch in self.assigned_watches:
                self.current_watches.remove(watch)

 
           # obtain new watches
            self._fill_watches()
           # print(f'New watches: {self.current_watches}')
            
            watchcount = len(self.current_watches)
            
       
            

            
            if  watchcount == 0:
                # could have backtracked to here, and some implicated values trashed our current watches. We have to check for satisfied here
                # this if fixable by updating the watches_at_last_decision attribute when deciding a variable.

                if self._check_satisfied() == False:
                    self.state = Parser.CLAUSESTATE.UNSATISFIED
                    print('UNSATISFIED')
                else:
                    self.state = Parser.CLAUSESTATE.SATISFIED
                    print('entered satisfied branch')
                return

            elif watchcount == 1:
                if self._check_satisfied() == True:
                    self.state = Parser.CLAUSESTATE.SATISFIED
                    print('entered satisfied branch')
                    return
                
                self.state = Parser.CLAUSESTATE.UNIT
                print('UNIT')
                #print(self.current_watches)
            
                self.missing_proposition = self.current_watches[0]
                print(f'missing proposition: {int(self.missing_proposition.identifier)+1}')    
                
                if self.missing_proposition in self.pos_propositions:
                    self.implied_unitvalue = 1
                else:
                    self.implied_unitvalue = 0
                self.missing_proposition.antecedent = self
            elif watchcount == 2:
                self.state = Parser.CLAUSESTATE.UNRESOLVED
                print('UNRESOLVED')

             

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