#!/usr/bin/python3

# coding: utf-8
import urllib
import urllib.request as request
import re

councillorURLS = []
# Liverpool, Knowlsey, St Helens, Sefton, Wirral, (Halton?)
councillorURLS.append(r"https://www.sthelens.gov.uk/council/councillors-elections-voting/find-your-local-councillor/")
councillorURLS.append(r"http://councillors.liverpool.gov.uk/mgFindMember.aspx")
councillorURLS.append(r"https://councillors.knowsley.gov.uk/mgFindMember.aspx")
councillorURLS.append(r"http://modgov.sefton.gov.uk/moderngov/mgFindMember.aspx")
councillorURLS.append(r"https://democracy.wirral.gov.uk/mgFindMember.aspx")
councillorURLS.append(r"http://councillors.halton.gov.uk/mgFindMember.aspx")


def writeToFile(allWards):
    f = open("allcouncillors.tsv", "w")
    f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % ("City/Town", "URL City", "Name Ward", "URL Ward", "URL Councillor", "Name Councillor"))
    for townUrl in allWards:
        name = allWards[townUrl]["name"]
        wards = allWards[townUrl]["wards"]
        for ward in wards:
            wardname = ward["name"]
            wardurl = ward["url"]
            for cllr in ward["cllrs"]:
                f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (name, townUrl, wardname, wardurl, cllr, ward["cllrs"][cllr]))
    f.close()

def getWard(urlstr, k):
    if type(k) == type(1):
        return "%s?XXR=0&AC=WARD&WID=%d" % (urlstr, k)
    else:
        return "%s%s" % (re.match("(https?\:\/\/[a-z]*\.[a-z]*\.[a-z]*\.uk)\/", urlstr).group(1), k)

def getCouncillors(urlstr, k):
    wardUrlStr = getWard(urlstr, k)
    if type(k) == type(1):
        r = request.urlopen(wardUrlStr).read().decode('utf-8')
        councillors = re.findall("\<a  href=\"mgUserInfo\.aspx\?UID=([0-9 ]*)\".*\>(.*)\<\/a\>", r, re.MULTILINE)
        return {"%s/mgUserInfo.aspx?UID=%d" % (re.match("(https?\:\/\/[a-z]*\.[a-z]*\.[a-z]*\.uk)\/", urlstr).group(1), int(o[0].strip())):o[1] for o in councillors}

    else:
        r = request.urlopen(wardUrlStr).read().decode('utf-8')
        names = re.findall("\<h3\>(.*)\<\/h3\>", r)
        ids = re.findall("\<a href=\".*mgUserInfo\.aspx\?UID=([0-9 ]*)\&?.*\".*\>", r, re.MULTILINE)
        assert(len(names) == len(ids))
        councillors = zip(ids, names)
        return {"%s/mgUserInfo.aspx?UID=%d" % ("https://moderngov.sthelens.gov.uk", int(o[0].strip())):o[1] for o in councillors}

def getAllCouncillors():
    allWards = {}
    for urlstr in councillorURLS:
        town = re.match("https?\:\/\/[a-z]*\.([a-z]*)\.", urlstr).group(1)
        print(town)
        allWards[urlstr] = {"name":town}
        r = request.urlopen(urlstr).read().decode('utf-8')
        # get all ward names and Ids
        m = re.search('.*\<select id\=\"WardId\" name=\"WardId\"\>(.*)\<\/select\>.*\<select?', r, re.MULTILINE|re.DOTALL) # some councils also list parishes, hence the second select
        if not m:
            m = re.search('.*\<select id\=\"WardId\" name=\"WardId\"\>(.*)\<\/select\>', r, re.MULTILINE|re.DOTALL)
        if m:
            options = re.findall("\<option *value=\"([0-9 ]*)\"\>(.*)\<\/option\>", m.group(1))
            # with these options we can find the councillors '?XXR=0&AC=WARD&WID=<id>
            wardDict = {int(o[0].strip()):o[1] for o in options}
        else:
            options = re.findall("\<li\>\<a href=\"(\/council\/councillors.*)\"\>(.*)\<\/a\>", r)
            wardDict = {o[0]:o[1] for o in options}
        wards = [ ]
        for k in wardDict:
            name = wardDict[k]
            print("  ", name)
            wardurl = getWard(urlstr, k)
            cllrs = getCouncillors(urlstr, k)
            wards.append({"name":name, "url":wardurl, "cllrs":cllrs})
        allWards[urlstr]["wards"] = wards
    return allWards

if __name__ == "__main__":
    allWards = getAllCouncillors()
    writeToFile(allWards)

