'''
@author: chen_xi
'''


class FileModel:
    
    def __init__(self, reader, searchConds, relation, joinCondTuples, \
                 displayFields):
        self.reader = reader
        self.searchConds = searchConds
        self.relation = relation
        self.joinCondTuples = joinCondTuples
        self.displayFields = displayFields
        
