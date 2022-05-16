from itsdangerous import JSONWebSignatureSerializer
import constants as cons
import asyncio
import aiohttp
import parser as parser
import json
import csv
from datetime import datetime, date
import time

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
chrome = Chrome('D:\Chromedriver\chromedriver.exe')
inputdataList = [] ## Start with empty list for RSC ID, Name, Tracker Link
linksList = [] ## Start with empty list for tracker links
identList = [] ## Start with empty list for platform & ident -> (platform/identifier)
api_linksList = [] ## Start with empty list for profile api links
idHolder = []
endpointList = []
finishedList = []
ratingdateHolder = []
ratingdate = []
ratingHolder = []
countLinks = 0
count = 0



with open('trackers.csv') as csvfile: ## Opens Trackers input file
    trackers = csv.reader(csvfile) 

    for row in trackers: ## For every row in trackers ->
        if row[0]:
            inputdataList.append(row[0:3]) ## Add to data list -> [0]RSC ID,[1]Name,[2]Link ([start:end-1]) 

    for data in inputdataList: ## For every entry in data List ->
        linksList.append(data[2]) ## Add trackers links to links list

    for link in linksList: ## For every link in link list ->
        if 'https://rocketleague.tracker.network/rocket-league/profile/' in link:
            ident = link.split('/', 5) ## Remove link info (Counts # of '/'), keep identifiers
            ident = [ident.replace('/overview', '') for ident in ident] ## Remove '/overview' from links
            if "mmr?playlist=" in ident[5]:
                ident[5] = ident[5][0:14]
            identList.append(ident[5]) ## Add identifiers to indentifier list
    else:
        if 'https://rocketleague.tracker.network/rocket-league/profile/' not in link:
            identList.append("BAD-LINK")
    
    for ident in identList:
        if ident != "BAD-LINK":
            api_linksList.append(cons.PROF_ENDP + ident)
        else:
            api_linksList.append(ident)
    
    
async def pullMMR(api_linksList):
    scrape = datetime.strptime('2022-04-11', '%Y-%m-%d')
    count = 0
    zonedRatingList = []
    async with aiohttp.ClientSession() as client:
        client.headers.add('Connection', 'keep-alive')
        client.headers.add('Accept', 'application/json, text/plain, */*')
        client.headers.add('Origin', 'https://rocketleague.tracker.network')
        client.headers.add('Host', 'api.tracker.gg')
        client.headers.add('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15')
        client.headers.add('Accept-Language','en')
        client.headers.add('Referer','https://rocketleague.tracker.network/')
        print('Pulling MMRs for {0} player(s)...'.format(len(api_linksList)))
        for link in api_linksList:
            if "BAD-LINK" not in link:
                count += 1
                chrome.get(link)
                jsonRAWOverview = chrome.find_element(by=By.TAG_NAME, value="pre").text          
                data = json.loads(jsonRAWOverview)['data']
                idHolder.append(str(count) + ") " + str(data['metadata']['playerId']))

        for id in idHolder:
            endpointList.append(cons.HIST_ENDP + str(id[3:]))
        
        for link in endpointList:
            chrome.get(link)
            jsonRAWOverview = chrome.find_element(by=By.TAG_NAME, value="pre").text          
            data = json.loads(jsonRAWOverview)['data']['13']
            for segment in data:
                ratingHolder.append(str(segment['rating']))
                ratingdateHolder.append(segment['collectDate'])
            for item in ratingdateHolder:
                date = str(item[0:10])
                date = datetime.strptime(date, '%Y-%m-%d')
                if date > scrape:
                    dateIdx = ratingdateHolder.index(item)
                    ratingdate.append(date)
            peak = max(ratingHolder)
            finishedList.append(inputdataList[0])
            finishedList[0].append(peak)
        print(finishedList)





async def main():
    await pullMMR(api_linksList)
    chrome.close()
asyncio.run(main())

# print(f"{len(api_linksList)} Entries in file")
# print("-------------------------------------")
# for link in api_linksList:
#     countLinks += 1
#     print(str(inputdataList[count][0]) + " " + str(countLinks) +") " + link)
#     count += 1
#     pullMMR(api_linksList)






