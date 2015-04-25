'''
Copyright (c) 2014 Chet Hosmer

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial 
portions of the Software.

'''

import os           # Python Standard Library OS Module
import time         # Python Standard Library Time Module
import hashlib      # Python Standard Library Hashing Methods
import sys


# Class: FileExaminer Class
#
# Desc: Handles all methods related to File Based Forensics
# Methods  constructor:    Initializes the Forensic File Object and Collects Basic Attributes
#                          File Size
#                          MAC Times
#                          Reads file into a buffer
#          hashFile:       Generates the selected one-way hash of the file
#          destructor:     Deletes the Forensic File Object

class FileExaminer:

    # Constructor
    
    def __init__(self, theFile):
        
        #Attributes of the Object
        
        self.lastError  = "OK"
        self.mactimes   = ["","",""]
        self.fileSize   = 0
        self.fileType   = "unknown"
        self.uid        = 0
        self.gid        = 0
        self.mountPoint = False
        self.fileRead   = False
        self.md5        = ""
        self.sha1       = ""
        #added
        self.exifPresent= False
        
        
        try:
            
            if os.path.exists(theFile):
                # get the file statistics
                theFileStat =  os.stat(theFile)
                
                # get the MAC Times and store them in a list
                
                self.macTimes = []
                self.macTimes.append(time.ctime(theFileStat.st_mtime))
                self.macTimes.append(time.ctime(theFileStat.st_atime))
                self.macTimes.append(time.ctime(theFileStat.st_ctime))
                
                # get and store the File size
                
                self.fileSize = theFileStat.st_size
                
                # Get and store the ownership information
                
                self.uid = theFileStat.st_uid
                self.gid = theFileStat.st_gid
                
                if os.path.isfile(theFile):
                    self.fileType = "File"
                # Is this a real file?
                elif os.path.islink(theFile):
                    self.fileType = "Link"
                # Is This filename actually a directory?
                elif os.path.isdir(theFile):
                    self.fileType = "Directory"
                else:
                    self.fileType = "Unknown"
                
                # Is the pathname a mount point?
                if os.path.ismount(theFile):
                    self.mountPoint = True
                else:
                    self.mountPoint = False        
                
                # Is the file Accessible for Read?
                
                if os.access(theFile, os.R_OK) and self.fileType == "File":
                    
                    # Open the file
                    fp = open(theFile, 'rb')
                    
                    # Assume we have enough space 
                    self.buffer = fp.read()
                   
                    # Close the file we have the entire file in memory
                    fp.close()
                    
                    self.fileRead = True
                
                else:
                    self.fileRead = False
                    
            else:
                self.lastError = "File does not exist"
                
        except:
            self.lastError = "File Exception Raised"       

    # partially completed hash file method
    
    #added
    def getPath(self):
        return self.path
    
    def hashFile(self,hashType):
        
        # Only supports two Hash Types currently
        
        try:
            
            if hashType == "MD5":
                hashObj = hashlib.md5()
                hashObj.update(self.buffer)
                self.md5 = hashObj.hexdigest().upper()
                self.lastError = "OK"
                return True
            elif hashType == "SHA1":
                hashObj = hashlib.sha1()
                hashObj.update(self.buffer)
                self.sha1 = hashObj.hexdigest().upper()
                self.lastError = "OK"
                return True
            else:
                self.lastError = "Invalid Hash Type Specified"
                return False
        except:
            self.lastError = "File Hash Failure"
            return False
            
    def __del__(self):
        print "closed"
    '''
    ripExif: searches for EXIF data on a single file
    @param: FileExaminer Object
    @return: void
    '''        
    #pull exif data from file    
    def ripExif(self):
        #initalize pointer
        ptr = 0   
        #copy data from object buffer to work with
        data = self.buffer
        
        #check for JPEG header
        if data[ptr:ptr+2] == b'\xFF\xD8': 
            print("DEBUG: IT'S A JPEG!")
            #if JPEG, start running through file
            while 1:                
                #check for APP1 header
                if data[ptr:ptr+2] == b'\xFF\xE1':
                    print("DEBUG: APP1 data found")
                    #if APP1 found, check for EXIF data
                    if data[ptr + 4:ptr + 8] == b"Exif":  
                        print("DEBUG: EXIF FOUND!!")
                        #Process EXIF data here
                    else:
                        print("DEBUG: No EXIF data found in this APPX ")
                    break
                #check for EOF or ~64K header size limit
                elif data[ptr:ptr+2] == b'0xFFD9' or ptr > 4000:
                    print("DEBUG: NO EXIF data found in image")
                    break
                else:
                    #keep advancing pointer to search for APP1 header
                    ptr = ptr + 2
       
        
# End Forensic File Class ====================================

#
# ------ MAIN SCRIPT STARTS HERE -----------------
#

if __name__ == '__main__':
    
    #set bool defaults
    imgFile = False
    imgDir = False
    
    #check for args
    if len(sys.argv) != 2:
        print("ERROR - USAGE: FileExaminer.py <file|dir|path>")
        exit(0)    
    
    # a forensic file object
    
    print "File Examainer Object Test \n"
    
    #FEobj = FileExaminer("c:\\TEST\\image.jpg")
    #FEobj = FileExaminer("c:\\")
    FEobj = FileExaminer(sys.argv[1])
    #print("PATH: %s" % sys.argv[1])
    
    if FEobj.lastError == "OK":
    
        print "MAC  Times: ", FEobj.macTimes
        print "File  Size: ", FEobj.fileSize
        print "Owner ID:   ", FEobj.uid
        print "Group ID:   ", FEobj.gid
        print "File  Type: ", FEobj.fileType
        print "Mount Point:", FEobj.mountPoint
        print "File Read:  ", FEobj.fileRead
        
        if FEobj.fileRead:
            if FEobj.hashFile("SHA1"):
                print "SHA1: ",FEobj.sha1
            else:
                print FEobj.lastError
        
        
        #BEGIN EXIF DATA SEARCH
        #check if path is dir or file
        if FEobj.fileType == 'File':
            #path is file, pass to ripEXIF method
            result = FEobj.ripExif()
        #elif FEobj.fileType == 'Directory':
            #loop through files in directory, passing them to ripEXIF method
            #maybe use a list to hold data from multiple objects? or print directly from method? 

       
        del FEobj
        
    else:
        print "Last Error: ", FEobj.lastError
        