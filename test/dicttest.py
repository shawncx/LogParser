'''
Created on 2014/11/26

@author: chen_xi
'''


class A:
    
    def __init__(self):
        self._a = "b"
        
    @property
    def a(self):
        print("get")
        return self._a
    
    @a.setter
    def a(self, value):
        print("set")
        self._a = value

if __name__ == "__main__":
    
    a = A()
    a.a = 1
    print(a.a)
    
    l = ["a", "b", "c"]
    
    a = 1
    
#     [a = x for x in l if x == "a"]
    
    print(a)