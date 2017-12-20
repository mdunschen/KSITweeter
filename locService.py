#!/usr/bin/python3

import urllib
import urllib.request as request
import json

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



if __name__ == "__main__":
    print(getWard("53.488609", "-2.885376"))
    print(getPostCode("53.488609", "-2.885376"))
    print(getDistrict("53.488609", "-2.885376"))

