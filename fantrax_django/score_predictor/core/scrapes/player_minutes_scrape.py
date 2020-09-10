import json
from bs4 import BeautifulSoup
from os.path  import basename
import pandas as pd
import requests
import string
import os

outdir = './core/scrapes/minutes_from_dict'

headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

# Process League Table
page = 'https://www.transfermarkt.co.uk/premier-league/startseite/wettbewerb/GB1'
tree = requests.get(page, headers = headers)
soup = BeautifulSoup(tree.content, 'html.parser')

# Create an empty list to assign these values to
teamLinks = []

# Extract all links with the correct CSS selector
links = soup.select("a.vereinprofil_tooltip")

# We need the location that the link is pointing to, so for each link, take the link location.
# Additionally, we only need the links in locations 1,3,5,etc. of our list, so loop through those only
for i in range(1,60):
    teamLinks.append(links[i].get("href"))
    teamLinks = list(set(teamLinks))
# For each location that we have taken, add the website before it - this allows us to call it later
for i in range(len(teamLinks)):
    teamLinks[i] = "https://www.transfermarkt.co.uk"+teamLinks[i]

# Create an empty list for our player links to go into
playerLinks = []

# Run the scraper through each of our 20 team links
for i in range(len(teamLinks)):

    # Download and process the team page
    page = teamLinks[i]
    tree = requests.get(page, headers = headers)
    soup = BeautifulSoup(tree.content, 'html.parser')
    # Extract all links
    links = soup.select("a.spielprofil_tooltip")
    # For each link, extract the location that it is pointing to
    for j in range(len(links)):
        playerLinks.append(links[j].get("href"))

playerLinks = list(set(playerLinks))

# Add the location to the end of the transfermarkt domain to make it ready to scrape
for j in range(len(playerLinks)):
    playerLinks[j] = "https://www.transfermarkt.co.uk"+playerLinks[j]
    playerLinks[j] = playerLinks[j].replace('profil', 'leistungsdaten')

# The page list the players more than once - let's use list(set(XXX)) to remove the duplicates
playerLinks = list(set(playerLinks))

for i in range(len(playerLinks)):

    # Take site and structure html
    page = playerLinks[i]
    tree = requests.get(page, headers=headers)
    soup = BeautifulSoup(tree.content, 'html.parser')

    # Find the player's name
    name = soup.find_all("h1")
    club_1 = soup.find_all("span", {"class": "hauptpunkt"})
    mydivsheader = soup.find_all("div", {"class": "table-header img-vat"})
    mydivs = soup.find_all("div", {"class": "responsive-table"})

    list_dfs = []
    for j in range(len(mydivs)):
        mydiv = str(mydivs[j].find('table'))
        dfs = pd.read_html(mydiv)
        df = dfs[0]
        df["Player"] = name[0].text
        df["For"] = club_1[0].text
        if "Opponent.1" in df.columns:
            splitter = df["Opponent.1"].str.split("(", n=1, expand=True)
            df["Opponent"] = splitter[0]
            df.drop(df.tail(1).index, inplace=True)
            df = df.rename({"Venue": "H/A", "For": "Club", "For.1": "Club Pos.",
                            "Unnamed: 9": "Goals", "Unnamed: 10": "Assists",
                            "Unnamed: 11": "Yellows", "Unnamed: 12": "2nd Yellows", "Unnamed: 13": "Reds",
                            "Unnamed: 14": "Minutes"}, axis=1)
        list_dfs.append(df)

    list_dfs = list_dfs[1:]

    my_div_dict = dict(zip(mydivsheader, list_dfs))

    for j, df in my_div_dict.items():
        competition = j.text.strip()
        if competition == 'Premier League':
            outname = '{0}.csv'.format(df.loc[0, 'Player'].translate({ord(c): None for c in string.whitespace}))
            fullname = os.path.join(outdir, outname)

            print(fullname)
            df.to_csv(fullname)

        else:
            pass


