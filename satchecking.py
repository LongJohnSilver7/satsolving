import os
import re

class Parser:
    comments = []
    problem = []
    clauses = []
    numberoflines = 0


    def __init__(self,filepath):
        with open(filepath) as f:
            lines = f.readlines()
        for id, l in enumerate(lines):
            lines[id] = l.strip('\n')

        linegenerator = self.g_pop(lines)
        self.parselines(linegenerator)


    
    '''
    returns list linewise
    ''' 
    def g_pop(self, itemlist):
        num = len(itemlist)
        self.numberoflines = num
        #yield num
        for i in range(num):
            try:
                yield itemlist.pop(0)
            except Exception as exc:
                print(exc)
        
    def parselines(self, linegenerator):
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
                    self.clauses.append(clause)
                elif k[0] == 'c':
                    
                    self.comments.append(k)
                elif k[0] == 'p':
                    self.problem.append(k)
                

            except Exception as exc:
               continue
        




if __name__ == "__main__":
   # li = [i for i in range(0)]
   # print(li)
    cnf = Parser(os.path.abspath('pigeon_hole_6.cnf'))
    print(cnf.clauses)
