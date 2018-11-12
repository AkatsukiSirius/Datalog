def getSelectFromWhereQuery(sqlQuery):
    '''
    type string: sqlQuery
    rtype string: sqlQueryFiltered
    '''
    sqlQueryFiltered = sqlQuery[sqlQuery.find('(')+1:sqlQuery.find(')')]
    return sqlQueryFiltered

def getSelectClause(sqlQuery):
    '''
    type string: sqlQuery
    rtype string: sqlSelect
    '''
    sqlQueryFiltered = getSelectFromWhereQuery(sqlQuery)
    sqlSelect = sqlQueryFiltered[sqlQueryFiltered.find('Select')+6:sqlQueryFiltered.find('From') - 1].strip(' ')
    return sqlSelect

def getFromClause(sqlQuery):
    '''
    type string: sqlQuery
    rtype string: sqlFrom
    '''
    sqlQueryFiltered = getSelectFromWhereQuery(sqlQuery)
    sqlFrom = sqlQueryFiltered[sqlQueryFiltered.find('From')+5:sqlQueryFiltered.find('Where') - 1].strip(' ')
    return sqlFrom

def getWhereClause(sqlQuery):
    '''
    type string: sqlQuery
    rtype string: sqlWhere
    '''
    sqlQueryFiltered = getSelectFromWhereQuery(sqlQuery)
    sqlWhere = sqlQueryFiltered[sqlQueryFiltered.find('Where')+5:].strip(' ')
    return sqlWhere

def getHeadTerms(sqlQuery):
    '''
    Descritption: extract head terms from select clauses
    type string: sqlSelect
    rtype string: headTerms
    '''
    results = []
    headTerms = "("
    sqlSelect = getSelectClause(sqlQuery)
    for term in sqlSelect.split(','):
        results.append(term.split('.')[1])
    for result in results:
        headTerms += result + ','
    headTerms = headTerms.strip(',')
    headTerms += ")"
    return headTerms

def getHead(sqlQuery):
    '''
    type string: sqlQuery
    rtype string: head
    '''
    headRule = sqlQuery[sqlQuery.find('Create View')+ 11:sqlQuery.find('as')].strip(' ')
    head = headRule + getHeadTerms(sqlQuery)
    return head

def getFacts(sqlFrom):
    '''
    type string: sqlFrom
    rtype list[string]
    '''
    return sqlFrom.split(', ')

def mainCode(sqlQuery, factList, inputSchemas):
    head = getHead(sqlQuery)
    print("Print Head:")
    print(head)


# Input SQL query
# Output Head
sqlQuery = "Create View r1 as(Select fact1.a, fact3.b From fact1, fact2, fact3 Where fact2.a=fact1.a and fact2.y=fact3.y )"
factList =['fact1(2,1)','fact1(2,3)','fact1(2,4)','fact2(20,10)','fact2(20,30)','fact2(20,40)', 'fact3(22,21)','fact3(22,23)','fact3(22,24)']
inputSchemas = ['fact1(x,a)', 'fact2(a,y)', 'fact3(y,b)']
mainCode(sqlQuery,factList,inputSchemas)
