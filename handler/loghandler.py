'''
Created on 2014/11/25

@author: chen_xi
'''


from csv import DictReader, DictWriter
import re
import time

DEFAULT_ENCODING = "MS932"


def createReader(fileName, conversionPattern=None, datePattern=None):
    reader = None
    if isCSV(fileName):
        reader = CSVReader(fileName)
    elif isLog(fileName):
        reader = Log4JReader(fileName, conversionPattern, datePattern)
    return reader

def createWriter(fileName):
    writer = None
    if isCSV(fileName):
        writer = CSVWriter(fileName)
    elif isLog(fileName):
        writer = LogWriter(fileName)
    return writer

def isCSV(fileName):
    partten = re.compile(r".*\.csv\Z")
    if partten.match(fileName):
        return True
    else:
        return False
    
def isLog(fileName):
    partten = re.compile(r".*\.log\Z")
    if partten.match(fileName):
        return True
    else:
        return False
    
    
class Writer:
    
    def __init__(self, fileName):
        self.fileName = fileName
        
    def write(self, recordDicts, fieldNames):
        raise TypeError("You should use its sub class")

class CSVWriter(Writer):
    
    def __init__(self, fileName):
        super().__init__(fileName)
        
    def write(self, recordDicts, fieldNames):
        with open(self.fileName, "w", newline='', encoding=DEFAULT_ENCODING) as file:
            writer = DictWriter(file, fieldNames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(recordDicts);
        
class LogWriter(Writer):
    
    def __init__(self, fileName):
        super().__init__(fileName)
        
    def write(self, recordDicts, fieldNames):
        with open(self.fileName, "w", encoding=DEFAULT_ENCODING) as file:
            for recordDict in recordDicts:
                record = self._dictToRecord(recordDict, fieldNames)
                file.write(record + "\n")
             
    def _dictToRecord(self, recordDict, fieldNames):
        record = ""
        for key in fieldNames:
            record += " " + recordDict[key]
        return record

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
    
    _CLASS_PATTERN = r"(?P<" + _CLASS + ">\s*\S*\s*)"
    _THREAD_PATTERN = r"(?P<" + _THREAD + ">\s*\S*\s*)"
    _PRIORITY_PATTERN = r"(?P<" + _PRIORITY + ">\s*\S*\s*)"
    _MESSAGE_PATTERN = r"(?P<" + _MESSAGE + ">.*)"
    _NEW_LINE_PATTERN = r"\n"
    _BLANK_PATTERN = r"\s"
    
    _FIELD_PATTERN_DICT = {_TIME: "",
                       _CLASS: _CLASS_PATTERN,
                       _THREAD: _THREAD_PATTERN,
                       _PRIORITY: _PRIORITY_PATTERN,
                       _MESSAGE: _MESSAGE_PATTERN,
                       _NEW_LINE: _NEW_LINE_PATTERN
                       }
    
    _TIME_YEAR = "y"
    _TIME_MONTH = "M"
    _TIME_DAY = "d"
    _TIME_HOUR = "H"
    _TIME_MINUTE = "m"
    _TIME_SECOND = "s"
    _TIME_MILLISECOND = "S"
    
    _DATE_YEAR = "Y"
    _DATE_MONTH = "m"
    _DATE_DAY = "d"
    _DATE_HOUR = "H"
    _DATE_MINUTE = "M"
    _DATE_SECOND = "S"
    _DATE_MILLISECOND = "f"
    
    _DATE_YEAR_PATTERN = r"(?:\d{2}|\d{4})"
    _DATE_MONTH_PATTERN = r"(?:\d{1}|\d{2})"
    _DATE_DAY_PATTERN = r"(?:\d{1}|\d{2})"
    _DATE_HOUR_PATTERN = r"(?:\d{1}|\d{2})"
    _DATE_MINUTE_PATTERN = r"(?:\d{1}|\d{2})"
    _DATE_SECOND_PATTERN = r"(?:\d{1}|\d{2})"
    _DATE_MILLISECOND_PATTERN = r"\d+"
    
    
    _DATE_PATTERN_DICT = {_DATE_YEAR: _DATE_YEAR_PATTERN,
                          _DATE_MONTH: _DATE_MONTH_PATTERN,
                          _DATE_DAY: _DATE_DAY_PATTERN,
                          _DATE_HOUR: _DATE_HOUR_PATTERN,
                          _DATE_MINUTE: _DATE_MINUTE_PATTERN,
                          _DATE_SECOND: _DATE_SECOND_PATTERN,
                          _DATE_MILLISECOND: _DATE_MILLISECOND_PATTERN
                          }
    
    _ESCAPE_CHARACTORS = "$()*+.?\\/^{}[]|"
    
    
    def __init__(self, fileName, conversionPattern, datePattern):
        super().__init__(fileName)
        
        self._initUserPattern(conversionPattern, datePattern)
        
        self.lineNumber = 0
        self.lastRecord = None
        
    
    def _initUserDatePattern(self, datePattern):
        self.datePattern = datePattern
        
        pattern = r""
        nextIsPattern = False
        for s in datePattern:
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
                if s in self._DATE_PATTERN_DICT:
                    pattern += self._DATE_PATTERN_DICT[s]
                    nextIsPattern = False
        self.userdatePattern = "(?P<" + self._TIME + ">" + pattern + ")"
   
    
    def _initUserPattern(self, conversionPattern, datePattern):
        
        self._initUserDatePattern(datePattern)
        self.conversionPattern = conversionPattern
        
        self.fields = []
        recordPattern = r""
        nextIsPattern = False
        for s in conversionPattern:
            if not nextIsPattern: 
                if s == self._TAG:
                    nextIsPattern = True
                elif s == self._BLANk:
                    recordPattern += self._BLANK_PATTERN
                else:
                    if s in self._ESCAPE_CHARACTORS:
                        recordPattern += "\\"
                    recordPattern += s
            else:
                if s in self._FIELD_PATTERN_DICT:
                    self.fields.append(s)
                    if s == self._TIME:
                        recordPattern += self.userdatePattern
                    else:
                        recordPattern += self._FIELD_PATTERN_DICT[s]
                    nextIsPattern = False
        self.userPattern = re.compile(recordPattern)
    
    
    def getFields(self):
        return self.fields
    
    
    def getRecords(self):
        
        with open(self.fileName, encoding=DEFAULT_ENCODING) as file:
            
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
        reader = DictReader(open(self.fileName, encoding=DEFAULT_ENCODING))
        return reader.fieldnames;
    
    def getRecords(self):
        for record in DictReader(open(self.fileName, encoding=DEFAULT_ENCODING)):
            yield record


'''
Condition for Search
'''

class SearchCondition:
    
    '''
    Search for single file
    '''
    
    def __init__(self, field, disabled=False):
        self.field = field
        self.disabled = disabled
    
    def isFulfill(self, record):
        raise TypeError("You should use its sub class")
    
        
class RangeSearchCondition(SearchCondition):
    
    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    TYPE_NUMBER = "number"
    
    TYPE_DATE = "date"
    
    TYPE_STRING = "string"
    
    COMP_BELOW = "below"
    
    COMP_OVER = "over"
    
    def __init__(self, field, valMin, valMax, dataType, datePattern=None, disabled=False):
        super().__init__(field, disabled)
        self.dataType = dataType
        self.datePattern = datePattern
        if dataType == self.TYPE_NUMBER:
            self.valMin = float(valMin)
            self.valMax = float(valMax)
        elif dataType == self.TYPE_DATE:
            self.valMin = time.strptime(valMin, self.DEFAULT_DATE_FORMAT)
            self.valMax = time.strptime(valMax, self.DEFAULT_DATE_FORMAT)
        else:
            self.valMin = valMin
            self.valMax = valMax
        
    def isFulfill(self, record):
        tarValue = record[self.field]
        if not tarValue:
            return (False, self.COMP_BELOW)
        if not tarValue:
            return (False, self.COMP_BELOW)
        if self.dataType == self.TYPE_DATE:
            tarValue = time.strptime(tarValue, self.datePattern)
        elif self.dataType == self.TYPE_NUMBER:
            tarValue = float(tarValue)
            
        if tarValue <= self.valMax and tarValue >= self.valMin:
            return (True, None)
        elif tarValue > self.valMax:
            return (False, self.COMP_OVER)
        else:
            return (False, self.COMP_BELOW)
        
    def toString(self):
        if self.dataType == self.TYPE_DATE:
            return self.field + " in [" + time.strftime(RangeSearchCondition.DEFAULT_DATE_FORMAT, self.valMin) \
                + ", " + time.strftime(RangeSearchCondition.DEFAULT_DATE_FORMAT, self.valMax) + "]"
        else:
            return self.field + " in [" + str(self.valMin) + ", " + str(self.valMax) + "]"
        
        
class EqualSearchCondition(SearchCondition):
    def __init__(self, field, val, disabled=False):
        super().__init__(field, disabled)
        self.val = val
        
    def isFulfill(self, record):
        if record[self.field] == self.val:
            return (True, None)
        else:
            return (False, None)
        
    def toString(self):
        return self.field + " equal " + self.val
    
    
class ContainSearchCondition(SearchCondition):
    def __init__(self, field, val, disabled=False):
        super().__init__(field, disabled)
        self.val = val
        
    def isFulfill(self, record):
        return (self.val in record[self.field], None)
        
    def toString(self):
        return self.field + " contains " + self.val
    
    
class JoinCondition:
    
    ''' 
    Search for two files join
    '''
    
    def __init__(self, fromField, toField, disabled=False):
        self.fromField = fromField
        self.toField = toField
        self.disabled = disabled
    
    def isFulfill(self, record):
        raise TypeError("You should use its sub class")
    
    
class EqualJoinCondition(JoinCondition):
    
    def __init__(self, fromField, toField, disabled=False):
        super().__init__(fromField, toField, disabled)
        
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
    
    def __init__(self, fileName, data, conditions, relation, enableOptimaize=True):
        self.fileName = fileName
        self.data = data
        self.conditions = conditions
        for cond in conditions:
            cond.disabled = False
        self.relation = relation
        self.enableOptimaize = enableOptimaize
        if(relation.lower() == ("or", "and")):
            raise ValueError("relation (%s) must be 'or' or 'and'" % relation)
        
    
    def process(self):
        fileResult = FileResult(self.fileName, [])
        
        optimaizeStop = False
        isLogFile = isLog(self.fileName)
        condLength = len(self.conditions)
        
        for record in self.data:
            addRecord = True
            
            for condition in self.conditions:
                if condition.disabled:
                    continue
                
                isFulfill, info = condition.isFulfill(record)
                
                if self.enableOptimaize:
                    if isLogFile:
                        if info == RangeSearchCondition.COMP_OVER and condition.dataType == RangeSearchCondition.TYPE_DATE:
                            condition.disabled = True
                            condLength -= 1
                            if condLength == 0 or self.relation == "and":
                                optimaizeStop = True
                    
                if isFulfill and self.relation == "or":
                    break
                elif not isFulfill and self.relation == "and":
                    addRecord = False
                    break
            if addRecord:
                fileResult.result.append(record)
            if optimaizeStop:
                break
                
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
                
                # If new field or value in from file appear, init the cache
                if not fromField in fromFieldCache:
                    fromFieldCache[fromField] = {fromValue: 0}
                elif not fromValue in fromFieldCache[fromField]:
                    fromFieldCache[fromField][fromValue] = 0
                
                # Process
                if fromFieldCache[fromField][fromValue] == 2:
                    # The value of field has been checked and not matched
                    # Abandon it
                    continue
                elif fromFieldCache[fromField][fromValue] == 1:
                    # The value of field has been checked and matched
                    # Only add the from record, because to record has been added last time
                    fromFileResult.result.append(record)
                elif fromFieldCache[fromField][fromValue] == 0:
                    # The value of field has not been checked
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
    
    
    
    conversionPattern = "%d [%t] %-5p %c - %m"
    
    datePattern4J = "yyyy-MM-dd HH:mm:ss,SSS"
    
    datePattern4P = "%Y-%m-%d %H:%M:%S,%f"
     
#     fileName = "../test-resource/scale_log1.log"
    
#     fileName = "C:/Users/chen_xi/Desktop/cim/cim-logs/cim"
    
    fileName = "../test-resource/test.log"
    
    logReader = Log4JReader(fileName, conversionPattern, datePattern4J, datePattern4P)
    
    log = "[2014/11/18 18:00:03] S trap{continue}\n"
    
    p = "\[(?P<d>\d{4}\/\d{2}\/\d{2}\s\d{2}:\d{2}:\d{2})\]\s(?P<p>\s*\S*\s*)\s(?P<m>.*)"
    
    pat = re.compile(p)
    
    m = pat.match(log)
    
    print(m)
    
    st = time.time()
    
#     n = 1
#     for r in logReader.getRecords():
# #         pass
#         print(r)
#         print(n)
#         n += 1
#     
#     print("line: " + str(logReader.lineNumber))
#         
#     et = time.time()
#     print(str(et - st))
    
