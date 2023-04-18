import fme
import fmeobjects
import re
import datetime
import time
import math
# from scipy.spatial.distance import cdist

def unixTimeNow(dt):
    return int(time.mktime(dt.timetuple()))

def isPoint(feat):
    return feat.getAttribute("fme_type") == "fme_point"

def isLine(feat):
    return feat.getAttribute("fme_type") == "fme_line"
    
def getLogs():
    return "%d..1."%(unixTimeNow(datetime.datetime.now()))

def checkQuotes(s):
    s = s.replace('"', '')
    s = s.replace("'", "")
    s = s.replace("\t", "")
    s = s.replace(":", "")
    s = s.replace("|", " ")
    return s

def getBoxId(com_id, net_id, box, elementsList):
    for boxTuple in elementsList['fme_point']:
        if boxTuple[0] == box:
            return "%s.%s.%d"%(com_id, net_id, boxTuple[1])
        

def connectCO(ffco, key, other_key, n1, n2):
    ffco.write(f'SADD {key}:co "{getLogs()}:{n1}|{other_key}|{n2}"\n')
    ffco.write(f'SADD {other_key}:co "{getLogs()}:{n2}|{key}|{n1}"\n')

def get_logs():
    now = datetime.now()  # ahora
    unixtime = int(time.mktime(now.timetuple()))
    return f'{unixtime}..1.'

def euclidean_dist(point1, point2):
    squared_diffs = [];
    for i in range(2):
        squared_diffs.append((point1[i] - point2[i]) ** 2)
    
    return math.sqrt(sum(squared_diffs))
        

def getClosest(comp_id, net_id, obj_id, elementsList, cable, ffco):
    MAX_RANGE = 0.1
    # vertices = list(map(lambda x: (x[0], x[1]), cable.getAllCoordinates()))
    key = "%s.%s.%d"%(comp_id, net_id, obj_id)
    for i in range (cable.numVertices()-1):
        v1 = cable.getCoordinates(i)
        v2 = cable.getCoordinates(i+1)
        total_distance = euclidean_dist(v1, v2)
        for boxTuple in elementsList['fme_point']:
            coordinates = (boxTuple[0].getCoordinates(0)[0], boxTuple[0].getCoordinates(0)[1])
            box_key = "%s.%s.%d"%(comp_id, net_id, boxTuple[1])
            if (total_distance - (euclidean_dist(v1, coordinates) + euclidean_dist(v2, coordinates)) <= MAX_RANGE):
                connectCO(ffco, key, box_key, )
    
    return None
    


