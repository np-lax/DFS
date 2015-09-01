#!/usr/bin/env python

##########################################################
#Name:              first.py
#Version:           0.1
#Functionality:     Prints out ASCII hex values and occurance count for each char in a given string
#Author:            Rob Cilla
##########################################################

#input string
testString = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"

#list to hold character count
charCount = [0] * 53


def countLetters(letter, array):
        alphaPos = ord(letter)
        
        if alphaPos <= 91:
                #print "place: " + str(ord(letter)-65)
                array[alphaPos-65] = array[alphaPos-65] + 1
        else:
                #print 'place: ' + str(ord(letter)-70)
                array[alphaPos-70] = array[alphaPos-70] + 1
                
        return array

def printCount(array):
        print '#####################'
        print 'CHAR\tOCCURANCES'
        for x in range(len(array)):
                if array[x] and x <= 26:
                        print chr(x+65) + '\t' + str(array[x])
                elif array[x] and x > 26:
                        print chr(x+70) + '\t' + str(array[x])
        return ' '
                        
        
print 'CHAR\t HEX'        

for letter in testString:
        charCount = countLetters(letter, charCount)
        print letter + '\t{:3x}1'.format(ord(letter)).upper()
        

print printCount(charCount)
    
    