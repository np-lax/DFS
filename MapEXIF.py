#!/usr/bin/env python
import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS      

##########################################################
#Name:              MapEXIF.py
#Version:           1.0
#Functionality:     Searches images for GPS data and then maps their locations
#by creating a KML file suitable for import to Google Earth or Google Maps
#Author:            Rob Cilla
##########################################################

'''
convertToDegrees: takes in gps coords pulled from EXIF data and converts them to degrees
@param: value of coordinate in minutes
@return: value of GPS coords in degrees
'''           
def minToDeg(value):
    #read in degrees from tuples in value list
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    #read in minutes from tuples in value list
    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    #read in seconds from tuples in value list
    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    #return coord (lat/long) in the degree format 
    return d + (m / 60.0) + (s / 3600.0)  


'''
ripExif: searches for EXIF data on a single file
@param: file to be searched
@return: void
'''        
#pull exif data from a single file    
def searchJPEG(imageFile):
    #open file
    f = open(imageFile, 'r')
    
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
                    #print("DEBUG: EXIF FOUND FOR %s" % imageFile)
    
                    pilImage = Image.open(imageFile)
                    EXIFData = pilImage._getexif()
    
                    #added file name to array
                    rippedExifLst.append("Image: %s" % imageFile)
    
                    #iterate through tuples in EXIF data
                    for tag, value in EXIFData.items():
                        #pull value of EXIF tag
                        tagsValue = TAGS.get(tag, tag)
    
                        if tagsValue == 'GPSInfo':
                            #create a local gps dict
                            gpsDict = {}
                            for gpsRaw in value:
                                #pull GPS tag from raw GPS data
                                gpsTag = GPSTAGS.get(gpsRaw, gpsRaw)
                                #populate dict with tags and values
                                gpsDict[gpsTag] = value[gpsRaw]
    
                                #ensure that the dict has the required info
                                if (gpsDict.has_key("GPSLatitude") and
                                    gpsDict.has_key("GPSLongitude") and 
                                    gpsDict.has_key("GPSLongitudeRef") and
                                    gpsDict.has_key("GPSLatitudeRef")):
                                    
                                    #pull values from the dict
                                    latitude = gpsDict["GPSLatitude"]
                                    latitideRef = gpsDict["GPSLatitudeRef"]
                                    longitude = gpsDict["GPSLongitude"]
                                    longitudeRef = gpsDict["GPSLongitudeRef"]   
                                    
    
                                    #convert lat/long to degrees                                            
                                    lat = minToDeg(latitude)
                                    lon = minToDeg(longitude)
                                    
                                    if (lat and lon):
                                        print("GPS data found for: %s" % os.path.basename(imageFile))
    
                                    #correct for the lat/long reference as necessary
                                    if latitideRef == "S":
                                        lat = 0 - lat
    
                                    if longitudeRef == "W":
                                        lon = 0 - lon
                                        
                                    #build gps output string    
                                    #gpsCoor = {"Latitude: ": lat, "Longitude: ": lon, "Latitude Reference: ": latitideRef, "Longitude Reference: ": longitudeRef}  
                                
                                    #build gps list
                                    tmp = [lat, lon, os.path.basename(imageFile)]
                                    
                                    #add this image's data list to global list
                                    coordList.append(tmp)

                                    #use break to ensure only 1 entry per image
                                    break                    
                    #break out of search loop
                    break
                else:
                    continue
                    #continue searching for other APP1's w/EXIF data
                    #print("DEBUG: No EXIF data found in this APPX ")                   
            #check for EOF or ~64K header size limit
            if data[ptr:ptr+2] == b'0xFFD9' or ptr > 4000:
                #print("DEBUG: No EXIF data found")
                #break out of search loop
                break
            else:
                #keep advancing pointer to search for APP1 header
                ptr = ptr + 2
    else:
        print("DEBUG: No EXIF data found")      

