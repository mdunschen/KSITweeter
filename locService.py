#!/usr/bin/python3

import urllib
import urllib.request as request
import json
import sqlite3

def getNearestStreet(lat, lon):
    urlstr = "http://router.project-osrm.org/nearest/v1/driving/%s,%s" % (lon, lat)
    r = request.urlopen(urlstr).read()
    cont = json.loads(r.decode('utf-8'))
    if cont['code'] == "Ok":
        return cont["waypoints"][0]["name"]


def getLocInformation(lat, lon, infokeys):
    urlstr = "http://api.postcodes.io/postcodes?lat=%s&lon=%s" % (lat, lon)
    r = request.urlopen(urlstr).read()
    cont = json.loads(r.decode('utf-8'))
    if cont["status"] and cont["result"]:
        return [cont["result"][-1][k] for k in infokeys]

def getPostCode(lat, lon):
    return getLocInformation(lat, lon, ("outcode",))

def getWard(lat, lon):
    return getLocInformation(lat, lon, ("admin_ward",))

def getDistrict(lat, lon):
    return getLocInformation(lat, lon, ("admin_district",))

def getWardCllrs(district, ward):
    db = sqlite3.connect("cllrs.db")
    c = db.cursor()
    c.execute("SELECT * FROM cllrs WHERE city=? AND wardName=?",(district, ward,))
    return c.fetchall()


def getCouncillorTwitterHandles(lat, lon):
    res = getLocInformation(lat, lon, ("admin_district", "admin_ward"))
    if res:
        district, ward = res[0], res[1]
        return [c[8] for c in getWardCllrs(district, ward) if c[8] and (('councillor' in c[9].lower()) or ('cllr' in c[9].lower()))]



if __name__ == "__main__":
    lat, lon = 53.3724111, -2.861466
    print(getWard(lat, lon))
    print(getPostCode(lat, lon))
    print(getDistrict(lat, lon))
    print(getCouncillorTwitterHandles(lat, lon))

