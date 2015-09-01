#!/usr/bin/env python

##########################################################
#Name:              mp.py
#Date:              18 Apr 2015
#Functionality:     use multithreading to hash a file while simultaniously searching for phone numbers
#Author:            Rob Cilla
##########################################################

import sys
import time
import multiprocessing
import hashlib
import re

'''
Hashfile: performs sha512 hash on file
@param: queue - queue to hold process result
@param: fileName - name of file to be hashed
@return: updates queue with function completion time
'''
def HashFile(queue, fileName):
    #use try/catch to attempt to open file with name fileName
    try:
        targetFile = open(fileName, 'r')
        fToHash = targetFile.read()
        targetFile.close()
    except IOError:
        print('%s cannot be opened...' % fileName)
        return None 
    
    try:
        #initalize hash object w/ sha512
        hashObj = hashlib.sha512()
        #update with read-in file data to get hash
        hashObj.update(fToHash)
        
        #check if hashObj is null
        if hashObj:
            #if not print header
            print('SHA512 HASH OF %s:' % fileName)
            #and print out hexdigest of calculated hash
            print(hashObj.hexdigest() + '\n') 
        #get rid of the hash object when finished with it
        del hashObj
    #exit the prgm if the hashing throws an error
    except Exception:
        print("ERROR: Problem calculating hash, exiting...")
        exit(0)
    #update queue with time the function finished    
    queue.put(time.time())

'''
SearchFile: searches for formatted data in file using supplied regex
@param: queue - queue to hold process result
@param: fileName - name of file to be hashed
@param: regExp - compiled regular expression to search for something
@return: updates queue with function completion time
'''    
def SearchFile(queue, fileName, regExp):
    #use try/catch to attempt to open file with name fileName  
    try:
        fToSearch = open(fileName, 'r')
    except IOError:
            print("%s cannot be opened..." % fileName)
            return None     
    #print header
    print('PHONE NUMBERS FOUND IN %s:' % fileName)
    #go through each line in the file
    for line in fToSearch:
        #search the line for the supplied regular expression
        result = re.search(regExp, line)
        #if there is a match
        if result:
            #print it
            print(result.group(0))
      
    print('\n')  
    
    #close the file        
    fToSearch.close() 
    #update queue with function completion time
    queue.put(time.time())
    
#MAIN   
def main():
    #check that there was a filename argument passed
    if len(sys.argv) != 2:
        print("ERROR: Please include the name of the file as an argument")
        exit(0)
    #pull filename from argument    
    fileName = sys.argv[1]
    
    #setup queue to hold thread results
    q = multiprocessing.Queue()
    #compile regular expression to search for phone numbers of various formats
    regex = re.compile("1?-?([(]\d{3}[)]|\d{3})?(-?|\s)\d{3}(-?|\s)\d{4}")
    
    #set up processes to call functions while passing the appropriate parameters
    hashProcess = multiprocessing.Process(target=HashFile, args=(q, fileName,))
    searchThread = multiprocessing.Process(target=SearchFile, args=(q, fileName, regex))
    
    #record thread start times
    startTime = time.time()
    #start the threads
    hashProcess.start()
    searchThread.start()
    
    #get the time each thread finished (order is determined by which thread was executed first)
    hTime = q.get() - startTime
    sTime = q.get() - startTime
    
    #join the processes to close them
    hashProcess.join()
    searchThread.join()
    #calculate overall completion time
    endTime = time.time() - startTime
    
    #print timing results
    print('Hashing thread completed in %s seconds' % hTime)
    print('Search thread completed in %s seconds' % sTime)
    print('Entire program completed in %s seconds' % endTime)

if __name__ == "__main__":
    main()
