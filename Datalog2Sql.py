class Node(object):
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)


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

def getPredPerTerm(term):
    predicate = ''
    if term.find('(') != -1 and term.find(')') != -1:
        predicate = term.split('(')[0]
    return predicate

def parseDatalog2Tree(clauses):
    '''
    type list[string]: clauses
    rtype Node: n
    '''
    n = Node(seperateHeadBody(clauses[0])[0])
    for literal in seperateHeadBody(clauses[0])[1].split(', '):
        n.add_child(literal)
    return n

def mapFactSchema(factList, inputSchemas):
    '''
    Description: make a dictionary to contain the fact schama and corresponds fact
    type list: factList
    type list: inputSchema
    '''
    results = {}
    for fact in factList:
        pred = getPredPerTerm(fact)
        for schema in inputSchemas:
            if schema.find(pred) != -1:
                for i in range(len(getTermsInParens(schema))):
                    key = pred + "." + getTermsInParens(schema)[i]
                    if key in results:
                        results[key].append(getTermsInParens(fact)[i])
                    else:
                        results[key] = [getTermsInParens(fact)[i]]
    return results


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


def translateDatalog2Sql(n, factList, inputSchemas):
    '''
    type Node: n
    type list: inputSchemas
    type list: factList
    rtype sqlQuery: string
    '''
    schemaDict = getSchemaDict(inputSchemas)
    factSchemaDict = mapFactSchema(factList, inputSchemas)
    sqlQuery = ''
    sqlQueryFrom = 'From '
    sqlQueryWhere = 'Where '
    sqlQuerySelect = 'Select '
    duplicateTerms = {}
    head = getPredPerTerm(n.data)
    sqlQueryView = 'Create View ' + head + ' as('
    headTerms = getTermsInParens(n.data)
    colNums = len(headTerms)
    i = 1
    for children in n.children:
        tab = getPredPerTerm(children)
        sqlQueryFrom += tab + ', '
        terms = getTermsInParens(children)
        # Update where clause
        for termPos in range(len(terms)):
            termCol = tab + '.' + terms[termPos]
            if termCol not in factSchemaDict:
                ### Need to edit
                sqlQueryWhere += tab + '.' + schemaDict[tab][termPos] + '=' + terms[termPos]  +" and "
            if terms[termPos] not in duplicateTerms:
                duplicateTerms[terms[termPos]] = termCol
            else:
                sqlQueryWhere += duplicateTerms[terms[termPos]] + "=" + termCol + " and "
        # Update select clause
        for term in terms:
            if term in headTerms and i <= 2:
                sqlQuerySelect += termCol + ", "
                i += 1

    sqlQuery += sqlQueryView + "\n" + sqlQueryFrom.strip(', ') + "\n" + sqlQueryWhere.strip(' and ') + "\n" + sqlQuerySelect.strip(', ') + ')'
    return sqlQuery

def mainCode(datalog, factList, inputSchemas):
    clauses = getClauses(datalog)
    n = parseDatalog2Tree(clauses)
    sqlQuery = translateDatalog2Sql(n, factList, inputSchemas)
    print(sqlQuery)


# Input Datalog query
# Note: 1. each facts are seperated by ', '
#       2. head and body are seperated by '：-'
#       3. input: datalog query, factlist, schemalist
datalog =  'r1(a,b):-fact1(x,a), fact2(20,y), fact3(y,b).'
factList =['fact1(2,1)','fact1(2,3)','fact1(2,4)','fact2(20,10)','fact2(20,30)','fact2(20,40)', 'fact3(22,21)','fact3(22,23)','fact3(22,24)']
inputSchemas = ['fact1(x,a)', 'fact2(a,y)', 'fact3(y,b)']
mainCode(datalog,factList,inputSchemas)
