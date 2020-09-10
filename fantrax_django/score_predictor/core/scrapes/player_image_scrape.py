import requests
from bs4 import BeautifulSoup
from os.path  import basename

headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

# Process League Table
page = 'https://www.transfermarkt.co.uk/premier-league/startseite/wettbewerb/GB1'
tree = requests.get(page, headers=headers)
soup = BeautifulSoup(tree.content, 'html.parser')

# Create an empty list to assign these values to
teamLinks = []

# Extract all links with the correct CSS selector
links = soup.select("a.vereinprofil_tooltip")
x
# We need the location that the link is pointing to, so for each link, take the link location.
# Additionally, we only need the links in locations 1,3,5,etc. of our list, so loop through those only
for i in range(1, 41, 2):
    teamLinks.append(links[i].get("href"))

# For each location that we have taken, add the website before it - this allows us to call it later
for i in range(len(teamLinks)):
    teamLinks[i] = "https://www.transfermarkt.co.uk" + teamLinks[i]

# Create an empty list for our player links to go into
playerLinks = []

# Run the scraper through each of our 20 team links
for i in range(len(teamLinks)):

    # Download and process the team page
    page = teamLinks[i]
    tree = requests.get(page, headers=headers)
    soup = BeautifulSoup(tree.content, 'html.parser')

    # Extract all links
    links = soup.select("a.spielprofil_tooltip")

    # For each link, extract the location that it is pointing to
    for j in range(len(links)):
        playerLinks.append(links[j].get("href"))

# Add the location to the end of the transfermarkt domain to make it ready to scrape
for j in range(len(playerLinks)):
    playerLinks[j] = "https://www.transfermarkt.co.uk" + playerLinks[j]

# The page list the players more than once - let's use list(set(XXX)) to remove the duplicates
playerLinks = list(set(playerLinks))

for i in range(len(playerLinks)):
    # Take site and structure html
    page = playerLinks[i]
    tree = requests.get(page, headers=headers)
    soup = BeautifulSoup(tree.content, 'html.parser')

    # Find image and save it with the player's name
    # Find the player's name
    name = soup.find_all("h1")

    # Use the name to call the image
    image = soup.find_all("img", {"title": name[0].text})

    # Extract the location of the image. We also need to strip the text after '?lm', so let's do that through '.split()'.
    src = image[0].get('src').split("?lm")[0]

    # Save the image under the player's name
    with open(name[0].text + ".jpg", "wb") as f:
        f.write(requests.get(src).content)
