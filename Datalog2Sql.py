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

def translateDatalog2Sql(n):
    '''
    type Node: n
    rtype sqlQuery: string
    '''
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
        for term in terms:
            termCol = tab + '.' + term
            if term not in duplicateTerms:
                duplicateTerms[term] = termCol
            else:
                sqlQueryWhere += duplicateTerms[term] + "=" + termCol + ", "
            if term in headTerms and i <= 2:
                sqlQuerySelect += termCol + ", "
                i += 1

    sqlQuery += sqlQueryView + "\n" + sqlQueryFrom.strip(', ') + "\n" + sqlQueryWhere.strip(', ') + "\n" + sqlQuerySelect.strip(', ') + ')'
    return sqlQuery


# Input Datalog query
# Note: 1. each facts are seperated by ', '
#       2. head and body are seperated by '：-‘
datalog = "r1(A,B):-fact1(A,X), fact2(X,Y), fact3(Y,B). "
clauses = getClauses(datalog)
n = parseDatalog2Tree(clauses)
sqlQuery = translateDatalog2Sql(n)
print(sqlQuery)