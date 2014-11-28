'''
Created on 2014/11/27

@author: chen_xi

'''


class Test:

    def getData(self):
        for i in range(10):
            yield i
            

if __name__ == "__main__":
    
    t = Test()
    for i in t.getData():
        print(i)