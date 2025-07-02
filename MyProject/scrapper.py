# import required modules
import requests

# get URL
page = requests.get("https://en.wikipedia.org/wiki/Main_Page")

# display status code
print(page.status_code)

# display scraped data
print(page.content)
# import required modules
from bs4 import BeautifulSoup
import requests

# get URL
page = requests.get("https://en.wikipedia.org/wiki/Main_Page")

# scrape webpage
soup = BeautifulSoup(page.content, 'html.parser')

# display scraped data
print(soup.prettify())# import required modules
from bs4 import BeautifulSoup
import requests

# get URL
page = requests.get("https://en.wikipedia.org/wiki/Main_Page")

# scrape webpage
soup = BeautifulSoup(page.content, 'html.parser')

list(soup.children)

# find all occurrence of p in HTML
# includes HTML tags
print(soup.find_all('p'))

print('\n\n')

# return only text
# does not include HTML tags
print(soup.find_all('p')[0].get_text())# import required modules
from bs4 import BeautifulSoup
import requests

# get URL
page = requests.get("https://en.wikipedia.org/wiki/Main_Page")

# scrape webpage
soup = BeautifulSoup(page.content, 'html.parser')

# create object
object = soup.find(id="mp-left")

# find tags
items = object.find_all(class_="mp-h2")
result = items[0]

# display tags
print(result.prettify())