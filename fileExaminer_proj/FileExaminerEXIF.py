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
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

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
        #added attribs
        #exifArray is a list of lists to hold EXIF data for each image
        self.exifArray  = []
        self.fileList   = []
        
        
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
                    self.fileList.append(theFile)
                # Is this a real file?
                elif os.path.islink(theFile):
                    self.fileType = "Link"
                # Is This filename actually a directory?
                elif os.path.isdir(theFile):
                    self.fileType = "Directory"
                    #populate file list
                    for f in os.listdir(theFile):
                        fullPath = os.path.join(theFile, f)
                        self.fileList.append(fullPath)
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
        print("closed")
        
    def flattenList(self, lst):
        tmpLst = []
        for item in lst:
            for i in item:
                tmpLst.append(i)
                
        return tmpLst
        
    def convertToDegrees(self, value):
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)
         
        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)
         
        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)
         
        return d + (m / 60.0) + (s / 3600.0)           
    
   
    def printEXIFData(self):
        #use self.FileList and self.exifArray to print data collected from images with EXIF data
        #FileList has the file names and the exifArray is a list of lists of exif data
        
        #check if any EXIF data was found in the file/dir - if so, print it out
        if len(self.exifArray) > 0:
            print "====================================================================="
            print "EXIF DATA"
            #search through the overall exifArray for lists
            for lst in self.exifArray:
                print("-------------")
                #roll through each list and print the contents
                for item in lst:
                    print(item)
                print("-------------")
            
    '''
    ripExif: searches for EXIF data on a single file
    @param: FileExaminer Object
    @return: void
    '''        
    #pull exif data from file    
    def ripExif(self):
        #run through dir or single file
        for files in self.fileList:
            #open first file
            f = open(files, 'r')
            
            #read data from file
            data = f.read()

            #initalize pointer for this file
            ptr = 0
            
            #close file
            f.close()
            
            #initalize exif list for file
            rippedExifLst = [] 
            
            #check for JPEG header
            if data[ptr:ptr+2] == b'\xFF\xD8': 
                #print("DEBUG: IT'S A JPEG!")
                
                #if JPEG, start search loop
                while 1:                
                    #check for APP1 header
                    if data[ptr:ptr+2] == b'\xFF\xE1':
                        #print("DEBUG: APP1 data found")
                        #if APP1 found, check for EXIF data
                        if data[ptr + 4:ptr + 8] == b"Exif":  
                           #print("DEBUG: EXIF FOUND FOR %s" % files)

                            pilImage = Image.open(files)
                            EXIFData = pilImage._getexif()
                                                   
                            #added file name to array
                            rippedExifLst.append("Image: %s" % files)
            
            
                            for tag, value in EXIFData.items():
                                tagsValue = TAGS.get(tag, tag)

                                if tagsValue == 'Artist':
                                    artistInfo = EXIFData.get(tag)
                                    rippedExifLst.append('Artist: %s' % artistInfo)
                            
                                if tagsValue == 'DateTimeOriginal':
                                    dateTime = EXIFData.get(tag)
                                    rippedExifLst.append('Date/Time: %s' % dateTime)
                            
                                if tagsValue == 'Make':
                                    cameraMake = EXIFData.get(tag)
                                    rippedExifLst.append('Camera Make: %s' % cameraMake)
                                    
                                if tagsValue == 'Model':
                                    cameraModel = EXIFData.get(tag)
                                    rippedExifLst.append('Camera Model: %s' % cameraModel)
                            
                                if tagsValue == 'GPSInfo':
                                    gpsDict = {}
                                    for gpsRaw in value:
                                        gpsTag = GPSTAGS.get(gpsRaw, gpsRaw)
                                        gpsDict[gpsTag] = value[gpsRaw]
                            
                                        if (gpsDict.has_key("GPSLatitude") and
                                            gpsDict.has_key("GPSLongitude") and 
                                            gpsDict.has_key("GPSLongitudeRef") and
                                            gpsDict.has_key("GPSLatitudeRef")):
                            
                                            latitude = gpsDict["GPSLatitude"]
                                            latitideRef = gpsDict["GPSLatitudeRef"]
                                            longitude = gpsDict["GPSLongitude"]
                                            longitudeRef = gpsDict["GPSLongitudeRef"]
                                                                                        
                                            lat = self.convertToDegrees(latitude)
                                            lon = self.convertToDegrees(longitude)
                            
                                            if latitideRef == "S":
                                                lat = 0 - lat
                            
                                            if longitudeRef == "W":
                                                lon = 0 - lon
                            
                                            gpsCoor = {"Latitude: ": lat, "Longitude: ": lon, "Latitude Reference: ": latitideRef, "Longitude Reference: ": longitudeRef}  
                                   
                                            rippedExifLst.append('GPS Data: %s' % gpsCoor)
                                            break
  
                            
                            #update overall object EXIF data array with list for this image
                            self.exifArray.append(rippedExifLst)
                            
                            #break out of search loop
                            break
                        else:
                            continue
                            #continue searching for other APP1's w/EXIF data
                            #print("DEBUG: No EXIF data found in this APPX ")                   

                        
                    #check for EOF or ~64K header size limit
                    if data[ptr:ptr+2] == b'0xFFD9' or ptr > 4000:
                        #print("DEBUG: NO EXIF data found in image")
                        #break out of search loop
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
    
    print("File Examainer Object Test \n")

    filePath = sys.argv[1]
    FEobj = FileExaminer(filePath)
    
    if FEobj.lastError == "OK":
    
        print("MAC  Times: ", FEobj.macTimes)
        print("File  Size: ", FEobj.fileSize)
        print("Owner ID:   ", FEobj.uid)
        print("Group ID:   ", FEobj.gid)
        print("File  Type: ", FEobj.fileType)
        print("Mount Point:", FEobj.mountPoint)
        print("File Read:  ", FEobj.fileRead)
        
        if FEobj.fileRead:
            if FEobj.hashFile("SHA1"):
                print("SHA1: ",FEobj.sha1)
            else:
                print(FEobj.lastError)
        
        #perform the EXIF search
        FEobj.ripExif()
        
        #print the EXIF data (if any)
        FEobj.printEXIFData()
       
        del FEobj
        
    else:
        print("Last Error: ", FEobj.lastError)
        