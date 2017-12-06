import datetime
import re
import sys
import pickle
import operator
sys.path.append("C:\\Program Files\\Anaconda3\\envs\\tensorflow\\lib\\site-packages")
import tweepy

from locService import getNearestStreet, getPostCode

vehicle_type = {
    1:("Pedal cycle","bicycle"),\
    2:("Motorcycle 50cc and under","moped"),\
    3:("Motorcycle 125cc and under","motorbike"),\
    4:("Motorcycle over 125cc and up to 500cc","motorbike"),\
    5:("Motorcycle over 500cc","motorbike"),\
    8:("Taxi/Private hire car","taxi"),\
    9:("Car","car"),\
    10:("Minibus (8 - 16 passenger seats)","van"),\
    11:("Bus or coach (17 or more pass seats)","bus"),\
    16:("Ridden horse","horse"),\
    17:("Agricultural vehicle","tractor"),\
    18:("Tram","tram"),\
    19:("Van / Goods 3.5 tonnes mgw or under","van"),\
    20:("Goods over 3.5t. and under 7.5t","lorry"),\
    21:("Goods 7.5 tonnes mgw and over","lorry"),\
    22:("Mobility scooter","mobility scooter"),\
    23:("Electric motorcycle","motorbike"),\
    90:("Other vehicle","vehicle"),\
    97:("Motorcycle - unknown cc","motorbike"),\
    98:("Goods vehicle - unknown weight","lorry"),\
    -1:("Data missing or out of range","vehicle")}




translations = {"2  (Female)": "woman",
                "1  (Male)": "man",
                "woman": "her",
                "man": "him",
                "child": "it",
                "01  (0 - 5)": "a",
                "02  (6 - 10)": "a",
                "03  (11 - 15)": "a",
                "04  (16 - 20)": "a teenage",
                "05  (21 - 25)": "a",
                "06  (26 - 35)": "a",
                "07  (36 - 45)": "a",
                "08  (46 - 55)": "a",
                "09  (56 - 65)": "a middle-aged",
                "10  (66 - 75)": "an elderly",
                "11  (Over 75)": "an elderly",
                "-1":"a"}


consumer_key, consumer_secret, access_token, access_token_secret = pickle.load(open("apikeys.bin", "rb")) 

def twitterAPI():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api



def tweet(status, replyto=None, imgfilename=None):
    if not (status or imgfilename):
        return
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', status)
    print("urls = ", urls)
    # take out all url texts from status for count, all urls count as 23
    rstat = status
    for u in urls:
        rstat = rstat.replace(u, '')
    nchars = len(rstat) + 23 * len(urls)
    if nchars > 140:
        print("Tweet too long")
        
    #print(status)
    
    api = twitterAPI()
    if (imgfilename and os.path.isfile(imgfilename)):
        try:
            stat = api.update_with_media(imgfilename, status=status, in_reply_to_status_id=(replyto and replyto.id))
        except Exception as e:
            print(e)
            stat = None
        
    else:
        try:
            stat = api.update_status(status=status, in_reply_to_status_id=(replyto and replyto.id))
        except Exception as e:
            print(e)
            stat = None
    return stat
def casualtyDesc(gender, age_band):
    if age_band in ("01  (0 - 5)", "02  (6 - 10)", "03  (11 - 15)"):
        return "a child"
    return "%s %s" % (translations[age_band], translations[gender])

def readKSIData(fn):
    data = open(fn).read()
    # first line is used for keys
    ksiData = []
    records = data.split('\n')
    keys = records[0].split("\t")
    for i, r in enumerate(records[1:]):
        rs = r.split('\t')
        assert len(keys) == len(rs) or len(rs) == 1, (len(keys), len(rs))
        if len(keys) == len(rs):
            d = dict(zip(keys, rs))
            ksiData.append(d)

    return ksiData

def addVehicleData(ksiData, vehData):
    v = open(vehData).read().split('\n')
    vdict = {}
    keys = v[0].split(',')
    for vd in v[1:]:
        rc = dict(zip(keys, vd.split(',')))
        if rc["Accident_Index"] not in vdict:
            vdict[rc["Accident_Index"]] = []
        vdict[rc["Accident_Index"]].append(rc)
    for kd in ksiData:
        assert kd["Accident_Index"] in vdict
        kd["Vehicle_Type"] = [int(v["Vehicle_Type"]) for v in vdict[kd["Accident_Index"]]]

def sortByDateTime(ksiData):
    sortedksiData = []
    for r in ksiData:
        date = r['Date']
        tim = r['Time']
        # make a datetime object
        dt = datetime.datetime.strptime("%s %s" % (date, tim), "%d/%m/%Y %H:%M")
        sortedksiData.append((dt, r))
    sortedksiData.sort(key=operator.itemgetter(0))
    return sortedksiData

def translate(phrase):
    if phrase not in translations:
        assert 0, phrase
    return translations[phrase]


def composeTweet(eventDate, record):
    tweetContent = []
    cd = casualtyDesc(record["Sex_of_Casualty"], record["Age_Band_of_Casualty"])
    pronoun = translate(cd.split(" ")[-1])
    lat, lon = record["Latitude"], record["Longitude"]
    streetname = getNearestStreet(lat, lon)
    if streetname:
        pc = getPostCode(lat, lon)
        if pc:
            streetinfo = " on %s (%s)" % (streetname, pc)
        else:
            streetinfo = " on %s" % (streetname)
    else:
        streetinfo = ""
    tweetContent.append("Today, at %s, %d year(s) ago%s, %s was seriously injured when a %s collided into %s." % (\
            record['Time'], \
            datetime.datetime.now().year - eventDate.year, \
            streetinfo, \
            cd, \
            vehicle_type[record["Vehicle_Type"][0]][1], \
            pronoun)) 
    return ''.join(tweetContent)
        



if __name__ == "__main__":
    ksiData = readKSIData("2016_05.tsv")
    addVehicleData(ksiData, r"Veh.csv")
    sortedksiData = sortByDateTime(ksiData)
    for i, de in enumerate(sortedksiData):
        date, event = de
        now = datetime.datetime.now()
        print (date)
        if date.month == now.month and date.day == now.day:
            print(now - date)
            print(i, composeTweet(date, event))
