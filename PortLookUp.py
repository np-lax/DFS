#!/usr/bin/env python

##########################################################
#Name:              PortLookUp.py
#Version:           0.1
#Functionality:     Create a dictionary of port numbers and then print out each port's description
#Author:            Rob Cilla
##########################################################

'''
CreatePortDictionary: function to build a dictionary of ports and descriptions from a text file
@param: PortTextFile - a file that holds the port numbers and their descriptions
@return: dictionary with populated ports, protocols and descriptions
'''
def CreatePortDictionary(PortTextFile):
    #create dictionary object
    portDictionary = {}

    #loop to run through the file containing the port information
    for line in PortTextFile:
        #use try/catch to skip any junk in the txt file
        try:
            #split each line into port number, protocol and description
            splitLine = line.split('  ',3)
            #check to see if the dictionary already has an entry for the port number read in from the file
            #splitLine[0] - protocol / splitLine[1] - port number / splitLine[2] - description
            if(portDictionary.has_key(splitLine[1])):
                #if yes, add new description and protocol to entry without creating new entry
                #dict[port][protocol] = [description]
                portDictionary[splitLine[1]][splitLine[0]] = splitLine[2]
            else:
                #if not, create new entry at the port # using the protocol and description
                #dict[port] = {protocol:description}
                portDictionary[splitLine[1]] = {splitLine[0]:splitLine[2]}
        #catch any errors thrown during the splitting or indexing, but continue through loop
        except IndexError:
            continue
    #return populated dictionary    
    return portDictionary
'''
PortLookup: function to look up port descriptions from the portDictionary
@param: portNumber - port number to get info for
@param: portDictionary - dictionary of ports, protocols and descriptions
@return: strings containing udp and tcp port descriptions
'''
def PortLookup(portNumber, portDictionary):
    #set descriptions to unassigned. This shows any ports not in the dictionary as unassigned
    udpPortDescription = 'unassigned'
    tcpPortDescription = 'unassigned'
    
    #try to find a description linked to a TCP key for the given port number
    try:
        tcpPortDescription = portDictionary[str(portNumber)]['TCP']
    except KeyError:
        pass
        
    #try to find a description linked to a UDP key for the given port number
    try:
        udpPortDescription = portDictionary[str(portNumber)]['UDP']  
    except KeyError:
        pass
        
    #remove leading and trailing whitespaces to help with printing later
    tcpPortDescription = tcpPortDescription.strip()
    udpPortDescription = udpPortDescription.strip()

    #return both descriptions
    return tcpPortDescription, udpPortDescription

def main():
    #open txt file of ports for reading
    PortTextFile = open('PortList.txt')
    #pass txt file to method to create dictionary
    portDictionary = CreatePortDictionary(PortTextFile)
    #close the txt file
    PortTextFile.close()
    
    #print header for output
    print("PORT  TCP INFO \t\t\t    UDP INFO")
    
    #run through port numbers 0-65506
    for portNum in range (0, 65507): 
        #pull tcp/udp info from the portLookup function. Pass it the current port number and the created dictionary
        tcp_info,udp_info = PortLookup(portNum, portDictionary)
        
        #create an output row
        row = '{:>4}  {:>8}  {:>30}'.format(portNum, tcp_info, udp_info)
        #print the output
        print(row)

if __name__ == "__main__":
    main()



