'''
@author: chen_xi
'''


class FileModel:
    
    def __init__(self, fileName, searchConds, relation, joinCondTuples, displayFields):
        self.fileName = fileName
        self.searchConds = searchConds
        self.relation = relation
        self.joinCondTuples = joinCondTuples
        self.displayFields = displayFields
