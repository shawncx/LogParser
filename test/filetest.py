'''
Created on 2014/11/27

@author: chen_xi
'''


if __name__ == "__main__":
    
    log = "2014-11-20 16:30:27,624 [main] DEBUG jp.co.worksap.cim.webapp.UserAgentControlFilter - UserAgentControlFilter: UAControlFilter is initialized.\n"
    
    filename = "../test-resource/scale_log1.log"
    
    file = open(filename, 'w')
    
    for i in range(10000000):
        file.write(log)