'''
Created on 2014/11/25

@author: chen_xi
'''
'''
Condition for Search
'''

import csv
import time


def getFields(filename):
    file = open(filename)
    reader = csv.reader(file)
    fields = []
    for row in reader:
        fields = row
        break;
    file.close()
    return fields;


class SearchCondition:
    
    '''
    Search for single file
    '''
    
    def __init__(self, field):
        self.field = field
    
    def isFulfill(self, record):
        pass
    
        
class RangeSearchCondition(SearchCondition):
    def __init__(self, field, valMin, valMax):
        super().__init__(field)
        self.valMin = valMin
        self.valMax = valMax
        
    def isFulfill(self, record):
        if record[self.field] <= self.valMax and record[self.field] >= self.valMin:
            return True
        else:
            return False
        
    def toString(self):
        return self.field + " in [" + self.valMin + ", " + self.valMax + "]"
        
class EqualSearchCondition(SearchCondition):
    def __init__(self, field, val):
        super().__init__(field)
        self.val = val
        
    def isFulfill(self, record):
        if record[self.field] == self.val:
            return True
        else:
            return False
        
    def toString(self):
        return self.field + " equal " + self.val
    
class ContainSearchCondition(SearchCondition):
    def __init__(self, field, val):
        super().__init__(field)
        self.val = val
        
    def isFulfill(self, record):
        return self.val in record[self.field]
        
    def toString(self):
        return self.field + " contain " + self.val
    
    
class JoinSearchCondition:
    ''' 
    Search for two files join
    '''
    def __init__(self, fromField, toField):
        self.fromField = fromField
        self.toField = toField
        
    def toString(self):
        return self.fromField + " = " + self.toField
    

'''
Search for file
'''
    
class SingleFileSearch:
    
    ''' According to the given conditions search the fulfill records in the given data
    
        'data' - a iterable list with dict
        'relation' - 'and' or 'or'
    '''
    
    def __init__(self, fileName, data, conditions, relation):
        self.fileName = fileName
        self.data = data
        self.conditions = conditions
        self.relation = relation
        if(relation.lower() == ("or", "and")):
            raise ValueError("relation (%s) must be 'or' or 'and'" % relation)
    
    def process(self):
        fileResult = FileResult(self.fileName, [])
        for record in self.data:
            flag = True
            for condition in self.conditions:
                isFulfill = condition.isFulfill(record)
                if isFulfill and self.relation == "or":
                    break
                elif not isFulfill and self.relation == "and":
                    flag = False
                    break
            if flag:
                fileResult.result.append(record)
                
        return fileResult
    
    
class JoinFileSearch:
    
    ''' According to the given conditions join the data in two files.
    
        'fromData' - a iterable list with dict
        'toData' - a iterable list with dict
        'relation' - relationship between conditions. It should be 'and' or 'or'
    '''
    
    def __init__(self, fromFileName, fromData, toFileName, toData, conditions):
        self.fromFileName = fromFileName
        self.fromData = fromData
        self.toFileName = toFileName
        self.toData = toData
        self.conditions = conditions
        self.indexes = {}
        
    def process(self):
        self._initIndex()
        fromFileResult = FileResult(self.fromFileName, [])
        toFileResult = FileResult(self.toFileName, [])
        fromFieldCache = {};
        for record in self.fromData:
            for condition in self.conditions:
                
                fromField = condition.fromField
                
                toField = condition.toField
                fromValue = record[fromField]
                
                '''
                    0 means has not decided
                    1 means successful match
                    2 means failed match
                '''
                
                if not fromField in fromFieldCache:
                    fromFieldCache[fromField] = {fromValue: 0}
                elif not fromValue in fromFieldCache[fromField]:
                    fromFieldCache[fromField][fromValue] = 0
                
                if fromFieldCache[fromField][fromValue] == 2:
                    continue
                elif fromFieldCache[fromField][fromValue] == 1:
                    fromFileResult.result.append(record)
                elif fromFieldCache[fromField][fromValue] == 0:
                    if fromValue in self.indexes[toField]:
                        fromFileResult.result.append(record)
                        toFileResult.result += self.indexes[toField][fromValue]
                        fromFieldCache[fromField][fromValue] = 1
                    else:
                        fromFieldCache[fromField][fromValue] = 2
                
        return (fromFileResult, toFileResult)
    
    def _initIndex(self):
        
        '''Create index for to file. All the target fields in to file will be added index.
    
            The index format will be like: 
            {toField1: 
                {toField1_value1: [recordcontent], 
                 toField1_value2: [recordcontent],
                 ...
                }, 
             toField2:
                {toField2_value1: [recordcontent], 
                 toField2_value2: [recordcontent]
                 ...
                }, 
                ...
            }
        '''
        
        if len(self.conditions) == 0:
            return
        for record in self.toData:
            for condition in self.conditions:
                toField = condition.toField
                toval = record[toField]
                if toField in self.indexes:
                    fieldDict = self.indexes[toField]
                    if toval in fieldDict:
                        fieldDict[toval].append(record)
                    else:
                        fieldDict[toval] = [record]
                else:
                    self.indexes[toField] = {toval: [record]}
                    
class Search:
    
    ''' 
    Object to process multiple kinds of search
    '''

    def __init__(self, singleFileSearches, joinFileSearches):
        self.singleFileSearches = singleFileSearches
        self.joinFileSearches = joinFileSearches
        
    def process(self):
        
        fileResults = {};
        
        startTime = time.time()
        
#         process file search 
        for singleFileSearch in self.singleFileSearches:
            fileResult = singleFileSearch.process()
            fileResults[fileResult.fileName] = fileResult
            
        for joinFileSearch in self.joinFileSearches:
            
#             update data if the data has been filtered in file search
            fromFileName = joinFileSearch.fromFileName
            if fromFileName in fileResults:
                joinFileSearch.fromData = fileResults[fromFileName].result
            toFileName = joinFileSearch.toFileName
            if toFileName in fileResults:
                joinFileSearch.toData = fileResults[toFileName].result
            
#             using new result to update result 
            (fromFileResult, toFileResult) = joinFileSearch.process()
            fileResults.update({fromFileResult.fileName : fromFileResult})
            fileResults.update({toFileResult.fileName : toFileResult})
            
        endTime = time.time()
            
        searchResult = SearchResult(fileResults, endTime - startTime)
        
        return searchResult

    
'''
Search result
'''
        
class SearchResult:
    
    '''Result for once search
    
        'results' - dict like: {fileName1: FileSearchResult2, fileName2: FileSearchResult2}
    '''
    
    def __init__(self, results, timeCost):
        self.results = results
        self.timeCost = timeCost
        
        
class FileResult:
    
    '''Result for file search
    
        'result' - iterable list with dict
    '''
    
    def __init__(self, fileName, result):
        self.fileName = fileName
        self.result = result
