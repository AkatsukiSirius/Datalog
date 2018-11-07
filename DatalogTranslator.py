# Tables
# Table 1: product, columns: "Product","Price"
# Table 2: madein , columns: "Product", "Country"
tables = ["madein", "price"]
productCol = ["Product","Price"]
madeinCol = ["Product", "Country"]
tabCol = {tables[0]:madeinCol, tables[1]:productCol}

# Constants
countries = ["germany","belgium","uk"]
prices = ["5"]

consDict = {"Country":countries,  "Price": prices}

# Datalog query to translate
datalog_goodProd = "good_product(Product):-madein(Product,germany).good_product(Product):-madein(Product,belgium)."

datalog_badProd = "bad_product(Product):-madein(Product,Country), Country!=germany, Country!=belgium, Country!=uk."

datalog_perfProd = "perfect_product(Product):-good_product(Product), not bad_product(belgium), price(Product,Price), Price<5."

# Seperators
sep1 = '.'
sep2 = ':-'
sep3 = ', '
cmps = ["!=",">","<","<=",">=","=="]

# Functions to clean the datalog query
def getClauses(datalog_query):
    return [item for item in datalog_query.split(sep1) if item != '']

def getHeads(datalog_query):
    clauses = getClauses(datalog_query)
    return [clause.split(sep2)[0] for clause in clauses]

def getAllPredicates(datalog_query):
    return [head.split('(')[0] for head in getHeads(datalog_query)]

def getVariablesInHeads(datalog_query):
    heads = getHeads(datalog_query)
    query = []
    for head in heads:
        query += [q.strip() for q in head[head.find("(")+1:head.find(")")].split(',')]
    return query

def getBodies(datalog_query):
    clauses = getClauses(datalog_query)
    return [clause.split(sep2)[1] for clause in clauses]


def getHBDict(datalog_query):
    result = {}
    clauses = getClauses(datalog_query)
    i = 1
    for clause in clauses:
        result["Clause"+str(i)] = clause.split(sep2)[0]+sep2+clause.split(sep2)[1]
        i += 1
    return result

def getTotalPredicates(datalog_query):
    result = []
    for body in getBodies(datalog_query):
        for term in body.split(', '):
            result.append(term)
    for head in getHeads(datalog_query):
        result.append(head)
    return result

def getLiteralHeadDict(datalog_query):
    bH = getHBDict(datalog_query)
    result = {}
    for key in bH.keys():
        if len(key.split(sep3))>1:
            for term in key.split(sep3):
                result[term] = bH[key]
        else:
            result[key.split(sep3)[0]] = bH[key]
    return result


def getVariablesInBodies(datalog_query):
    query = []
    for body in getHBDict(datalog_query).keys():
        for term in body.split(', '):
            if term.find("(") != -1:
                query += [q.strip() for q in term[term.find("(")+1:term.find(")")].split(',')]
            else:
                for cmp in cmps:
                    if term.find(cmp) != -1:
                        query.append(term.split(cmp)[0])
                        query.append(term.split(cmp)[1])
    return query

def getVariablesInClauses(datalog_query):
    query = []
    for body in getHBDict(datalog_query).keys():
        for term in body.split(', '):
            if term.find("(") != -1:
                query += [q.strip() for q in term[term.find("(")+1:term.find(")")].split(',')]
            else:
                for cmp in cmps:
                    if term.find(cmp) != -1:
                        query.append(term.split(cmp)[0])
                        query.append(term.split(cmp)[1])
    for body in getHBDict(datalog_query).values():
        for term in body.split(', '):
            if term.find("(") != -1:
                query += [q.strip() for q in term[term.find("(")+1:term.find(")")].split(',')]
            else:
                for cmp in cmps:
                    if term.find(cmp) != -1:
                        query.append(term.split(cmp)[0])
                        query.append(term.split(cmp)[1])
    return query

def getPVDict(datalog_query):
    '''
    :type string: datalog query to translate
    :rtype dictonary: constant - new predicate pair
    '''
    predConsDict = {}
    i = 1
    for var in getVariablesInClauses(datalog_query):
        for ls in consDict.values():
            if var in ls:
                if var in predConsDict.keys():
                    continue
                else:
                    predConsDict[var] = 'P'+str(i)
                    i = i + 1
    return predConsDict

def generateNewPred4Const(pvDict):
    '''
    :type dictionary: pvDict
    :rtype dictonary: newPredicates
    '''
    newPredicates = []
    for key in pvDict.keys():
        newPredicates.append(pvDict[key]+'='+'{('+key+')};')
    return newPredicates

def generateConstList(consDict):
    '''
    :type dictionary:consDict
    :rtype consts: constant list
    '''
    consts = []
    for key in consDict.keys():
        consts+=consDict[key]
    return consts

# Step 1. Generate new predicates for variables, replace
def replaceConstInDLClauses(bH, consts,pvDict):
    '''
    :type dictionary: bH
    :type list: constants in original datalog query
    :type dictionary: constant - new Predicate pairs
    :rtype dictionary: newDict
    '''
    newDict = {}
    for key in bH.keys():
        i = 1
        clause = bH[key]
        for const in consts:
            if clause.find(const) != -1:
                variable = "v" + str(i)
                clause = clause.replace(const,variable)
                add = ", " + pvDict[const] + "(" + variable + ")"
                temp = clause + add
                i = i + 1
        newDict[key] = temp
    return newDict


