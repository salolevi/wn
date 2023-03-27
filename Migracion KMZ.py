import fme
import fmeobjects
import re

def checkQuotes(s):
    s = s.replace('"', '')
    s = s.replace("'", "")
    s = s.replace("\t", "")
    s = s.replace(":", "")
    s = s.replace("|", " ")
    return s

# network types: 1 == troncal, 2 == distribucion, 3 == clientes, 4 == infraestructura, 5 == areas de zonas
def getOcfg1(fType, fFolder):
    ocfg1 = {  
                "NAP1N" : ["go/fo/cie", "2N1", "1"],
                "NAP1LL": ["go/fo/cie", "2N1", "1"],
                "NAP2N" : ["go/fo/cie", "2N2", "1"],
                "NAP16LL" : ["go/fo/cie", "2N2", "1"],
                "NAP16NOI" : ["go/fo/cie", "2N2", "1"],
                "NODO" : ["go/fo/cie", "NODO", "1"],
                "METRO" : ["go/fo/cie", "CM", "1"], 
                "BOTELLA" : ["go/fo/cie", "1N", "1"],
                "NAPEM" : ["go/fo/cie", "1N", "1"],
                "CLMAY" : ["go/fo/cli", "CLIENTE", "1"],
            }
    ocfg2 = {   
                "4" : ["gc/fo", "4", "1"], 
                "8" : ["gc/fo", "8", "1"], 
                "12" : ["gc/fo", "12", "1"], 
                "16" : ["gc/fo", "16", "1"], 
                "24" : ["gc/fo", "24", "1"], 
                "36" : ["gc/fo", "36", "1"], 
                "48" : ["gc/fo", "48", "1"], 
            }
    
    ret = None
    
    if fType == "fme_point":
        return ocfg1[fFolder];

    elif fType == "fme_line":
        pelos = re.sub("[^0-9]", "", fFolder)
        return ocfg2[pelos]
    
    return None
        
        
  
def getFolder(parent, folderList):
    for folder in folderList:
        id = folder.getAttribute("kml_name")
        if parent == id:
            return folder
    return None
    
def getStyle(style, styleList, styleMapList):
    st1 = style.strip("#")
        
    # check if it is a StyleMap
    for st in styleMapList:
        id = st.getAttribute("kml_id")
        if st1 == id:
            st1 = st.getAttribute("kml_style_url_normal")
            st1 = st1.strip("#")
            break
    
    # check for the style
    for st in styleList:
        id = st.getAttribute("kml_id")
        if st1 == id:
            return st
            
    return None
    
