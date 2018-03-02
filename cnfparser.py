import os
import re

class Parser:
    comments = []
    problem = []
    clauses_as_str = []
    numberoflines = 0
    clauses = []
    propositions = []

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
        self.clause_count = len(self.clauses)
        problem_parsed = self._get_number_list_from_string(self.problem[0])
        try:
            self.proposition_count = int(problem_parsed[0])
        except:
            print('Problem missing')


        # create number of neccessary propositions
        self.propositions = [self.Proposition(str(ind)) for ind,p in enumerate(range(self.proposition_count), 0)]
        

        # create useable clause objects for each clause we parsed from the cnf file
        self.clauses = [self.cnf_to_clause(self.propositions, c_as_str) for c_as_str in self.clauses_as_str]
        #collection = []
        #for c_as_str in self.clauses_as_str:

        #    collection.append(Parser.cnf_to_clause(self, self.propositions, c_as_str))
        
        #print(f'collection is this: {collection}')
    
    def _get_number_list_from_string(self, string_containing_numbers):
        return re.findall(r'[-]?\d+', string_containing_numbers)

    # creates a clause, mapping the corresponding propositions onto it    
    def cnf_to_clause(self, proposition_list, clause_as_string):
        print('starting function to sort the propositions in neg and pos lists')
        l_propositions = self._get_number_list_from_string(clause_as_string)
        print(l_propositions)
        
        resulting_clause = Parser.Clause()
        print('these should be empty')
        print(resulting_clause.neg_propositions)
        print(resulting_clause.pos_propositions)
        for p in l_propositions:
            print(int(p))
            # iterating over every proposition
            if int(p) < 0:
                # proposition is negated:
                print('prop is put in negative list')
                resulting_clause.add_neg_prop(proposition_list[abs(int(p))-1])
            if int(p) > 0:
                # proposition is not negated
                resulting_clause.add_pos_prop(proposition_list[int(p)-1])   
        
        print(resulting_clause.neg_propositions)
        print(resulting_clause.pos_propositions)
        print('clause should function at this point')
        return resulting_clause

    class Clause:

        def __init__(self, *args):
            self.pos_propositions = []
            self.neg_propositions = []
            self.propositions = []
            for proposition in args:
                self.propositions.append(proposition)
        
        def add_neg_prop(self, prop):
            self.neg_propositions.append(prop)
        
        def add_pos_prop(self, prop):
            self.pos_propositions.append(prop)
        
        #self.pos_propositions.append()
            

    class Proposition:
        value = None
        assigned = False
        value_not_flippable = False
        identifier = None
        def __init__(self, identifier=None):
            self.value = None
            self.assigned = False
            self.value_not_flippable = False
            if identifier is not None:
                self.identifier = identifier

        def assign(self, value, b=False):
            self.value = value
            self.assigned = True
            self.value_not_flippable = b
        
        def unassign(self):
            self.value = None
            self.assigned = False
            self.value_not_flippable = False
       
        def set_flippable(self, b):
            self.value_not_flippable = not b

        def is_flippable(self):
            return not self.value_not_flippable
        
        def flip(self, b=False):
            if self.assigned == True:
                if self.value == 0:
                    self.value = 1
                    return
                if self.value == 1:
                    self.value = 0
                    return




    






if __name__ == "__main__":
    cnf = Parser(os.path.abspath('test.cnf'))

    # cleanly obtain a list of propositions, that we can assign
    propositions = cnf.propositions
    # cleanly obtain a list of clause objects, where each clause reacts to an assignment we make for our propositions
    clauses = cnf.clauses