inp = datalog_goodProd+datalog_badProd+datalog_perfProd
pvDict = getPVDict(inp)
bH = getHBDict(inp)
newPredicates = generateNewPred4Const(pvDict)
consts = generateConstList(consDict)

newDict = replaceConstInDLClauses(bH, consts,pvDict)

# Step 2. Combine the Multiple-Clause Predicate Definitions

def combineMultiClausePredicate(newDict):
    '''
    type dictionary: clause pair
    rtype dictionary: new predicates
    '''
    # Find duplicate rules
    predCount = {}
    duplicatePred = []
    for key in newDict.keys():
        a = newDict[key].split(':')[0]
        b = a.split('(')[0]
        if b in predCount:
            duplicatePred.append(b)
            predCount[b] += 1
        else:
            predCount[b] = 1

    # get each predicate in duplicate rule just found
    i = len(pvDict) + 1
    newPredicate3 = {}
    for key in newDict.keys():
        a = newDict[key].split(':')[0]
        b = a.split('(')[0]
        newPredicate3[b] = ''

    # combine the duplicate rules and generate new predicate
    for key in newDict.keys():
        a = newDict[key].split(':')[0]
        b = a.split('(')[0]
        if predCount[b] > 1:
            newDict[key] = newDict[key].replace(b, 'P' + str(i))
            newPredicate3[b] += 'P' + str(i) + ' logicAnd '
            i += 1

    newPredicate3Cleard = {}
    for key in newPredicate3.keys():
        if newPredicate3[key] != '':
            newPredicate3Cleard[key] = newPredicate3[key].strip('logicAnd ')

    return newPredicate3Cleard

# Step 3.

# Python code to merge dict using a single
# expression
def MergeDicts(dict1, dict2):
    res = {**dict1, **dict2}
    return res


def renameVariableInClauses(newDict):
    results = ''
    # Count variables in head
    for key in newDict.keys():
        head = newDict[key].split(':-')[0]
        body = newDict[key].split(':-')[1]
        # get each term in body
        predicates = body.split(', ')

        bvPreds = []
        bvEqs = []
        bvNegPreds = []
        for predicate in predicates:
            if predicate.find("not ") != -1:
                bvNegPreds.append(predicate)
            elif predicate.find("(") != -1:
                bvPreds.append(predicate)
            else:
                bvEqs.append(predicate)

        # First, deal with the variables in positive predicate
        i = 1
        btDict = {}
        for bvPred in bvPreds:
            terms = bvPred[bvPred.find("(") + 1:bvPred.find(")")].split(',')
            terms = [term for term in terms if term != '']
            for term in terms:
                btDict['x' + str(i)] = term
                i += 1
        # Generate additional predicate
        a = {}
        newEq = ''
        for item in btDict.items():
            if item[1] in a:
                newEq += a[item[1]] + '==' + item[0] + ', '
            else:
                a[item[1]] = item[0]

        newBody = ''
        btDict4Mapping = btDict
        # use an other variable when same term appears in another prediacate
        usedVars = []
        for bvPred in bvPreds:
            newPred = bvPred
            for variable in btDict4Mapping.keys():
                if newPred.find(btDict4Mapping[variable]) != -1:
                    if variable not in usedVars:
                        newPred = newPred.replace(btDict4Mapping[variable], variable)
                        usedVars.append(variable)
            newBody += newPred + ', '
        newBody = newBody + newEq

        # Second, deal with varibles in Eq
        # Create additional variables in pre-defined predicates

        # List Variables in pre-defined predicates
        varInIneq = []
        for bvEq in bvEqs:
            for cmp in cmps:
                if bvEq.find(cmp) != -1:
                    varInIneq.extend(bvEq.split(cmp))
        varInIneq = sorted(list(set(varInIneq)))
        newVarFlag = len(btDict)

        # Create dictionaries for new variables
        varDict4Ineq = {}
        for variable in varInIneq:
            if variable not in btDict.values():
                varDict4Ineq['x' + str(newVarFlag + 1)] = variable
                newVarFlag += 1

        btDict = MergeDicts(btDict, varDict4Ineq)
        newbvEqs = []
        for bvEq in bvEqs:
            newbvEq = bvEq
            for variable, bt in btDict.items():
                if newbvEq.find(bt) != -1:
                    newbvEq = newbvEq.replace(bt, variable)
            newbvEqs.append(newbvEq)

        for newbvEq in newbvEqs:
            newBody += newbvEq + ', '

        # Third, deal with variables in negated predicate
        newbvNegPreds = []
        for bvNegPred in bvNegPreds:
            newbvNegPred = bvNegPred
            for variable, bt in btDict.items():
                if bvNegPred.find(bt) != -1:
                    newbvNegPred = newbvNegPred.replace(bt, variable)
            newbvNegPreds.append(newbvNegPred)

        for newbvNegPred in newbvNegPreds:
            newBody += newbvNegPred + ', '

        newBody = newBody.strip(', ')

        newHead = head
        for variable in btDict.keys():
            if head.find(btDict[variable]) != -1:
                newHead = newHead.replace(btDict[variable], variable)

        newClause = newHead + ":-" + newBody
        results += newClause + '.'
    return results

newDict1 = newDict
rr = renameVariableInClauses(newDict1)
print(rr)