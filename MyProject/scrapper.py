from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

# Step 1: Fetch the page
url = "https://en.wikipedia.org/wiki/Main_Page"
headers = {"User-Agent": "Mozilla/5.0"}  # Important for Wikipedia

response = requests.get(url, headers=headers)

# Step 2: Check for successful fetch
if response.status_code != 200:
    print(f"Failed to retrieve page. Status code: {response.status_code}")
    exit()

# Step 3: Parse the page
soup = BeautifulSoup(response.content, 'html.parser')

# Step 4: Extract all <p> tags and display text
paragraphs = soup.find_all('p')
scraped_data = []

print("All Paragraph Texts:\n")
for p in paragraphs[:5]:  # limit to first 5 for preview
    text = p.get_text().strip()
    print(text)
    print('-' * 40)

    # Prepare for MongoDB
    scraped_data.append({
        "title": "Wikipedia Main Page",
        "description": text,
        "source": "Wikipedia",
        "url": url
    })

# Step 5: Extract content from the "mp-left" section
mp_left = soup.find(id="mp-left")
if mp_left:
    headlines = mp_left.find_all(class_="mp-h2")
    print("\nMain Page Headlines:\n")
    for h in headlines:
        print(h.get_text().strip())
else:
    print("Could not find 'mp-left' section")

# Step 6: Save to MongoDB
mongo_client = MongoClient("mongodb://emmanuel:K7154muhell@localhost:27017/?authSource=admin")
mongo_db = mongo_client["LearningSystem"]
mongo_collection = mongo_db["scraped_content"]

if scraped_data:
    mongo_collection.insert_many(scraped_data)
    print(f"\n Inserted {len(scraped_data)} items into MongoDB.")
else:
    print("No content to insert.")
