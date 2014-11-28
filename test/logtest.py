'''
Created on 2014/11/24

@author: chen_xi
'''
import re
import time




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

_LINE_NUMBER = "line number"


def _getLogFields(userFormat):
    logFields = []
    timeIndex = -1
    userPatterns = userFormat.split(sep=" ")
    for i, userPattern in enumerate(userPatterns):
        isPattern = False
        for field in _FIELD_PATTERN_DICT:
            fieldPattern = _FIELD_PATTERN_DICT[field]
            if fieldPattern.match(userPattern):
                logFields.append(field)
                if field == _TIME:
                    timeIndex = i
                isPattern = True
                break
        if not isPattern:
            logFields.append(userPattern)
    return (timeIndex, logFields)


def _isNewRecord(lineArr, timeIndex):
    '''If at the time index, the string can be casted to Time, regard this line is a new record
    '''
    if (timeIndex + 1) >= len(lineArr):
        return False
    timeStr = lineArr[timeIndex] + " " + lineArr[timeIndex + 1]
    try:
        time.strptime(timeStr, _TIME_FORMAT)
        return True
    except Exception:
        return False
        
def _parserLines(timeIndex, logFields, file):
    logHeader = []
    logDatas = []
    
    lines = open(file).readlines()
    for lineIndex, line in enumerate(lines):
        lineArr = line.split(sep=" ")
        
        for i in range(len(lineArr) - 1, -1, -1):
            if(len(lineArr[i]) == 0):
                del lineArr[i]
        
        if _isNewRecord(lineArr, timeIndex):
            logData = {}
            lineArrIndex = 0
            for index, logField in enumerate(logFields):
                logData[logField] = lineArr[lineArrIndex]
                if lineArrIndex == timeIndex:
                    lineArrIndex += 1
                    timeStr = logData[logField] + " " + lineArr[lineArrIndex]
                    logData[logField] = time.strptime(timeStr, _TIME_FORMAT)
                lineArrIndex += 1
                
                if index == (len(logFields) - 1) and lineArrIndex < len(lineArr):
                    #If it is the last field but there are still data in record, add all data to last field
                    for remindIndex in range(lineArrIndex, len(lineArr)):
                        logData[logField] = logData[logField] + " " + lineArr[remindIndex]
                    
            logData[_LINE_NUMBER] = lineIndex + 1
            logDatas.append(logData)
        elif len(logDatas) == 0:
            #If is not a new line and there is not log data before, regard it as header
            logHeader.append(line)
        else:
            #If is not a new line, append this line after last record's message
            lastData = logDatas[-1:][0]
            lastData[_MESSAGE] = lastData[_MESSAGE] + line
    return (logHeader, logDatas)


if __name__ == "__main__":
    
    userFormat = "%d [%t] %-5p %c - %m"
    
    timeIndex, logFields = _getLogFields(userFormat)
    
    lines = ["2014-11-20 16:31:20,164 [main] DEBUG org.seasar.framework.container.util.S2ContainerUtil - Registering component definition of class(jp.co.worksap.cim.web.criteria.dto.CopyDto[criteria_dto_copyDto])."]
    
    file = "../test-resource/test.log"
    
    logHeader, logDatas = _parserLines(timeIndex, logFields, file)
    
    print("Header: \r\n")
    for header in logHeader:
        print(header + "\r\n")
    print("\r\n")
    
    print("Data: \r\n")
    for data in logDatas:
        print(data[_MESSAGE] + "\r\n")
            