class FeatureProcessor(object):
    def __init__(self):
        self.featureList = []
        self.folderList = []
        self.styleList = []
        self.styleMapList = []
        self.featureTypeList = [ "document", "folder", "placemark", "style", "stylemap"]
    
    def input(self, feature):
        fmeFeatureType = feature.getAttribute("fme_feature_type").strip().lower()
        if fmeFeatureType in self.featureTypeList:
            self.featureList.append(feature)
        elif fmeFeatureType == "folder":
            print("hola")
            self.folderList.append(feature)
        elif fmeFeatureType == "style":
            self.styleList.append(feature)
        elif fmeFeatureType == "stylemap":
            self.styleMapList.append(feature)

    def close(self):
        ffo = open(r"C:\Users\Salo\WN\fo" + ".txt","w")
        ffocfg = open(r"C:\Users\Salo\WN\ocfg" + ".txt","w")
        ffval = open(r"C:\Users\Salo\WN\val" + ".txt","w")
        ffsidx = open(r"C:\Users\Salo\WN\sidx" + ".txt","w")
        ffv = open(r"C:\Users\Salo\WN\v"+ ".txt","w")
        ffgeoidx = open(r"C:\Users\Salo\WN\geoidx" + ".txt","w")
        companyId = "11"
        id = 0
        logs = "1679577251..1."
        # print(self.folderList)
                
        for feature in self.featureList:
            # A - store kml folders in @folder
            fList = []
            parent = feature.getAttribute("kml_parent")
            parentType = feature.getAttribute("kml_parent_type")
            while parentType == "Folder":
                folder = getFolder(parent, self.folderList)
                if folder != None:
                    parent = folder.getAttribute("kml_parent")
                    parentType = folder.getAttribute("kml_parent_type")
                    name = folder.getAttribute("kml_name")
                    fList.append(name);
                else:
                    parentType = None
            
            # B - write @kmlId == kml_id, @oName == kml_name, @comm == kml_description, @oStyle == kml_style_url, @folder == fFolder
            fFeatureType = feature.getAttribute("fme_feature_type")
            fType = feature.getAttribute("fme_type")
            fId = feature.getAttribute("kml_id")
            fName = feature.getAttribute("kml_name")
            fStyle = feature.getAttribute("kml_style_url")
            fFolder = ""
            ss = "%s|%s|%s|%s|%s|%s"%(fFeatureType, fType, fId, fName, fStyle, fFolder)
            
            # C - graphic styling such as @oColor == kml_iconstyle_color
            style = getStyle(fStyle, self.styleList, self.styleMapList)
            if (style == None):
                ss = "%s - %s unexistent kml_style_url"%(ss, fStyle)
            else:
                if fType == "fme_line":
                    kmlColor = getKmlColor(style.getAttribute("kml_linestyle_color"))
                    width = style.getAttribute("kml_linestyle_width")
                    ss = "%s|%s~%s"%(ss, kmlColor, width)    
                elif fType == "fme_area":
                    kmlColor = getKmlColor(style.getAttribute("kml_linestyle_color"))
                    kmlBkColor = getKmlColor(style.getAttribute("kml_polystyle_color"))
                    width = style.getAttribute("kml_linestyle_width")
                    ss = "%s|%s~%s~%s"%(ss, kmlColor, kmlBkColor, width)    
                elif fType == "fme_point":
                    icon = style.getAttribute("kml_icon_href")
                    if icon != None:
                        idx = icon.rfind("/")
                        icon = icon[idx+1:]
                    kmlColor = getKmlColor(style.getAttribute("kml_iconstyle_color"))
                    scale = style.getAttribute("kml_iconstyle_scale")
                    ss = "%s|%s~%s~%s"%(ss, kmlColor, icon, scale)    
                else:
                    pass
                    #ss = "%s - %s unknown fme_type"%(ss, fType)
            
            # D - define ocfg and @oType
            ocfg = getOcfg1(fType, fFolder)
            if ocfg != None:
                ss = "%s|%s|%s|%s"%(ocfg[2], ocfg[0], ocfg[1], ss)
                
                # E - write files    
                id = id + 1
                strId = "%s.%s.%d"%(companyId, ocfg[2], id)
                ffo.write("SET " + strId + " \"" + logs + "\"\n")                                    # SET 10.1.1 "0..1."
                ffocfg.write("SADD " + strId + ":ocfg \"" + logs + ":" + ocfg[0] + "\"\n")           # SADD 10.1.1:ocfg "0..1.:a/cgc/a"
            
                # write values
                fName = checkQuotes(fName)                
                ffval.write("SADD " + strId + ":val \"" + logs + ":@oName|" + fName + "|0\"\n")      # SADD 10.1.1:val "0..1.:@oName|CAMPO INDIO|0"
                fId = checkQuotes(fId)
                ffval.write("SADD " + strId + ":val \"" + logs + ":@kmlId|" + fId + "|0\"\n")
                if fDesc != "":
                    fDesc = checkQuotes(fDesc)
                    ffval.write("SADD " + strId + ":val \"" + logs + ":@comm|" + fDesc + "|0\"\n")
                fStyle = checkQuotes(fStyle)
                ffval.write("SADD " + strId + ":val \"" + logs + ":@oStyle|" + fStyle + "|0\"\n")
                fFolder = checkQuotes(fFolder)
                ffval.write("SADD " + strId + ":val \"" + logs + ":@folder|" + fFolder + "|0\"\n")
                if ocfg[1] != "":
                    ffval.write("SADD " + strId + ":val \"" + logs + ":@oType|" + ocfg[1] + "|0\"\n")
                if fType == "fme_line":
                    if kmlColor != None:
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@color|" + kmlColor + "|0\"\n")
                    if width != None:
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@width|" + width + "|0\"\n")
                elif fType == "fme_area":
                    if kmlColor != None:
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@color|" + kmlColor + "|0\"\n")
                    if kmlBkColor != None:
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@bkColor|" + kmlBkColor + "|0\"\n")
                    if width != None:
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@width|" + width + "|0\"\n")
                elif fType == "fme_point":
                    if kmlColor != None:
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@color|" + kmlColor + "|0\"\n")
                    if icon != None:
                        icon = checkQuotes(icon)
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@icon|" + icon + "|0\"\n")
                    if scale != None:
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@scale|" + scale + "|0\"\n")
            
                ffsidx.write("ZADD " + companyId + ".@oName.sidx 0 \"" + fName + ":" + logs + ":" + strId + "\"\n")       # ZADD 10.@oName.sidx 0 "CAMPO INDIO:0..1.:10.1.1"
                ffsidx.write("ZADD " + companyId + ".@kmlId.sidx 0 \"" + fId + ":" + logs + ":" + strId + "\"\n")
                ffsidx.write("ZADD " + companyId + ".@folder.sidx 0 \"" + fFolder + ":" + logs + ":" + strId + "\"\n")
                if fDesc != "":
                    ffsidx.write("ZADD " + companyId + ".@comm.sidx 0 \"" + fDesc + ":" + logs + ":" + strId + "\"\n")
                                
                geoidxId = "GEOADD " + companyId + "." + ocfg[2] + ":geoidx "
                
                # write vertex
                n = feature.numVertices()
                i = 0
                while i < n:
                    latlon = feature.getCoordinate(i)
                    sLat = "%.13f"%(latlon[1])
                    sLon = "%.13f"%(latlon[0])
                    # SADD 10.1.1:v "0..1.:-50.7690301903|-70.7467998635|0|0"
                    ffv.write("SADD " + strId + ":v \"" + logs + ":" + sLat + "|" + sLon + "|" + str(i) + "|0\"\n")      
                    # GEOADD 10.1:geoidx -70.7467998635 -50.7690301903 "0..1.:10.1.1|0|9"
                    ffgeoidx.write(geoidxId + sLon + " " + sLat + " \"" + logs + ":" + strId + "|" + str(i) + "|" + str(n) + "\"\n") 
                    i = i + 1
            else:
                ss = "missing ocfg|%s"%(ss)
                
            print(ss)
        
        ffo.close()
        ffocfg.close()
        ffval.close()
        ffsidx.close()
        ffv.close()
        ffgeoidx.close()        
        