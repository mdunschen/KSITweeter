import urllib
import urllib.request as request
import json

def getNearestStreet(lat, lon):
    urlstr = "http://router.project-osrm.org/nearest/v1/driving/%s,%s" % (lon, lat)
    r = request.urlopen(urlstr).read()
    cont = json.loads(r.decode('utf-8'))
    if cont['code'] == "Ok":
        return cont["waypoints"][0]["name"]


def getPostCode(lat, lon):
    urlstr = "http://api.postcodes.io/postcodes?lat=%s&lon=%s" % (lat, lon)
    r = request.urlopen(urlstr).read()
    cont = json.loads(r.decode('utf-8'))
    print (cont["status"])
    if cont["status"] and cont["result"]:
        return cont["result"][-1]["outcode"]

def getWard(lat, lon):
    urlstr = "http://api.postcodes.io/postcodes?lat=%s&lon=%s" % (lat, lon)
    r = request.urlopen(urlstr).read()
    cont = json.loads(r.decode('utf-8'))
    print (cont["status"])
    if cont["status"] and cont["result"]:
        return cont["result"][-1]["admin_ward"]


if __name__ == "__main__":
    print(getNearestStreet("53.4025", "-2.9865"))
    print(getPostCode("53.4025", "-2.9865"))
    print(getWard("53.4025", "-2.9865"))
    print(getNearestStreet("53.372420", "-2.861337"))
    print(getPostCode("53.372420", "-2.861337"))
    print(getWard("53.372420", "-2.861337"))

