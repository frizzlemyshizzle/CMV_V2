import csv
from sys import api_version
import constants as cons

## trn ID from overview - > Network -> Steam ID -> data -> metadata -> playerId

## Historic Data - https://api.tracker.gg/api/v1/rocket-league/player-history/mmr/<playerID>

## https://api.tracker.gg/api/v2/rocket-league/standard/profile/steam/<steamID>


inputdataList = [] ## Start with empty list for RSC ID, Name, Tracker Link
linksList = [] ## Start with empty list for tracker links
identList = [] ## Start with empty list for platform & ident -> (platform/identifier)
api_linksList = [] ## Start with empty list for profile api links
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
            identList.append(ident[5]) ## Add identifiers to indentifier list
    else:
        if 'https://rocketleague.tracker.network/rocket-league/profile/' not in link:
            identList.append("BAD-LINK")
    
    for ident in identList:
        if ident != "BAD-LINK":
            api_linksList.append(cons.PROF_ENDP + ident)
        else:
            api_linksList.append(ident)




print(f"{len(api_linksList)} Entries in file")
print("-------------------------------------")
for link in api_linksList:
    countLinks += 1
    print(str(inputdataList[count][0]) + " " + str(countLinks) +") " + link)
    count += 1

    
