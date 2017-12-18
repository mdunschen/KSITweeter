#!/usr/bin/python3

# coding: utf-8
import urllib
import urllib.request as request
import re
import html

from ksitweetbot import findCouncillorOnTwitter

councillorURLS = []
# Liverpool, Knowlsey, St Helens, Sefton, Wirral, (Halton?)
councillorURLS.append(r"https://democracy.wirral.gov.uk/mgFindMember.aspx")
councillorURLS.append(r"https://www.sthelens.gov.uk/council/councillors-elections-voting/find-your-local-councillor/")
councillorURLS.append(r"http://councillors.liverpool.gov.uk/mgFindMember.aspx")
councillorURLS.append(r"https://councillors.knowsley.gov.uk/mgFindMember.aspx")
councillorURLS.append(r"http://modgov.sefton.gov.uk/moderngov/mgFindMember.aspx")
councillorURLS.append(r"http://councillors.halton.gov.uk/mgFindMember.aspx")


def writeToFile(allWards):
    f = open("allcouncillors.tsv", "w")
    f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % ("City/Town", "URL City", "Name Ward", "URL Ward", "Name Councillor", "Email", "URL Councillor", "twitter", "twitter_desc", "twitter_url"))
    for townUrl in allWards:
        name = allWards[townUrl]["name"]
        wards = allWards[townUrl]["wards"]
        for ward in wards:
            wardname = html.unescape(ward["name"])
            wardurl = ward["url"]
            for cllr in ward["cllrs"]:
                f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (name, townUrl, wardname, wardurl, html.unescape(ward["cllrs"][cllr]['name']), ward["cllrs"][cllr]['address'], cllr, ward["cllrs"][cllr]['twitter']['handle'], ward["cllrs"][cllr]['twitter']['desc'], ward["cllrs"][cllr]['twitter']['link']))
    f.close()

def getCllrAddressInfo(cllrUrl, cllrName):
    print("url = ", cllrUrl)
    r = request.urlopen(cllrUrl).read().decode('utf-8')
    emails = re.findall(r"mailto:([\w-]+[\'\w\.]*[\w-]+\@[\w-]+\.+[\w-]+\.+[\w-]+)", r, re.MULTILINE)
    print(cllrName, emails)
    if len(emails) > 1:
        emails = [e for e in emails if e[-6:] == 'gov.uk']
    if len(set(emails)) > 1:
        # look for part of name in email
        emails = [e for e in emails if cllrName.split(' ')[-1].lower() in e]
    assert(len(emails) in (0, 1) or len(set(emails)) == 1), emails
    return {'email':emails and emails[0] or ''}


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
        cllrs = {"%s/mgUserInfo.aspx?UID=%d" % (re.match("(https?\:\/\/[a-z]*\.[a-z]*\.[a-z]*\.uk)\/", urlstr).group(1), int(o[0].strip())):{'name':o[1]} for o in councillors}

    else:
        r = request.urlopen(wardUrlStr).read().decode('utf-8')
        names = re.findall("\<h3\>(.*)\<\/h3\>", r)
        ids = re.findall("\<a href=\".*mgUserInfo\.aspx\?UID=([0-9 ]*)\&?.*\".*\>", r, re.MULTILINE)
        assert(len(names) == len(ids))
        councillors = zip(ids, names)
        cllrs = {"%s/mgUserInfo.aspx?UID=%d" % ("http://moderngov.sthelens.gov.uk", int(o[0].strip())):{'name':o[1]} for o in councillors}

    for url in cllrs:
        cllrs[url]['address'] = getCllrAddressInfo(url, cllrs[url]['name'])
    return cllrs

def getAllCouncillors():
    allWards = {}
    for urlstr in councillorURLS[:1]:
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
            wards.append({"name":html.unescape(name), "url":wardurl, "cllrs":cllrs})
            for c  in cllrs:
                cllrName = html.unescape(cllrs[c]['name'])
                lastName = (cllrName.split(' '))[-1]
                wardName = html.unescape(name)
                twitterUser = findCouncillorOnTwitter(lastName, town, wardName) or findCouncillorOnTwitter(cllrName.split(' ')[1:], town, wardName)
                if twitterUser:
                    cllrs[c]['twitter'] = {"handle":"@%s" % twitterUser.screen_name, "desc":twitterUser.description, "link":"https://twitter.com/%s" % twitterUser.screen_name}
                else:
                    cllrs[c]['twitter'] = {"handle":'', "desc":'', "link":''}

        allWards[urlstr]["wards"] = wards
    return allWards

if __name__ == "__main__":
    allWards = getAllCouncillors()
    writeToFile(allWards)


