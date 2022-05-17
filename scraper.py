import constants as cons
import asyncio
import aiohttp
import json
import csv
from datetime import datetime
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By


chrome = Chrome('D:\Chromedriver\chromedriver.exe')
inputdataList = [] ## Start with empty list for RSC ID, Name, Tracker Link
linksList = [] ## Start with empty list for tracker links
identList = [] ## Start with empty list for platform & ident -> (platform/identifier)
profEndPointList = [] ## Start with empty list for profile api links
histEndPointList = []
trnIdList = []
finishedList = []


threesRatingdateHolder = []
threesRatingHolder = []
threesRatingList = []

doublesRatingdateHolder = []
doublesRatingHolder = []
doublesRatingList = []

''' Initial trackers reader. Reads through the input / trackers csv file and adds each row to an input list.
    Removes redundant link information and flags for incorrect links and creates the profile endpoint link 
    required to find the player's tracker network ID.
'''
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
            profEndPointList.append(cons.PROF_ENDP + ident)
        else:
            profEndPointList.append(ident)
    
    


async def pullMMR(profEndPointList):
    scrape = datetime.strptime('2022-03-11', '%Y-%m-%d')
    count = 0
    listCount = 0
    async with aiohttp.ClientSession() as client:
        client.headers.add('Connection', 'keep-alive')
        client.headers.add('Accept', 'application/json, text/plain, */*')
        client.headers.add('Origin', 'https://rocketleague.tracker.network')
        client.headers.add('Host', 'api.tracker.gg')
        client.headers.add('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15')
        client.headers.add('Accept-Language','en')
        client.headers.add('Referer','https://rocketleague.tracker.network/')
        print('Pulling MMRs for {0} player(s)...'.format(len(profEndPointList)))


        for link in profEndPointList: ## For each link in profile endpoint list ->
            if "BAD-LINK" not in link: ## If link not flagged 
                count += 1
                chrome.get(link) ## Open link with Chrome Driver
                jsonRAWOverview = chrome.find_element(by=By.TAG_NAME, value="pre").text ## Retreive page contents
                data = json.loads(jsonRAWOverview)['data'] ## Load all data as json
                trnIdList.append(str(count) + ") " + str(data['metadata']['playerId'])) ## Obtain Tracker Network ID, add to trnIdList and number

        for id in trnIdList: ## For each id in trnIdList ->
            histEndPointList.append(cons.HIST_ENDP + str(id[3:])) ## Create endpoint links and add to list
        for link in histEndPointList: ## For each endpoint link in list ->
            chrome.get(link) ## Open page with Chrome Driver
            jsonRAWOverview = chrome.find_element(by=By.TAG_NAME, value="pre").text ## Load all data as json
            threesData = json.loads(jsonRAWOverview)['data']['13'] ## Obtain all Threes MMRs
            doublesData = json.loads(jsonRAWOverview)['data']['11'] ## Obtain all Doubles MMRs


            ''' The below for loop blocks work identically aside from assigning to different lists to record data for both
                threes and doubles game modes.
            '''
            for segment in doublesData: ## For each recorded rating in doublesData ->
                doublesRatingHolder.append(str(segment['rating'])) ## Add rating to holder list
                doublesRatingdateHolder.append(segment['collectDate']) ## Add recorded date of rating to holder list
            for item in doublesRatingdateHolder: ## For each item in doubles rating holder ->
                date = str(item[0:10]) ## Take 'yyyy-mm-dd'' as date
                date = datetime.strptime(date, '%Y-%m-%d') ## Convert to time 
                if date >= scrape: ## If date of rating collection is after scrape date ->
                    dateIdx = doublesRatingdateHolder.index(item) ## Store index of date
                    doublesRatingList.append(int(doublesRatingHolder[dateIdx])) ## Add index equivalent elmnt from rating holder list to zoned list


            for segment in threesData:
                threesRatingHolder.append(str(segment['rating']))
                threesRatingdateHolder.append(segment['collectDate'])
            for item in threesRatingdateHolder:
                date = str(item[0:10])
                date = datetime.strptime(date, '%Y-%m-%d')
                if date > scrape:
                    dateIdx = threesRatingdateHolder.index(item)
                    threesRatingList.append(int(threesRatingHolder[dateIdx]))
        

            
            threesPeak = max(threesRatingList) ## Take 3s peak as max value in list
            doublesPeak = max(doublesRatingList) ## Take 2s peak as max value in list
            finishedList.append(inputdataList[listCount])
            finishedList[listCount].append(doublesPeak)
            finishedList[listCount].append(threesPeak)
            

            ## Clear lists before looping
            threesRatingdateHolder.clear()
            threesRatingHolder.clear()
            threesRatingList.clear()


            doublesRatingdateHolder.clear()
            doublesRatingHolder.clear()
            doublesRatingList.clear()
            listCount += 1



    ## Write to CSV
    with open("output.csv", 'w', newline="") as output:
        writeCount = 1
        for set in finishedList:
            print(f'Writing MMRs for entry {writeCount} of {len(finishedList)}')
            write = csv.writer(output)
            write.writerow(set)
            writeCount += 1







async def main():
    await pullMMR(profEndPointList)
    chrome.close()
asyncio.run(main())