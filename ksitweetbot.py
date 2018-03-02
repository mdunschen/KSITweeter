#!/usr/bin/python3

# coding: utf-8

import datetime, time
import re
import sys
import pickle
import operator
import threading

sys.path.append("C:\\Program Files\\Anaconda3\\envs\\tensorflow\\lib\\site-packages")
import tweepy

from locService import *

vehicle_type = {
    1:("Pedal cycle","bicycle", "rider"),\
    2:("Motorcycle 50cc and under","moped", "rider"),\
    3:("Motorcycle 125cc and under","motorbike", "rider"),\
    4:("Motorcycle over 125cc and up to 500cc","motorbike", "rider"),\
    5:("Motorcycle over 500cc","motorbike", "rider"),\
    8:("Taxi/Private hire car","taxi", "driver"),\
    9:("Car","car", "driver"),\
    10:("Minibus (8 - 16 passenger seats)","van", "driver"),\
    11:("Bus or coach (17 or more pass seats)","bus", "driver"),\
    16:("Ridden horse","horse", "rider"),\
    17:("Agricultural vehicle","tractor", "driver"),\
    18:("Tram", "tram", ""),\
    19:("Van / Goods 3.5 tonnes mgw or under","van", "driver"),\
    20:("Goods over 3.5t. and under 7.5t","lorry", "driver"),\
    21:("Goods 7.5 tonnes mgw and over","lorry", "driver"),\
    22:("Mobility scooter","mobility scooter", "rider"),\
    23:("Electric motorcycle","motorbike", "rider"),\
    90:("Other vehicle", "", "driver"),\
    97:("Motorcycle - unknown cc","motorbike", "rider"),\
    98:("Goods vehicle - unknown weight","lorry", "driver"),\
    -1:("Data missing or out of range","", "driver")}




translations = {"2  (Female)": "woman",
                "1  (Male)": "man",
                "woman": "her",
                "man": "him",
                "child": "her/him",
                "01  (0 - 5)": "A",
                "02  (6 - 10)": "A",
                "03  (11 - 15)": "A",
                "04  (16 - 20)": "A teenage",
                "05  (21 - 25)": "A young",
                "06  (26 - 35)": "A",
                "07  (36 - 45)": "A",
                "08  (46 - 55)": "A",
                "09  (56 - 65)": "A middle-aged",
                "10  (66 - 75)": "An elderly",
                "11  (Over 75)": "An elderly",
                "1  (Fatal)": "killed",
                "2  (Serious)": "seriously injured",
                "0  (Pedestrian)": "walking ",
                "1  (Cyclist)": "cycling ",
                "3  ('Motorcyclist')": "riding ",
                "-1":""}

sexMap = {1: "1  (Male)", 2: "2  (Female)", 3: "Unknown"}
ageMap = {1: "01  (0 - 5)",\
          2: "02  (6 - 10)",\
          3: "03  (11 - 15)",\
          4: "04  (16 - 20)",\
          5: "05  (21 - 25)",\
          6: "06  (26 - 35)",\
          7: "07  (36 - 45)",\
          8: "08  (46 - 55)",\
          9: "09  (56 - 65)",\
          10: "10  (66 - 75)",\
          11: "11  (Over 75)",
          -1: "unknown"}

consumer_key, consumer_secret, access_token, access_token_secret = pickle.load(open("apikeys.bin", "rb")) 

def twitterAPI():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit = True)
    return api



def tweetChars(status):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', status)
    # take out all url texts from status for count, all urls count as 23
    rstat = status
    for u in urls:
        rstat = rstat.replace(u, '')
    nchars = len(rstat) + 23 * len(urls)
    return nchars

def tweet(status, replyto=None, imgfilename=None):
    if not (status or imgfilename):
        return
    nchars = tweetChars(status)
    print("characters: ", nchars)
    if nchars > 140:
        print("Tweet too long")
        
    print(status)
    
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

def multiTweet(stats):
    r = None
    for s in stats:
        print(s)
        r = tweet(s, r)

def driverDesc(gender, age_band, vehicleType):
    return "a %s %s" % (vehicle_type[vehicleType][1], vehicle_type[vehicleType][2])
    
