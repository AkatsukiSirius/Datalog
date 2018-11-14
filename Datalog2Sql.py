import re

def getClauses(datalog_query):
    '''
    Description: Seperate each clause by character '.'
    type string: datalog_query
    rtype list
    '''
    return [item for item in datalog_query.split('.') if item != '']

def seperateHeadBody(clause):
    '''
    Description: get head and body for each clause
    type string: clauses
    rtype list
    '''
    head = clause.split(':-')[0]
    body = clause.split(':-')[1]
    return head,body

def getTermsInParens(a):
    '''
    Description: get each term in parentheses
    type string: a
    rtype list: results
    '''
    results = []
    if a.find('(') != -1 and a.find(')') != -1:
        terms = a[a.find("(")+1:a.find(")")].split(',')
        for term in terms:
            results.append(term)
    return results

def getColsFromHead(head):
    cols = getTermsInParens(head)
    return cols

def getPredPerTerm(term):
    predicate = ''
    if term.find('(') != -1 and term.find(')') != -1:
        predicate = term.split('(')[0]
    return predicate

def getTabsPerBody(body):
    tabs = []
    bodyLiterals = body.split(', ')
    for bodyLiteral in bodyLiterals:
        if bodyLiteral.find('(') != -1 and bodyLiteral.find(')') != -1:
            predicate = bodyLiteral.split('(')[0]
            tabs.append(predicate)
    return tabs

def getSchemaDict(inputSchemas):
    '''
    Description: Create a dictionary for schemas
    type list: inputSchemas
    rtype dictionary
    '''
    schemaDict = {}
    for schema in inputSchemas:
        pred = getPredPerTerm(schema)
        if pred in schemaDict:
            schemaDict[pred] += getTermsInParens(schema)
        else:
            schemaDict[pred] = getTermsInParens(schema)
    return schemaDict

def getBodyDict(body):
    '''
    Description: create a dictionary to contain predicate-term pair
    type string: body
    rtype dict: bodyDict
    '''
    bodyDict = {}
    bodyLiterals = body.split(', ')
    for bodyLiteral in bodyLiterals:
        if bodyLiteral.find('(') != -1 and bodyLiteral.find(')') != -1:
            predicate = bodyLiteral.split('(')[0]
            bodyDict[predicate] = bodyLiteral[bodyLiteral.find('(')+1:bodyLiteral.find(')')].split(',')
        else:
            bodyDict[bodyLiteral] = bodyLiteral
    return bodyDict

def getSelectQuery(cols, bodyDict):
    '''
    Description: generate clause
    type list[string]: cols
    type dict: bodyDict
    rtype string: selectCaluse
    '''
    selectClause = 'select '
    for col in cols:
        for pred in bodyDict.keys():
            if col in bodyDict[pred]:
                selectClause += pred + '.' + col + ', '
                break
    selectClause = selectClause.strip(', ')
    return selectClause

def getFromQuery(body):
    '''
    Descrption: generate from clause
    type string: body
    rtype string: fromClause
    '''
    fromClause = 'from '
    for tab in getTabsPerBody(body):
        fromClause += tab + ', '
    fromClause = fromClause.strip(', ')
    return fromClause

def getWhereQuery(bodyDict, schemaDict):
    '''
    Description: generate where clause
    type dict: bodyDict
    type dict: schemaDict
    rtype string: whereClause
    '''
    split_comp = ">|<|="
    dictCol = {}
    whereClause = 'where '
    for pred in bodyDict.keys():
        if len(re.findall(split_comp, pred))==0:
            for term in bodyDict[pred]:
                if term not in dictCol and term in schemaDict[pred]:
                    dictCol[term] = pred
                elif term in dictCol and term in schemaDict[pred]:
                    whereClause += dictCol[term] + '.' + term + '=' + pred + '.' + term + ' and '
                # specify constant
                elif term not in schemaDict[pred]:
                    pos = bodyDict[pred].index(term)
                    whereClause += pred + '.'+ schemaDict[pred][pos] + '=' + term + ' and '
        # translate built-in predicate
        else:
            term = re.split(split_comp,pred)[0]
            term = term.strip(' ')
            whereClause += dictCol[term] + '.' + pred + ' and '
    whereClause = whereClause.strip(' and ')
    return whereClause

def mainCode(datalog,inputSchemas):
    schemaDict = getBodyDict(inputSchemas)
    clauses = getClauses(datalog)
    head = seperateHeadBody(clauses[0])[0]
    cols = getColsFromHead(head)
    body = seperateHeadBody(clauses[0])[1]
    bodyDict = getBodyDict(body)
    selectClause = getSelectQuery(cols, bodyDict)
    fromClause = getFromQuery(body)
    whereClause = getWhereQuery(bodyDict, schemaDict)
    sql = selectClause + ' ' + fromClause + ' ' + whereClause
    return sql

# Input Datalog query
# Note: 1. each facts are seperated by ', '
#       2. head and body are seperated by '：-'
#       3. input: datalog query, factlist, schemalist
datalog =  'r1(a,b):-fact1(x,a), fact2(x,y), fact3(y,b).'
inputSchemas = 'fact1(x,a), fact2(a,y), fact3(y,b)'
result = mainCode(datalog,inputSchemas)
print(result)
