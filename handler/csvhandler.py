'''
Created on 2014/11/4

@author: chen_xi
'''

from csv import DictReader
import csv
import time


def getfields(filename):
    file = open(filename)
    reader = csv.reader(file)
    fields = []
    for row in reader:
        fields = row
        break;
    file.close()
    return fields;

'''
Search for single file
'''

class SearchCondition:
    def __init__(self, field):
        self.field = field
    
    def isfulfill(self, row):
        pass
    
        
class RangeSearchCondition(SearchCondition):
    def __init__(self, field, valmin, valmax):
        super().__init__(field)
        self.valmin = valmin
        self.valmax = valmax
        
    def isfulfill(self, row):
        if row[self.field] <= self.valmax and row[self.field] >= self.valmin:
            return True
        else:
            return False
        
    def tostring(self):
        return self.field + " in [" + self.valmin + ", " + self.valmax + "]"
        
class ValueSearchCondition(SearchCondition):
    def __init__(self, field, val):
        super().__init__(field)
        self.val = val
        
    def isfulfill(self, row):
        if row[self.field] == self.val:
            return True
        else:
            return False
        
    def tostring(self):
        return self.field + " = " + self.val
        
        
class SingleFileSearch:
    
    ''' According to the given conditions search the fulfill rows in the given data
    
        'data' - a iterable list with dict
        'relation' - 'and' or 'or'
    '''
    
    def __init__(self, filename, data, conditions, relation):
        self.filename = filename
        self.data = data
        self.conditions = conditions
        self.relation = relation
        if(relation.lower() == ("or", "and")):
            raise ValueError("relation (%s) must be 'or' or 'and'" % relation)
    
    def process(self):
        fileresult = FileResult(self.filename, [])
        for row in self.data:
            flag = True
            for condition in self.conditions:
                isfulfill = condition.isfulfill(row)
                if isfulfill and self.relation == "or":
                    break
                elif not isfulfill and self.relation == "and":
                    flag = False
                    break
            if flag:
                fileresult.result.append(row)
                
        return fileresult
    
    
'''
Search for two files join
'''
    
class JoinSearchCondition:
    def __init__(self, fieldtuple):
        self.fieldtuple = fieldtuple
        
    def tostring(self):
        return self.fieldtuple[0] + " = " + self.fieldtuple[1]
        
    
class JoinFileSearch:
    
    ''' According to the given conditions join the data in two files.
    
        'fromdata' - a iterable list with dict
        'todata' - a iterable list with dict
        'relation' - relationship between conditions. It should be 'and' or 'or'
    '''
    
    def __init__(self, fromfilename, fromdata, tofilename, todata, conditions):
        self.fromfilename = fromfilename
        self.fromdata = fromdata
        self.tofilename = tofilename
        self.todata = todata
        self.conditions = conditions
        self.indexes = {}
        
    def process(self):
        self._init_indexes()
        fromfileresult = FileResult(self.fromfilename, [])
        tofileresult = FileResult(self.tofilename, [])
        fromfieldCache = {};
        for row in self.fromdata:
            for condition in self.conditions:
                
                (fromfield, tofield) = condition.fieldtuple
                fromvalue = row[fromfield]
                
                '''
                    0 means has not decided
                    1 means successful match
                    2 means failed match
                '''
                
                if not fromfield in fromfieldCache:
                    fromfieldCache[fromfield] = {fromvalue: 0}
                elif not fromvalue in fromfieldCache[fromfield]:
                    fromfieldCache[fromfield][fromvalue] = 0
                
                if fromfieldCache[fromfield][fromvalue] == 2:
                    continue
                elif fromfieldCache[fromfield][fromvalue] == 1:
                    fromfileresult.result.append(row)
                elif fromfieldCache[fromfield][fromvalue] == 0:
                    if fromvalue in self.indexes[tofield]:
                        fromfileresult.result.append(row)
                        tofileresult.result += self.indexes[tofield][fromvalue]
                        fromfieldCache[fromfield][fromvalue] = 1
                    else:
                        fromfieldCache[fromfield][fromvalue] = 2
                
        return (fromfileresult, tofileresult)
    
    
    def _init_indexes(self):
        
        '''Create index for to file. All the target fields in to file will be added index.
    
            The index format will be like: 
            {tofield1: 
                {tofield1_value1: [rowcontent], 
                 tofield1_value2: [rowcontent],
                 ...
                }, 
             tofield2:
                {tofield2_value1: [rowcontent], 
                 tofield2_value2: [rowcontent]
                 ...
                }, 
                ...
            }
        '''
        
        if len(self.conditions) == 0:
            return
        for row in self.todata:
            for condition in self.conditions:
                tofield = condition.fieldtuple[1]
                toval = row[tofield]
                if tofield in self.indexes:
                    fielddict = self.indexes[tofield]
                    if toval in fielddict:
                        fielddict[toval].append(row)
                    else:
                        fielddict[toval] = [row]
                else:
                    self.indexes[tofield] = {toval: [row]}
            
                
    
