import re
def getHeadTerms(sqlSelect):
    '''
    Descritption: extract head terms from select clauses
    type string: sqlSelect
    rtype string: headTerms
    '''
    results = []
    headTerms = '('
    for term in sqlSelect.split(','):
        results.append(term.split('.')[1])
    for result in results:
        headTerms += result + ','
    headTerms = headTerms.strip(',')
    headTerms += ")"
    return headTerms

def splitSQL(sqlQuery):
    '''
    Description: return head literal and split sql query
    type string: sqlQuery
    rtype list
    '''
    sqlQuery = sqlQuery.lower()
    split_sql = "select|from|where"
    head = sqlQuery.split('as (')[0]
    sqlWhere = ''
    if sqlQuery.find('where') != -1:
        [sqlSelect, sqlFrom, sqlWhere] = [item.strip(' ') for item in re.split(split_sql, sqlQuery.split('as(')[1].strip(')')) if item != '']
    else:
        [sqlSelect, sqlFrom] = [item.strip(' ') for item in re.split(split_sql, sqlQuery.split('as(')[1].strip(')')) if item != '']
    headRule = head[head.find('create view')+ 11:sqlQuery.find('as')].strip(' ')
    headLiteral = headRule + getHeadTerms(sqlSelect)
    return headLiteral, sqlFrom, sqlWhere

def getTableSchema(inputSchemas):
    '''
    Description: generate a dictionary for body literals
    :type string: inputSchemas
    :rtype schemaDict
    '''
    schemaDict = {}
    for schema in inputSchemas:
        schemaDict[schema.split("(")[0]] =  schema
    return schemaDict

def list2str(a_list):
    return ', '.join(list(map(str, a_list)))

def getBody(inputSchemas, sqlFrom,sqlWhere):
    split_logic = " and | or "
    split_comp = ">|<"
    split_comp1 = ">=|<="
    split_comp2 = ">=|<=|>|<"
    schemaDict = getTableSchema(inputSchemas)
    body = []
    if sqlWhere != '':
        for whereCondition in re.split(split_logic, sqlWhere): # or
            if whereCondition.find("=") != -1 and len(re.findall(split_comp1,whereCondition)) == 0:
                # translate join condition
                condLHS = whereCondition.split("=")[0]
                condRHS = whereCondition.split("=")[1]
                if condLHS.find(".") != -1 and condRHS.find(".") != -1:
                    tabl = condLHS.split('.')[0]
                    if schemaDict[tabl] not in body:
                        body.append(schemaDict[tabl])
                    tab2 = condRHS.split('.')[0]
                    if schemaDict[tab2] not in body:
                        body.append(schemaDict[tab2])
                # translate'=' condition
                elif condLHS.find(".") > -1 and condRHS.find(".") == -1:
                    tab = condLHS.split('.')[0]
                    col = condLHS.split('.')[1]
                    body.append(col + "=" + re.split(split_comp, condRHS)[0])
            # translate built-in condition
            elif len(re.findall(split_comp2,whereCondition)) > 0:
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
    else:
         body.append(schemaDict[sqlFrom])
    body = sorted(body)
    bodyLiterals = list2str(body)
    return bodyLiterals

def mainCode(sqlQuery, inputSchemas):
    headLiteral, sqlFrom, sqlWhere = splitSQL(sqlQuery)
    bodyLiteral = getBody(inputSchemas, sqlFrom, sqlWhere)
    print("DataLog Query: ")
    print(headLiteral + ":- " + bodyLiteral)


# Input SQL query
# Output Head
sqlQuery = "Create View r1 as(select fact1.a, fact3.b from fact1, fact2, fact3 where fact2.a=fact1.a and fact2.y=fact3.y and fact2.a>=10)"
# factList = ['fact1(2,1)','fact1(2,3)','fact1(2,4)','fact2(20,10)','fact2(20,30)','fact2(20,40)', 'fact3(22,21)','fact3(22,23)','fact3(22,24)']
inputSchemas = ['fact1(x,a)', 'fact2(a,y)', 'fact3(y,b)']
mainCode(sqlQuery,inputSchemas)