# network types: 1 == troncal, 2 == distribucion, 3 == clientes, 4 == infraestructura, 5 == areas de zonas
def getOcfg1(fName, fType, fFolder):
    ocfg1 = {  
                "NAP1N" : ["go/fo/cie", "2N1", "2"],
                "NAP1NLL": ["go/fo/cie", "2N1", "2"],
                "NAP2N" : ["go/fo/cie", "2N2", "2"],
                "NAP16LL" : ["go/fo/cie", "2N2", "2"],
                "NAP16NOI" : ["go/fo/cie", "2N2", "2"],
                "NODO" : ["go/fo/olt", "NODO", "1"],
                "METRO" : ["go/fo/cie", "CM", "2"], 
                "BOTELLA" : ["go/fo/cie", "BOT", "1"],
                "NAPEM" : ["go/fo/cie", "1N", "1"],
                "CLMAY" : ["go/fo/cli", "CLIENTE", "1"],
                "ROSETA" : ["go/fo/cie", "ROS", "2"],
            }
    ocfg2 = {   
                "4" : ["gc/fo", "4", "2"], 
                "8" : ["gc/fo", "8", "2"], 
                "12" : ["gc/fo", "12", "2"], 
                "16" : ["gc/fo", "16", "2"], 
                "24" : ["gc/fo", "24", "2"], 
                "36" : ["gc/fo", "36", "2"],
                "40" : ["gc/fo", "36", "2"],
                "48" : ["gc/fo", "48", "2"], 
                "Gen" : ["gc/fo", "GEN", "2"]
            }
    ocfg3 = {   
                "8x1" : ["gc/fo", "8x1", "1"],
                "8" : ["gc/fo", "8", "1"],
                "12" : ["gc/fo", "12", "1"], 
                "12x2" : ["gc/fo", "12x2", "1"], 
                "16" : ["gc/fo", "16", "1"], 
                "24" : ["gc/fo", "24", "1"], 
                "24x2" : ["gc/fo", "24x2", "1"], 
                "36" : ["gc/fo", "36", "1"],
                "40" : ["gc/fo", "36", "1"],
                "48" : ["gc/fo", "48", "1"], 
                "64" : ["gc/fo", "64", "1"],
                "72" : ["gc/fo", "72", "1"],
                "96" : ["gc/fo", "96", "1"],
                "144" : ["gc/fo", "144", "1"],
                "256" : ["gc/fo", "256", "1"],
                "Gen" : ["gc/fo", "GEN", "1"]
            }
    
    if fType == "fme_point":
        return ocfg1[fFolder]

    elif fType == "fme_line":
        if fName.lower().startswith("troncal"):
            if (fFolder == "Gen"):
                return ocfg3[fFolder]
            pelos = re.sub("[^0-9]", "", fFolder)
            if pelos == "8":
                key =  "8" if "LF" in fName else "8x1"
            elif pelos == "12":
                key = "12x2" if "GLC" in fName else "12"    
            elif pelos == "24":
                key = "24x2" if "FW" in fName else "24"
            else:
                key = pelos
            return ocfg3[key]
        else:
            if fFolder == "Gen":
                return ocfg2[fFolder]
            else:
                key = re.sub("[^0-9]", "", fFolder)
                return ocfg2[key]
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
        self.elementsList = {
            'fme_line': [],
            'fme_point': []
        }
        self.logs = "%d..1."%(unixTimeNow(datetime.datetime.now()))
    
    def input(self, feature):
        fmeFeatureType = feature.getAttribute("fme_feature_type").strip().lower()
        featureTuple = (feature, len(self.featureList))
        self.featureList.append(featureTuple)
        if fmeFeatureType == "placemark":
            self.elementsList[feature.getAttribute("fme_type")].append(featureTuple)
        if fmeFeatureType == "folder":
            self.folderList.append(feature)
        elif fmeFeatureType == "style":
            self.styleList.append(feature)
        elif fmeFeatureType == "stylemap":
            self.styleMapList.append(feature)

    def close(self):
        fo = open(r"C:\Users\Salo\WN\o" + ".txt","w")
        ffocfg = open(r"C:\Users\Salo\WN\ocfg" + ".txt","w")
        ffval = open(r"C:\Users\Salo\WN\val" + ".txt","w")
        ffsidx = open(r"C:\Users\Salo\WN\sidx" + ".txt","w")
        ffv = open(r"C:\Users\Salo\WN\v"+ ".txt","w")
        ffgeoidx = open(r"C:\Users\Salo\WN\geoidx" + ".txt","w")
        ffco = open(r"C:\Users\Salo\WN\co" + ".txt","w")
        companyId = "400"
        id = 0
        unixtime = unixTimeNow(datetime.datetime.now())
        logs = "%d..1."%(unixtime)
        # print(self.folderList)
                
        for feature in self.featureList:
            # A - store kml folders in @folder
            if (feature[0].getAttribute("fme_feature_type") == "Placemark"):
                parent = feature[0].getAttribute("kml_parent")
                fFolder = getFolder(parent, self.folderList)
                fFeatureType = feature[0].getAttribute("fme_feature_type")
                fType = feature[0].getAttribute("fme_type")
                fId = feature[0].getAttribute("kml_id")
                fName = feature[0].getAttribute("kml_name") or "No Name"
                fStyle = feature[0].getAttribute("kml_style_url").strip("#")
                ss = "%s|%s|%s|%s|%s|%s"%(fFeatureType, fType, fId, fName, fStyle, fFolder)
                ocfg = getOcfg1(fName, fType, fFolder)
                if ocfg != None:
                    ss = "%s|%s|%s|%s"%(ocfg[2], ocfg[0], ocfg[1], ss)
                    
                    # E - write files    
                    id = id + 1
                    strId = "%s.%s.%d"%(companyId, ocfg[2], id)
                    fo.write("SET " + strId + " \"" + logs + "\"\n")                                    # SET 10.1.1 "0..1."
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
                    if fFolder == "NAP1NLL" or fFolder == "NAP16LL":
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@nLib|" + "0" + "|0\"\n")
                        
                    if fFolder == "NAP16NOI":
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@notI|" + "true" + "|0\"\n")
                        
                    
                    if isPoint(feature[0]):
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@oType|" + ocfg[1] + "|0\"\n")
                    else:
                        ffval.write("SADD " + strId + ":val \"" + logs + ":@foType|" + ocfg[1] + "|0\"\n")
                    ffsidx.write("ZADD " + companyId + ".@oName.sidx 0 \"" + fName + ":" + logs + ":" + strId + "\"\n")       # ZADD 10.@oName.sidx 0 "CAMPO INDIO:0..1.:10.1.1"
                    ffsidx.write("ZADD " + companyId + ".@kmlId.sidx 0 \"" + fId + ":" + logs + ":" + strId + "\"\n")
                    ffsidx.write("ZADD " + companyId + ".@folder.sidx 0 \"" + fFolder + ":" + logs + ":" + strId + "\"\n")
                                    
                    geoidxId = "GEOADD " + companyId + "." + ocfg[2] + ":geoidx "
                    
                    # write vertex
                    n = feature[0].numVertices()
                    i = 0
                    while i < n:
                        latlon = feature[0].getCoordinate(i)
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
        
        fo.close()
        ffocfg.close()
        ffval.close()
        ffsidx.close()
        ffv.close()
        ffgeoidx.close() 
