#!/usr/bin/python3

# coding: utf-8
import urllib
import urllib.request as request
import re

councillorURLS = []
# Liverpool, Knowlsey, St Helens, Sefton, Wirral, (Halton?)
councillorURLS.append(r"http://councillors.liverpool.gov.uk/mgFindMember.aspx")
councillorURLS.append(r"https://councillors.knowsley.gov.uk/mgFindMember.aspx")
councillorURLS.append(r"https://www.sthelens.gov.uk/council/councillors-elections-voting/find-your-local-councillor/")
councillorURLS.append(r"http://modgov.sefton.gov.uk/moderngov/mgFindMember.aspx")
councillorURLS.append(r"https://democracy.wirral.gov.uk/mgFindMember.aspx")
councillorURLS.append(r"http://councillors.halton.gov.uk/mgFindMember.aspx")


for urlstr in councillorURLS:
    r = request.urlopen(urlstr).read()
    # get all ward names and Ids
    m = re.search('.*\<select id\=\"WardId\" name=\"WardId\"\>(.*)\<\/select\>', r.decode('utf-8'), re.MULTILINE|re.DOTALL)
    if m:
        options = re.findall("\<option *value=\"[0-9 ]*\"\>(.*)\<\/option\>", m.group(1))
        print(options)
    else:
        print("no results for: ", urlstr)


