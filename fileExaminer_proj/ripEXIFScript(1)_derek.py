import os
import sys

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


filePath = sys.argv[1]

for fn in os.listdir(filePath):
    
     
    joinPath = os.path.join(filePath, fn)
    
    
    pilImage = Image.open(joinPath)
    EXIFData = pilImage._getexif()
    
    #print "File Name: ", os.path.basename(joinPath)
    
    for tag, theValue in EXIFData.items():
        tagsValue = TAGS.get(tag, tag)
        
        if tagsValue == 'Artist':
            artistInfo = EXIFData.get(tag)
            #print "Artist: ", artistInfo
        
        if tagsValue == 'DateTimeOriginal':
            dateTime = EXIFData.get(tag)
            #print "Date & Time: ", dateTime
            
        if tagsValue == 'Make':
            cameraMake = EXIFData.get(tag)
            #print "Camera Make: ", cameraMake
            
        if tagsValue == 'Model':
            cameraModel = EXIFData.get(tag)
            #print "Camera Model: ", cameraModel
            
        if tagsValue == 'GPSInfo':
            gpsInfo = EXIFData.get(tag)
            #print "GPS Data: ", gpsInfo  
            
    print "File Name: ", os.path.basename(joinPath)
    print "Artist: ", artistInfo
    print "Date & Time: ", dateTime
    print "Camera Make: ", cameraMake
    print "Camera Model: ", cameraModel
    print "GPS Data: ", gpsInfo
            
     