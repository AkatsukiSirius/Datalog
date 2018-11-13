import re
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

def getTableSchema(inputSchemas):
    schemaDict = {}
    for schema in inputSchemas:
        schemaDict[schema.split("(")[0]] =  schema
    return schemaDict

def str2list(t_str):
    a_list = []
    for c in str(t_str):
        a_list.append(c)
    return a_list

def list2str(a_list):
    return ', '.join(list(map(str, a_list)))

def sub(string,position,currentValue):
    new = []
    for s in string:
        new.append(s)
    new[position] = currentValue
    return ''.join(new)

def getBody(inputSchemas, sqlQuery):
    split_logic = " and | or "
    split_comp = ">|<|>=|<="
    schemaDict = getTableSchema(inputSchemas)
    sqlWhere = getWhereClause(sqlQuery)
    body = []
    for whereCondition in re.split(split_logic, sqlWhere): # or
        if whereCondition.find("=") != -1 and len(re.findall(split_comp,whereCondition)) == 0:
            # Find join part
            condLHS = whereCondition.split("=")[0]
            condRHS = whereCondition.split("=")[1]
            if condLHS.find(".") != -1 and condRHS.find(".") != -1:
                tabl = condLHS.split('.')[0]
                if schemaDict[tabl] not in body:
                    body.append(schemaDict[tabl])
                tab2 = condRHS.split('.')[0]
                if schemaDict[tab2] not in body:
                    body.append(schemaDict[tab2])
            # Find '=' condition
            elif condLHS.find(".") > -1 and condRHS.find(".") == -1:
                col = condLHS.split('.')[1]
                body.append(col + "=" + re.split("=", condRHS)[0])
            body = sorted(body)
        elif len(re.findall(split_comp,whereCondition)) > 0:
            condLHS = re.split(split_comp,whereCondition)[0]
            condRHS = re.split(split_comp,whereCondition)[1]
            if condLHS.find(".") > -1 and condRHS.find(".") > -1:
                term0 = condLHS.split('.')[1]
                term1 = condRHS.split('.')[1]
                temp = whereCondition.replace(condLHS, term0)
                temp = temp.replace(condRHS, term1)
                body.append(temp)
            elif condLHS.find(".") > -1 and condRHS.find(".") == -1:
                term0 = condLHS.split('.')[1]
                temp = whereCondition.replace(condLHS, term0)
                body.append(temp)
    bodyLiterals = list2str(body)
    return bodyLiterals



def mainCode(sqlQuery, inputSchemas):
    head = getHead(sqlQuery)
    body = getBody(inputSchemas, sqlQuery)
    print("DataLog Query: ")
    print(head + ":-" + body)


# Input SQL query
# Output Head
sqlQuery = "Create View r1 as(Select fact1.a, fact3.b From fact1, fact2, fact3 Where fact2.a=fact1.a and fact2.y=fact3.y and fact2.a>fact3.y)"
# factList = ['fact1(2,1)','fact1(2,3)','fact1(2,4)','fact2(20,10)','fact2(20,30)','fact2(20,40)', 'fact3(22,21)','fact3(22,23)','fact3(22,24)']
inputSchemas = ['fact1(x,a)', 'fact2(a,y)', 'fact3(y,b)']
mainCode(sqlQuery,inputSchemas)