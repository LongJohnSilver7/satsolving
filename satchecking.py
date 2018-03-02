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
        self.propositions = [self.Proposition() for p in range(self.proposition_count)]

        # create useable clause objects for each clause we parsed from the cnf file
        self.clauses = [self.cnf_to_clause(self.propositions, c_as_str) for c_as_str in self.clauses_as_str]
        
    
    def _get_number_list_from_string(self, string_containing_numbers):
        return re.findall(r'[-]?\d+', string_containing_numbers)

    # creates a clause, mapping the corresponding propositions onto it    
    def cnf_to_clause(self, proposition_list, clause_as_string):
        l_propositions = self._get_number_list_from_string(clause_as_string)
        resulting_clause = self.Clause()
        for p in l_propositions:
            # iterating over every proposition
            if int(p) < 0:
                # proposition is negated:
                resulting_clause.add_neg_prop(proposition_list[abs(int(p))-1])
            if int(p) > 0:
                # proposition is not negated
                resulting_clause.add_pos_prop(proposition_list[int(p)-1])   
        
        return resulting_clause

    class Clause:
        pos_propositions = []
        neg_propositions = []
        propositions = []
        def __init__(self, *args):
            for proposition in args:
                self.propositions.append(proposition)
        
        def add_neg_prop(self, prop):
            self.neg_propositions.append(prop)
        
        def add_pos_prop(self, prop):
            self.pos_propositions.append(prop)
        
        #self.pos_propositions.append()
            

    class Proposition:
        value = None
        def __init__(self):
            self.value = None

        def assign(self, value):
            self.value = value

    






if __name__ == "__main__":
    cnf = Parser(os.path.abspath('pigeon_hole_6.cnf'))

    # cleanly obtain a list of propositions, that we can assign
    propositions = cnf.propositions
    # cleanly obtain a list of clause objects, where each clause reacts to an assignment we make for our propositions
    clauses = cnf.clauses

    print(cnf.propositions)
    print(cnf.clauses)