'''
buildKMLObjects: builds KML objects from coords and filenames
@param: cList - list of lists of EXIF GPS data from images
@return: list of KML objects
'''  
def buildKMLObjects(cList):
    #create list to hold kml objects
    KMLLst = []
    #for each list(containing img name + coords) in the cList
    for imageLst in cList:
        #create a KML object (according to google KML documentation)
        tmpKML = (
            '<Placemark>\n'
            '<name>%s</name>\n'
            '<Point>\n'
            '<coordinates>%6f,%6f</coordinates>\n'
            '</Point>\n'
            '</Placemark>\n'
            )%(imageLst[2],imageLst[1],imageLst[0])
        #and add the kml object to the 'master list' of all KML objects created
        KMLLst.append(tmpKML)
    #return the list of KML objects
    return KMLLst

'''
createKMLFile: writes KML objects and necessary formatting info to file
@param: KMLObjectArray - list of KML objects
@param: fname - user-specified output file name
@return: void
'''          
def createKMLFile(KMLObjectArray, fname):
    #open output file
    fname = fname + '.kml'
    outputKML = open(fname, 'w')
    #write KML header to output file
    outputKML.write("<?xml version='1.0' encoding='UTF-8'?>\n<kml xmlns='http://earth.google.com/kml/2.1'>\n<Document>\n")
    #loop through KML Object Array and print each KML object to the file
    for obj in KMLObjectArray:
        outputKML.write(obj)

    #add closing formatting tags to file
    outputKML.write("</Document>\n</kml>")
    
    #close the file
    outputKML.close()
    
    #print completion msg
    print("\nOutput file %s created successfully" % fname) 

if __name__ == '__main__':
  
    #check for file path argument
    if len(sys.argv) != 3:
        print("ERROR - USAGE: mapEXIF.py <file|dir|path> <KML file destination>")
        exit(0)    
    
    #set file path from system argument    
    imagePath = sys.argv[1]
    
    #set output file name from sys arg
    outputFileName = sys.argv[2]
    
    #create path type attribute
    pathType  = "None"
    
    #create list to hold files if path is a dir
    filesList = []
    
    #create list to hold info for each file w/ GPS coords (name + coords)
    coordList = []
    
    #print startup msg
    print("Searching file path for GPS data...\n")
    
    try:
        #check if supplied filepath exists
        if os.path.exists(imagePath):
            #check if path is a file
            if os.path.isfile(imagePath):
                #if so, set flag
                pathType = "File"
                #and add to files list
                filesList.append(imagePath)
            #check if path is a directory
            elif os.path.isdir(imagePath):
                #if so, set flag
                pathType = "Dir"
                #and then populate file list from directory
                for f in os.listdir(imagePath):
                    fullPath = os.path.join(imagePath, f)
                    filesList.append(fullPath)              
            else:
                #if not a file or directory, throw error + exit
                print("ERROR: Supplied path is not a file or a directory. Exiting...")
                sys.exit(0)
        else:
            #if path doesn't exist, throw error + exit
            print("ERROR: Supplied path does not exist. Exiting...")
            sys.exit(0)        
    except IOError:
        #throw error and exif if some error with the file path operations
        print("ERROR: File path error. Exiting...")
        sys.exit(0)    
    
    #if the supplied path is a file
    if pathType == "File":
        #simply search the single file for GPS data
        searchJPEG(filesList[0])
    #if path is a directory    
    elif pathType == "Dir":
        #loop through directory and pass files to the search method one at a time
        for f in filesList:
            searchJPEG(f)
    
    #create list of KML objects using the buildKMLObj method, passing it the list
    #of coords gathered by the search JPEG method
    KMLObjects = buildKMLObjects(coordList)
    
    #if the list of KMLObjects isn't empty
    if KMLObjects:
        #send the list and specified file name to the file writing method
        createKMLFile(KMLObjects, outputFileName)
    else:
        print("No images with GPS data found. Exiting...")