def personDesc(gender, age_band):
    if age_band in ("01  (0 - 5)", "02  (6 - 10)", "03  (11 - 15)"):
        return "A child"
    if gender in ("Unknown") or age_band in ("unknown"):
        return "an unknown driver"
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
        kd["Sex_of_Driver"] = [sexMap[int(v["Sex_of_Driver"])] for v in vdict[kd["Accident_Index"]]]
        kd["Age_Band_of_Driver"] = [ageMap[int(v["Age_Band_of_Driver"])] for v in vdict[kd["Accident_Index"]]]

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
    if record['Casualty_Type'] not in ('1  (Cyclist)', '0  (Pedestrian)'):
        print(record['Casualty_Type'])
        return
    tweetContent = []
    cd = personDesc(record["Sex_of_Casualty"], record["Age_Band_of_Casualty"])
    dd = driverDesc(record["Sex_of_Driver"][0], record["Age_Band_of_Driver"][0], record["Vehicle_Type"][0])
    pronoun = translate(cd.split(" ")[-1])
    severity = translate(record["Casualty_Severity"])
    lat, lon = record["Latitude"], record["Longitude"]
    streetname = getNearestStreet(lat, lon)
    if streetname:
        pc = getPostCode(lat, lon)
        if pc:
            streetinfo = "on %s (%s)" % (streetname, pc[0])
        else:
            streetinfo = "on %s" % (streetname)

    else:
        res = getLocInformation(lat, lon, ("admin_district", "outcode"))
        if res:
            district, pc = res[0], res[1]
            streetinfo = "in %s (%s)" % (district, pc)
        else:
            streetinfo = ""
    casualtyType = translate(record["Casualty_Type"])
    yearsago = datetime.datetime.now().year - eventDate.year
    if yearsago == 1:
        yearsago = "%d year" % yearsago
    else:
        yearsago = "%d years" % yearsago
    templ0 = "Today, %s, %s ago %s: %s %s %s was %s by %s"
    templ1 = "%s was %s today %s ago (%s, %s) %s%s, by %s"
    tweetContent.append(templ1 % (\
            cd, \
            severity, \
            yearsago, \
            record['Time'], \
            "%d/%d/%d" % (eventDate.day, eventDate.month, eventDate.year-2000), \
            casualtyType, \
            streetinfo, \
            dd))
    if 0:
        tweetContent.append(templ0 % (\
                record['Time'], \
                yearsago, \
                "(%d/%d/%d)" % (eventDate.day, eventDate.month, eventDate.year-2000), \
                cd, \
                casualtyType, \
                streetinfo, \
                severity, \
                dd))
    return ''.join(tweetContent)

def splitTweetToMultiple(cont, urlsToAdd, tagsToAdd):
    totalChars = tweetChars(cont) + tweetChars(' '.join(urlsToAdd + tagsToAdd)) 
    print("totalChars = ", totalChars)
    if totalChars <= 140:
        return [''.join([cont + ' '.join(urlsToAdd + tagsToAdd)])]
    cont = ''.join([cont + ' '.join(urlsToAdd + tagsToAdd)])
    status = []
    icount = 1
    while cont:
        words = cont.split(' ')
        singleTweet = ['%d:' % icount]
        icount += 1
        while words and tweetChars(' '.join(singleTweet)) < 140:
            singleTweet.append(words.pop(0))
        if tweetChars(' '.join(singleTweet)) > 140:
            words.insert(0, singleTweet.pop())
        assert tweetChars(' '.join(singleTweet)) <= 140
        status.append(' '.join(singleTweet))
        # now rebuild cont from the rest
        cont = ' '.join(words)
        print("Remaining: ", cont)
    return status

def tweetTodaysEvents(today = None):
    ksiData = readKSIData("2016/2016_05.tsv")
    addVehicleData(ksiData, "2016/Veh.csv")
    sortedksiData = sortByDateTime(ksiData)
    if not today:
        today = datetime.datetime.now()
    
    # scroll forward to today
    i = 0
    de = sortedksiData[i]
    date, event = de
    while date.month < today.month or date.day < today.day:
        i += 1
        if i == len(sortedksiData):
            i = 0
        de = sortedksiData[i]
        date, event = de

    # tweet all of today's events.
    while date.month == today.month and date.day == today.day:
        now = datetime.datetime.now()
        secondsWait = (3600 * date.time().hour + 60 * date.time().minute) - \
                      (3600 * now.time().hour + 60 * now.time().minute)
        print("seconds to wait: ", secondsWait)
        cont = composeTweet(date, event)
        if cont:
            lat, lon = event["Latitude"], event["Longitude"]
            urlsToAdd = [' ', r"@livepedestrian", r"http://wacm.org.uk"]
            tagsToAdd = [r"#VisionZero", r"#NotJustAStat"]
            cllrsOnTwitter = getCouncillorTwitterHandles(lat, lon)
            if cllrsOnTwitter:
                urlsToAdd = [' '] + cllrsOnTwitter + urlsToAdd[1:]

            # split into multiple tweets
            status = splitTweetToMultiple(cont, urlsToAdd, tagsToAdd)

            if secondsWait <= 0:
                print ("Immediate tweet: \n", status)
                multiTweet(status)

            else:
                t = threading.Timer(secondsWait - 2, multiTweet, [status])
                print ("Waiting to tweet: \n",status)
                t.start()
                t.join()
                
        i += 1
        if i == len(sortedksiData):
            i = 0
        de = sortedksiData[i]
        date, event = de
        print(date.day, date.month)
        
def findCouncillorOnTwitter(name, council, ward):
    api = twitterAPI()
    rlast = []
    for r in  tweepy.Cursor(api.search_users, "%s" % (name)).pages(10):
        r = [u for u in r if ((council.lower() in u.description.lower() or ward.lower() in u.description.lower()) and ("member" in u.description.lower() or "cllr" in u.description.lower() or "councillor" in u.description.lower()))]
        if r and len(r) == 1:
            return r[0]



if __name__ == "__main__":
    day = datetime.datetime.now()
    tweetTodaysEvents(day)
    if 0:
        result = findCouncillorOnTwitter("James Noakes", "Liverpool", "Clubmoor") 
        if result:
            print(result.screen_name, result.description)
        result = findCouncillorOnTwitter("Crone", "Liverpool", "Michaels") 
        if result:
            print(result.screen_name, result.description)
        result = findCouncillorOnTwitter("O'Byrne", "Liverpool", "Warbreck") 
        if result:
            print(result.screen_name, result.description)
