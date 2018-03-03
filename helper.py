from cnfparser import Parser

def evaluate_clause(clause):
    negs = [i.value for i in clause.neg_propositions ]
    for neg_prop in clause.neg_propositions:
        if neg_prop.assigned == False:
            print(f'careful: {neg_prop} was not assigned')
            continue
        else:
            if neg_prop.value == 0:
                return True

    for pos_prop in clause.pos_propositions:
        if pos_prop.assigned == False:
        
           print(f'careful: {pos_prop} was not assigned')
           continue
        else:
            if pos_prop.value == 1:
                return True

    return False

def get_current_assignment(proposition_list):
    # create a nice readable dictionary
    res = {}
    for prop in proposition_list:
        if prop.assigned == True:
            identifier = 'X' + prop.identifier
            res[identifier] = prop.value
    
    return res

def clause_to_dict(clause):
    res = {}
    for props in clause.neg_propositions:
        name = 'X'+props.identifier + '_NEG'
        res[name] = props.value
        
    for props in clause.pos_propositions:
        name = 'X'+props.identifier+'_POS'
        res[name] = props.value

    print(res)
    return res

def prop_occurencetype_in_clause(clause, prop):
    res = []
    if prop in clause.pos_propositions:
        res.append(1)
    else:
        res.append(0)
    if prop in clause.neg_propositions:
        res.append(1)
    else:
        res.append(0)
    # returns (pos_occurences, neg_occurences)
    return res
