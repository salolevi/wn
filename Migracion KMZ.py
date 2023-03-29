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
                "NAP1NLL": ["go/fo/cie", "2N1", "1"],
                "NAP2N" : ["go/fo/cie", "2N2", "1"],
                "NAP16LL" : ["go/fo/cie", "2N2", "1"],
                "NAP16NOI" : ["go/fo/cie", "2N2", "1"],
                "NODO" : ["go/fo/cie", "NODO", "1"],
                "METRO" : ["go/fo/cie", "CM", "1"], 
                "BOTELLA" : ["go/fo/cie", "1N", "1"],
                "NAPEM" : ["go/fo/cie", "1N", "1"],
                "CLMAY" : ["go/fo/cli", "CLIENTE", "1"],
                "ROSETA" : ["go/fo/cie", "ROS", "1"],
            }
    ocfg2 = {   
                "4" : ["gc/fo", "4", "1"], 
                "8" : ["gc/fo", "8", "1"], 
                "12" : ["gc/fo", "12", "1"], 
                "16" : ["gc/fo", "16", "1"], 
                "24" : ["gc/fo", "24", "1"], 
                "36" : ["gc/fo", "36", "1"], 
                "48" : ["gc/fo", "48", "1"], 
                "Gen" : ["gc/fo", "gen", "1"]
            }
    
    if fType == "fme_point":
        return ocfg1[fFolder]

    elif fType == "fme_line":
        if (fFolder == "Gen"):
            return ocfg2[fFolder]
        pelos = re.sub("[^0-9]", "", fFolder)
        return ocfg2[pelos]
    
    return None
        
        
  
def getFolder(parent, folderList):
    for folder in folderList:
        id = folder.getAttribute("kml_id")
        if parent == id:
            return folder.getAttribute("kml_name")
    return None
    
def getStyle(style, styleList, styleMapList):
    if (style != None):
        st1 = style.strip("#")

        for st in styleMapList:
            id = st.getAttribute("kml_id")
            if st1 == id:
                st1 = st.getAttribute("kml_style_url_normal").strip("#")
                break

        # check for the style
        for st in styleList:
            id = st.getAttribute("kml_id")
            if st1 == id:
                return st
                
    else:
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
        self.featureList.append(feature)
        if fmeFeatureType == "folder":
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
            if (feature.getAttribute("fme_feature_type") == "Placemark"):
                parent = feature.getAttribute("kml_parent")
                fFolder = getFolder(parent, self.folderList)
                # while parentType == "Folder":
                #     folder = getFolder(parent, self.folderList)
                #     if folder != None:
                #         parent = folder.getAttribute("kml_parent")
                #         parentType = folder.getAttribute("kml_parent_type")
                #         name = folder.getAttribute("kml_name")
                #         fList.append(name)
                #     else:
                #         parentType = None
                
                # B - write @kmlId == kml_id, @oName == kml_name, @comm == kml_description, @oStyle == kml_style_url, @folder == fFolder
                fFeatureType = feature.getAttribute("fme_feature_type")
                fType = feature.getAttribute("fme_type")
                fId = feature.getAttribute("kml_id")
                fName = feature.getAttribute("kml_name") or "No Name"
                fStyle = feature.getAttribute("kml_style_url").strip("#")
                # fFolder = feature.getFolder()
                ss = "%s|%s|%s|%s|%s|%s"%(fFeatureType, fType, fId, fName, fStyle, fFolder)
                
                # C - graphic styling such as @oColor == kml_iconstyle_color
                # style = getStyle(fStyle, self.styleList, self.styleMapList)
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
                    fStyle = checkQuotes(fStyle)
                    ffval.write("SADD " + strId + ":val \"" + logs + ":@oStyle|" + fStyle + "|0\"\n")
                    fFolder = checkQuotes(fFolder)
                    ffval.write("SADD " + strId + ":val \"" + logs + ":@folder|" + fFolder + "|0\"\n")
                    ffval.write("SADD " + strId + ":val \"" + logs + ":@oType|" + ocfg[1] + "|0\"\n")
                    ffsidx.write("ZADD " + companyId + ".@oName.sidx 0 \"" + fName + ":" + logs + ":" + strId + "\"\n")       # ZADD 10.@oName.sidx 0 "CAMPO INDIO:0..1.:10.1.1"
                    ffsidx.write("ZADD " + companyId + ".@kmlId.sidx 0 \"" + fId + ":" + logs + ":" + strId + "\"\n")
                    ffsidx.write("ZADD " + companyId + ".@folder.sidx 0 \"" + fFolder + ":" + logs + ":" + strId + "\"\n")
                                    
                    geoidxId = "GEOADD " + companyId + "." + ocfg[2] + ":geoidx "
                    
                    # write vertex
                    if (feature.getAttribute("fme_type") == "fme_line"):
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