'''
Search result
'''
        
class SearchResult:
    
    '''Result for file search
    
        'results' - dict like: {filename1: FileSearchResult2, filename2: FileSearchResult2}
    '''
    
    def __init__(self, results, timecost):
        self.results = results
        self.timecost = timecost
        
class FileResult:
    
    '''Result for file search
    
        'result' - iterable list with dict
    '''
    
    def __init__(self, filename, result):
        self.filename = filename
        self.result = result
        
        
class Search:
    
    ''' Object to process multiple kinds of search
    '''

    def __init__(self, singlefilesearches, joinfilesearches):
        self.singlefilesearches = singlefilesearches
        self.joinfilesearches = joinfilesearches
        
    def process(self):
        
        fileresults = {};
        
        starttime = time.time()
        
#         process file search 
        for singlefilesearch in self.singlefilesearches:
            fileresult = singlefilesearch.process()
            fileresults[fileresult.filename] = fileresult
            
        for joinfilesearch in self.joinfilesearches:
            
#             update data if the data has been filtered in file search
            fromfilename = joinfilesearch.fromfilename
            if fromfilename in fileresults:
                joinfilesearch.fromdata = fileresults[fromfilename].result
            tofilename = joinfilesearch.tofilename
            if tofilename in fileresults:
                joinfilesearch.todata = fileresults[tofilename].result
            
#             using new result to update result 
            (fromfileresult, tofileresult) = joinfilesearch.process()
            fileresults.update({fromfileresult.filename : fromfileresult})
            fileresults.update({tofileresult.filename : tofileresult})
            
        endtime = time.time()
            
        searchresult = SearchResult(fileresults, endtime - starttime)
        
        return searchresult
    

class FieldFilter:
    
    def process(self, filename, fields, data):
        pass

if __name__ == '__main__':
    
#     filecond = ValueSearchCondition("gender", "male")
#     filesearch = SingleFileSearch("test1.csv", DictReader(open("test1.csv")), [filecond], "and")
    filecond = ValueSearchCondition("data2", "2")
    filesearch = SingleFileSearch("scale_output.csv", DictReader(open("scale_output.csv")), [filecond], "and")
    filesearch1 = SingleFileSearch("scale_output1.csv", DictReader(open("scale_output1.csv")), [filecond], "and")
    filesearch2 = SingleFileSearch("scale_output2.csv", DictReader(open("scale_output2.csv")), [filecond], "and")
    filesearch3 = SingleFileSearch("scale_output3.csv", DictReader(open("scale_output3.csv")), [filecond], "and")
    filesearch4 = SingleFileSearch("scale_output4.csv", DictReader(open("scale_output4.csv")), [filecond], "and")
    
    
#     joincond = JoinSearchCondition(("id", "id"))
#     joinsearch = JoinFileSearch("test1.csv", DictReader(open("test1.csv")), "test2.csv", DictReader(open("test2.csv")), [joincond])
    joincond = JoinSearchCondition(("data2", "data2"))
    joinsearch = JoinFileSearch("scale_output.csv", DictReader(open("scale_output.csv")), "scale_output1.csv", DictReader(open("scale_output1.csv")), [joincond])
    joinsearch1 = JoinFileSearch("scale_output1.csv", DictReader(open("scale_output1.csv")), "scale_output2.csv", DictReader(open("scale_output2.csv")), [joincond])
    joinsearch2 = JoinFileSearch("scale_output2.csv", DictReader(open("scale_output2.csv")), "scale_output3.csv", DictReader(open("scale_output3.csv")), [joincond])
    joinsearch3 = JoinFileSearch("scale_output3.csv", DictReader(open("scale_output3.csv")), "scale_output4.csv", DictReader(open("scale_output4.csv")), [joincond])
     
    search = Search([filesearch, filesearch1, filesearch2, filesearch3, filesearch4], [joinsearch, joinsearch1, joinsearch2, joinsearch3])
    result = search.process()
    
    fileresults = result.results
#     print(len(fileresults))
    for filername in fileresults:
        print(filername)
        print(len(fileresults[filername].result))
       

