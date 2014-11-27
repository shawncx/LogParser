'''
Created on 2014/11/25

@author: chen_xi
'''


from csv import DictReader
import csv
import re
import time


class Reader:
    
    def getFields(self):
        raise TypeError("You should use its sub class")
    
    def next(self):
        raise TypeError("You should use its sub class")
    
    def __iter__(self):
        return self


class Log4JReader(Reader):
    
    LINE_NUMBER = "line number"
    
    _TIME_FORMAT = "%Y-%m-%d %H:%M:%S,%f"

    _STYLE = "%"
    _TIME = "d"
    _CLASS = "c"
    _THREAD = "t"
    _PRIORITY = "p"
    _MESSAGE = "m"
    _NEW_LINE = "n"
    
    _TIME_PATTERN = re.compile("\S*" + _STYLE + "\S*" + _TIME + "\S*")
    _CLASS_PATTERN = re.compile("\S*" + _STYLE + "\S*" + _CLASS + "\S*")
    _THREAD_PATTERN = re.compile("\S*" + _STYLE + "\S*" + _THREAD + "\S*")
    _PRIORITY_PATTERN = re.compile("\S*" + _STYLE + "\S*" + _PRIORITY + "\S*")
    _MESSAGE_PATTERN = re.compile("\S*" + _STYLE + "\S*" + _MESSAGE + "\S*")
    _NEW_LINE_PATTERN = re.compile("\S*" + _STYLE + "\S*" + _NEW_LINE + "\S*")
    
    _FIELD_PATTERN_DICT = {_TIME: _TIME_PATTERN, 
                       _CLASS: _CLASS_PATTERN, 
                       _THREAD: _THREAD_PATTERN, 
                       _PRIORITY: _PRIORITY_PATTERN, 
                       _MESSAGE: _MESSAGE_PATTERN, 
                       _NEW_LINE: _NEW_LINE_PATTERN
                       }
    
    
    def __init__(self, fileName, userFormat):
        self.userFormat = userFormat
        self.fileName = fileName
        self.lineNumber = 0
        
        self.file = open(fileName)
        self.timeIndex = -1
        self.fields = self._getFields()
        
        for index, field in enumerate(self.fields):
            if field == self._TIME:
                self.timeIndex = index
                break
            
        self.isHeadEnd = False
        self.nextLine = None
   
    
    def _getFields(self):
        logFields = []
        userPatterns = self.userFormat.split(sep=" ")
        for userPattern in userPatterns:
            isPattern = False
            for field in self._FIELD_PATTERN_DICT:
                fieldPattern = self._FIELD_PATTERN_DICT[field]
                if fieldPattern.match(userPattern):
                    logFields.append(field)
                    isPattern = True
                    break
            if not isPattern:
                logFields.append(userPattern)
        return logFields
    
    
    def getFields(self):
        return self.getFields()
    
    
    def __next__(self):
        
        self.lineNumber += 1
        
        if self.nextLine:
            line = self.nextLine
        else:
            line = self.file.readline()
            
        if not line:
            raise StopIteration()
        
        lineArr = line.split(sep=" ")
            
        for i in range(len(lineArr) - 1, -1, -1):
            if(len(lineArr[i]) == 0):
                del lineArr[i]
        
        logData = {self.LINE_NUMBER: self.lineNumber}
        
        if not self.isHeadEnd:
            if self._isNewRecord(lineArr, self.timeIndex):
                self.isHeadEnd = True
            else:
                #If is not a new line and there is not log data before, regard it as header
                for field in self.fields:
                    if field == self._MESSAGE:
                        logData[field] = line
                    else:
                        logData[field] = ""
                        
        if self.isHeadEnd:
            lineArrIndex = 0
            for index, field in enumerate(self.fields):
                logData[field] = lineArr[lineArrIndex]
                if lineArrIndex == self.timeIndex:
                    lineArrIndex += 1
                    timeStr = logData[field] + " " + lineArr[lineArrIndex]
                    logData[field] = time.strptime(timeStr, self._TIME_FORMAT)
                lineArrIndex += 1
                
                if index == (len(self.fields) - 1) and lineArrIndex < len(lineArr):
                    #If it is the last field but there are still data in record, add all data to last field
                    for remindIndex in range(lineArrIndex, len(lineArr)):
                        logData[field] = logData[field] + " " + lineArr[remindIndex]
                        
            while True:
                self.nextLine = self.file.readline()
                # File is over
                if not self.nextLine:
                    break
                nextLineArr = self.nextLine.split(sep=" ")
                if not self._isNewRecord(nextLineArr, self.timeIndex):
                    logData[self._MESSAGE] = logData[self._MESSAGE] + self.nextLine
                    self.lineNumber += 1
                else:
                    break
                    
        return logData
    
    def getData(self):
        
        logFields = self.getFields()
        lines = open(self.fileName).readlines()
        
        logHeader = []
        logDatas = []
        
        for lineIndex, line in enumerate(lines):
            lineArr = line.split(sep=" ")
            
            for i in range(len(lineArr) - 1, -1, -1):
                if(len(lineArr[i]) == 0):
                    del lineArr[i]
            
            if self._isNewRecord(lineArr, self.timeIndex):
                logData = {}
                lineArrIndex = 0
                for index, logField in enumerate(logFields):
                    logData[logField] = lineArr[lineArrIndex]
                    if lineArrIndex == self.timeIndex:
                        lineArrIndex += 1
                        timeStr = logData[logField] + " " + lineArr[lineArrIndex]
                        logData[logField] = time.strptime(timeStr, self._TIME_FORMAT)
                    lineArrIndex += 1
                    
                    if index == (len(logFields) - 1) and lineArrIndex < len(lineArr):
                        #If it is the last field but there are still data in record, add all data to last field
                        for remindIndex in range(lineArrIndex, len(lineArr)):
                            logData[logField] = logData[logField] + " " + lineArr[remindIndex]
                        
                logData[self._LINE_NUMBER] = lineIndex + 1
                logDatas.append(logData)
            elif len(logDatas) == 0:
                #If is not a new line and there is not log data before, regard it as header
                logHeader.append(line)
            else:
                #If is not a new line, append this line after last record's message
                lastData = logDatas[-1:][0]
                lastData[self._MESSAGE] = lastData[self._MESSAGE] + line
        return (logHeader, logDatas)
    
    
    def _isNewRecord(self, lineArr, timeIndex):
        '''If at the time index, the string can be casted to Time, regard this line is a new record
        '''
        if (timeIndex + 1) >= len(lineArr):
            return False
        timeStr = lineArr[timeIndex] + " " + lineArr[timeIndex + 1]
        try:
            time.strptime(timeStr, self._TIME_FORMAT)
            return True
        except Exception:
            return False
    

class CSVReader:
    
    def __init__(self, fileName):
        self.fileName = fileName
        
    def getFields(self):
        reader = DictReader(open(self.fileName))
        return reader.fieldnames();
    
    def getData(self):
        return DictReader(open(self.fileName))



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
        
        

if __name__ == "__main__":
    
    userFormat = "%d [%t] %-5p %c - %m"
     
    fileName = "../test-resource/test.log"
    
    logReader = Log4JReader(fileName, userFormat)
    
    for r in logReader:
        print(str(r))
    
