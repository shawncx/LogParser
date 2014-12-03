'''
Created on 2014/11/27

@author: chen_xi
'''
import re

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


def convertToPattern(conversionPattern):
    pattern = r""
    nextIsPattern = False
    for s in conversionPattern:
        if not nextIsPattern: 
            if s == _TAG:
                nextIsPattern = True
            elif s == _BLANk:
                pattern += _BLANK_PATTERN
            else:
                if s in _ESCAPE_CHARACTORS:
                    pattern += "\\"
                pattern += s
        else:
            if s in _FIELD_PATTERN_DICT:
                pattern += _FIELD_PATTERN_DICT[s]
                nextIsPattern = False
    return pattern


if __name__ == "__main__":
    
    a = "2014-11-20 16:30:28,406 [main] DEBUG factory.S2ContainerFactory - created(path=convention.dicon)\n"
    
    timePatternStr = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}"
    
    threadPatternStr = r".*"
    
    priorityPatternStr = r"\S*"
    
    classPatternStr = r"\S*"
    
    messagePatternStr = r".*"
    
    nextLinePatternStr = r"\n"
    
    blankPatternStr = r"\s"
    
    conversionPattern = "%d [%t] %-5p %c - %m%n"
    
    pattern = convertToPattern(conversionPattern)
    print(pattern)
    
    p = re.compile(pattern)
    
    match = p.match(a)
    if match:
        print(_TIME + ": " + match.group(_TIME))
        print(_CLASS+ ": " + match.group(_CLASS))
        print(_THREAD + ": " + match.group(_THREAD)) 
        print(_PRIORITY + ": " + match.group(_PRIORITY))
        print(_MESSAGE + ": " + match.group("_MESSAGE"))
              
              
              
              
              
              
