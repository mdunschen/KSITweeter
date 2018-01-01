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


def getLocInformation(lat, lon, infokey):
    urlstr = "http://api.postcodes.io/postcodes?lat=%s&lon=%s" % (lat, lon)
    r = request.urlopen(urlstr).read()
    cont = json.loads(r.decode('utf-8'))
    if cont["status"] and cont["result"]:
        return cont["result"][-1][infokey]

def getPostCode(lat, lon):
    return getLocInformation(lat, lon, "outcode")

def getWard(lat, lon):
    return getLocInformation(lat, lon, "admin_ward")

def getDistrict(lat, lon):
    return getLocInformation(lat, lon, "admin_district")

def getWardCllrs(ward):
    db = sqlite3.connect("cllrs.db")
    c = db.cursor()
    c.execute("SELECT * FROM cllrs WHERE wardName=?",(ward,))
    return c.fetchall()


def getCouncillorTwitterHandles(lat, lon):
    ward = getWard(lat, lon)
    if ward:
        return [c[8] for c in getWardCllrs(ward) if c[8] and (('councillor' in c[9].lower()) or ('cllr' in c[9].lower()))]



if __name__ == "__main__":
    lat, lon = 53.3724111, -2.861466
    print(getWard(lat, lon))
    print(getPostCode(lat, lon))
    print(getDistrict(lat, lon))
    print(getCouncillorTwitterHandles(lat, lon))

