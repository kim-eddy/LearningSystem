from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import time

base_url = "https://www.w3schools.com"
headers = {"User-Agent": "Mozilla/5.0"}

def scrape_topic_data(topic_names):
    """
    Scrape W3Schools JavaScript tutorial pages for the given topic names.
    Returns a list of dicts with title, description, code_examples, lists, source, url.
    """
    javascript_tutorial_url = f"{base_url}/js/"
    response = requests.get(javascript_tutorial_url, headers=headers)
    if response.status_code != 200:
        print(f" Failed to fetch JavaScript main page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.select('.w3-bar-block a[href^="/js/"]')
    topic_urls = [base_url + a['href'] for a in links if a['href'].endswith(".asp")]

    # Filter URLs by topic_names if provided
    filtered_urls = []
    for url in topic_urls:
        for topic in topic_names:
            if topic.lower() in url.lower():
                filtered_urls.append(url)
                break
    if not filtered_urls:
        print(" No matching topics found.")
        return []

    scraped_data = []
    for url in filtered_urls:
        print(f" Scraping {url}")
        page = requests.get(url, headers=headers)
        time.sleep(1)
        if page.status_code != 200:
            print(f" Skipping {url} - status {page.status_code}")
            continue

        page_soup = BeautifulSoup(page.content, 'html.parser')
        title_tag = page_soup.find('h1') or page_soup.find('h2')
        paragraphs = page_soup.find_all('p')
        code_blocks = page_soup.find_all('div', class_='w3-code')
        code_examples = [code.get_text('\n', strip=True) for code in code_blocks if code.get_text(strip=True)]

        lists = []
        for ul in page_soup.find_all('ul'):
            items = [li.get_text(strip=True) for li in ul.find_all('li') if li.get_text(strip=True)]
            if items:
                lists.append({'type': 'ul', 'items': items})
        for ol in page_soup.find_all('ol'):
            items = [li.get_text(strip=True) for li in ol.find_all('li') if li.get_text(strip=True)]
            if items:
                lists.append({'type': 'ol', 'items': items})

        if not title_tag:
            continue

        content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        scraped_data.append({
            "title": title_tag.get_text(strip=True),
            "description": content,
            "code_examples": code_examples,
            "lists": lists,
            "source": "W3Schools",
            "url": url
        })
    return scraped_data

# Optional: CLI usage for manual scraping
if __name__ == "__main__":
    topics = ["intro", "syntax", "variables"]  # Example topics
    data = scrape_topic_data(topics)
    if data:
        mongo_client = MongoClient("mongodb://emmanuel:K7154muhell@localhost:27017/?authSource=admin")
        mongo_db = mongo_client["LearningSystem"]
        mongo_collection = mongo_db["scraped_content"]
        mongo_collection.insert_many(data)
        print(f"\n Inserted {len(data)} JavaScript topics into MongoDB.")
    else:
        print(" No topics were scraped.")
