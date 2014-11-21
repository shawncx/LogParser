'''
@author: chen_xi
'''


class FileModel:
    
    def __init__(self, filename, searchconds, relation, joincondtuples, displayfields):
        self.filename = filename
        self.searchconds = searchconds
        self.relation = relation
        self.joincondtuples = joincondtuples
        self.displayfields = displayfields
