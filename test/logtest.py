'''
Created on 2014/11/25

@author: chen_xi
'''


from csv import DictReader
import re
import time

def createReader(fileName):
    reader = None
    if _isCSV(fileName):
        reader = CSVReader(fileName)
    elif _isLog(fileName):
        reader = Log4JReader(fileName)
    return reader

def _isCSV(fileName):
    partten = re.compile(r"\S*\.csv\Z")
    if partten.match(fileName):
        return True
    else:
        return False
    
def _isLog(fileName):
    partten = re.compile(r"\S*\.log\Z")
    if partten.match(fileName):
        return True
    else:
        return False

class Reader:
    
    def __init__(self, fileName):
        self.fileName = fileName
    
    def getFields(self):
        raise TypeError("You should use its sub class")
    
    def getRecords(self):
        raise TypeError("You should use its sub class")
    

class Log4JReader(Reader):
    
    LINE_NUMBER = "line number"
    
    _TAG = "%"
    _TIME = "d"
    _CLASS = "c"
    _THREAD = "t"
    _PRIORITY = "p"
    _MESSAGE = "m"
    _NEW_LINE = "n"
    _BLANk = " "
    
    _TIME_PATTERN = r"(?P<d>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})"
    _CLASS_PATTERN = r"(?P<c>\S*)"
    _THREAD_PATTERN = r"(?P<t>.*)"
    _PRIORITY_PATTERN = r"(?P<p>\S*)"
    _MESSAGE_PATTERN = r"(?P<m>.*)"
    _NEW_LINE_PATTERN = r"\n"
    _BLANK_PATTERN = r"\s"
    
    _FIELD_PATTERN_DICT = {_TIME: _TIME_PATTERN, 
                       _CLASS: _CLASS_PATTERN, 
                       _THREAD: _THREAD_PATTERN, 
                       _PRIORITY: _PRIORITY_PATTERN, 
                       _MESSAGE: _MESSAGE_PATTERN, 
                       _NEW_LINE: _NEW_LINE_PATTERN
                       }
    
    _ESCAPE_CHARACTORS = "$()*+.?\\/^{}[]|"
    
    
    def __init__(self, fileName, conversionPattern):
        super().__init__(fileName)
        self._initPattern(conversionPattern)
        
        self.lineNumber = 0
        self.lastRecord = None
   
    
    def _initPattern(self, conversionPattern):
        self.fields = []
        pattern = r""
        nextIsPattern = False
        for s in conversionPattern:
            if not nextIsPattern: 
                if s == self._TAG:
                    nextIsPattern = True
                elif s == self._BLANk:
                    pattern += self._BLANK_PATTERN
                else:
                    if s in self._ESCAPE_CHARACTORS:
                        pattern += "\\"
                    pattern += s
            else:
                if s in self._FIELD_PATTERN_DICT:
                    self.fields.append(s)
                    pattern += self._FIELD_PATTERN_DICT[s]
                    nextIsPattern = False
        self.userPattern = re.compile(pattern)
    
    
    def getFields(self):
        return self.getFields()
    
    
    def getRecords(self):
        
        with open(self.fileName) as file:
            
            for line in file:
                
                self.lineNumber += 1
                
                match = self.userPattern.match(line)
                 
                record = {self.LINE_NUMBER: self.lineNumber}
                if not match and self.lastRecord == None:
                    # Header
                    for field in self.fields:
                            if field == self._MESSAGE:
                                record[field] = line
                            else:
                                record[field] = ""
                    yield record
                     
                elif not match:
#                     s2 = time.time()
                    # Message append
                    self.lastRecord[self._MESSAGE] = self.lastRecord[self._MESSAGE] + line
#                     e2 = time.time()
#                     self.time2 += (e2 - s2)
                 
                else:
                     
                    if self.lastRecord:
                        # Get new record means last record has been finished, so yield it
                        yield self.lastRecord
                     
                    # New Record
                    for field in self.fields:
                        record[field] = match.group(field)
                                 
                    self.lastRecord = record
                     
            if self.lastRecord:
                # The last record need to be yield
                yield self.lastRecord
    

class CSVReader(Reader):
    
    def __init__(self, fileName):
        super().__init__(fileName)
    
    def getFields(self):
        reader = DictReader(open(self.fileName))
        return reader.fieldnames;
    
    def getRecords(self):
        for record in DictReader(open(self.fileName)):
            yield record


'''
Condition for Search
'''

class SearchCondition:
    
    '''
    Search for single file
    '''
    
    def __init__(self, field):
        self.field = field
    
    def isFulfill(self, record):
        raise TypeError("You should use its sub class")
    
        
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
        
        
        

if __name__ == "__main__":
    
    userFormat = "%d [%t] %-5p %c - %m"
     
    fileName = "../test-resource/scale_log1.log"
    
#     fileName = "C:/Users/chen_xi/Desktop/cim/cim-logs/cim"
    
#     fileName = "../test-resource/test.log"
    
    logReader = Log4JReader(fileName, userFormat)
    
    st = time.time()
    
    for r in logReader.getRecords():
#         print(str(r))
        pass
    
#     print(logReader.time1)
#     print(logReader.time2)
#     print(logReader.time3)
    print("line: " + str(logReader.lineNumber))
        
    et = time.time()
    print(str(et - st))
    
