import os 
from xml.etree import ElementTree
import dicttoxml
import collections

#get file path
filename = "test.xml"
fullFile = os.path.abspath(filename)

#load xml
tree = ElementTree.parse(fullFile)

#------------------------------------------------
#Create a dictionnary like this : {chapter:text}
#------------------------------------------------
#trying to find all chapter number with this shape :
"""
<text font="ABCDEE+Georgia,Bold" bbox="302.330,703.065,309.680,717.660" colourspace="DeviceGray" ncolour="0" size="14.595">1</text>
<text font="ABCDEE+Georgia,Bold" bbox="309.650,703.065,313.460,717.660" colourspace="DeviceGray" ncolour="0" size="14.595"> </text>
"""
#store all chapter and text associated
tabTitle = {}

#find all textbox
textboxs = tree.findall(".//textbox")

for textbox in textboxs:

    #store temp chapter number
    titleNumber = ''
    
    #store temp text
    tempText = ''
    
    #get all text in textbox
    texts = textbox.findall(".//text")

    for text in texts:
        try: #we try because all text block doesnt have attrib

            tempText = text.text

            #get all bold text, its maybe a chapter number
            if text.attrib['font'] == "ABCDEE+Georgia,Bold":
                if text.text.isdigit(): #if its a digit , store it
                    titleNumber = titleNumber + text.text 
                elif text.text == ' ' and len(titleNumber) != 0: #if next digit is ' ' this is a chapter
                    tabTitle[titleNumber] = ''
                    titleNumber = ''
                    tempText = '' #reset text buffer
                else : # but if next text is not a digit or a ' ' then erase temp title number
                    titleNumber = ''
            
            #if at least 1 title is found associate text with chapter
            if len(tabTitle) > 0:
                tabTitle[list(tabTitle.keys())[-1]] = tabTitle[list(tabTitle.keys())[-1]] + tempText
        
        except:# ?? no attrib == new paragraph??
            pass

# minor modification 

#erase number at the end of text, its the number for the next chapter
for key in tabTitle:
    if int(key) < len(tabTitle): # dont need to modify the last element
        #need to find the last number that match the next chapter number
        lastIndex = 0
        while lastIndex != -1: #we need to iterate to find only the last index
            index = lastIndex
            lastIndex = tabTitle[key].find(str(int(key)+1), index+1) #find index of next number matching
        
        tabTitle[key] = tabTitle[key][:index] #shorten string to erase last number

#------------------------------------------------
#search link in each chapter's text
#------------------------------------------------
#we need to create another dictionnary to hold all link
# like this : {chapter:[link1,...,linkX]}
linkDict = {}
# link in text have this format ' au XXX'

for key in tabTitle: #iterate through all text
    bufferLink = []
    indexLink = 0

    while indexLink != -1: #there are maybe many link in a text

        link = ''

        #First try to find ' au ' in string
        indexLink = tabTitle[key].find(' au ', indexLink+1) 
        if indexLink > 0: # if one instance of 'au ' is found
            
            # if index+4 is digit, this is a link with 1,2 or 3 digit max.
            if tabTitle[key][indexLink+4].isdigit():
                link = link + tabTitle[key][indexLink+4]

                if tabTitle[key][indexLink+5].isdigit():
                    link = link + tabTitle[key][indexLink+5]

                    if tabTitle[key][indexLink+6].isdigit():
                        link = link + tabTitle[key][indexLink+6]
                
                bufferLink.append(link) #store link in buffer
            
    linkDict[key] = bufferLink # finally store in the dictionnary

#------------------------------------------------
#Generate XML
#------------------------------------------------
"""
<chapter>
    <id>XXX</id>
    <text>XXXX</text>
    <link>XXX</link>
    <link>XXX</link>
</chapter>
"""

xmlRoot = ElementTree.Element('root')

for key in tabTitle:

    xmlChapter = ElementTree.SubElement(xmlRoot,'chapter')

    xmlId = ElementTree.SubElement(xmlChapter,'id')
    xmlId.text = key

    xmlText = ElementTree.SubElement(xmlChapter, 'text')
    xmlText.text = tabTitle[key]

    if len(linkDict[key]): #if there is some link 
        for link in linkDict[key]:
            xmlLink = ElementTree.SubElement(xmlChapter, 'link')
            xmlLink.text = link 


#store in a file
tree = ElementTree.ElementTree(xmlRoot)
tree.write("6 - l'oeil du Dragon.xml")
tree.write("6 - l'oeil du Dragon.html", method='html')