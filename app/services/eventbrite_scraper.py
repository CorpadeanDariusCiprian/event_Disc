from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time


def search_events(keyword=None, category=None, date=None, address=None, limit=5):
    # Build base URL
    base_url = "https://www.eventbrite.com/d/"

    # Build path parts
    location_part = address.replace(" ", "-").lower() if address else "online"
    category_part = category.replace(" ", "-").lower() if category else ""
    keyword_part = keyword.replace(" ", "-").lower() if keyword else ""

    # Compose URL path — Eventbrite URLs typically look like:
    # https://www.eventbrite.com/d/{location}/{category}/{keyword}/
    # We'll join only the parts that exist
    url_path_parts = [location_part]
    if category_part:
        url_path_parts.append(category_part)
    if keyword_part:
        url_path_parts.append(keyword_part)

    url_path = "/".join(url_path_parts)
    url = f"{base_url}{url_path}/"

    # Add date filter as query param if provided
    if date:
        url += f"?start_date={date}"

    print(f"Scraping URL: {url}")  # Debug print

    # Setup selenium and scrape as before (omitted for brevity)
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    event_cards = soup.select('li div[data-testid="search-event"]')

    results = []

    for card in event_cards[:limit]:  # Limit number of results
        name_tag = card.select_one('h3')
        name = name_tag.get_text(strip=True) if name_tag else "N/A"

        price_tag = card.select_one('div[class*="priceWrapper"] p')
        price = price_tag.get_text(strip=True) if price_tag else "N/A"

        organizer_tag = card.select_one('p.eds-text-color--ui-800')
        organizer = organizer_tag.get_text(strip=True) if organizer_tag else "N/A"

        datetime_tag = card.select_one('p.event-card__clamp-line--one')
        datetime_text = datetime_tag.get_text(strip=True) if datetime_tag else "N/A"
        datetime_cleaned = datetime_text.split('+')[0].strip() if datetime_text != "N/A" else "N/A"

        results.append({
            'name': name,
            'price': price,
            'organizer': organizer,
            'datetime': datetime_cleaned
        })

    return results

if __name__ == "__main__":
    keyword = "cooking"  # Example keyword
    events = scrape_eventbrite(keyword)
    for e in events:
        print(f"Event: {e['name']}")
        print(f"Price: {e['price']}")
        print(f"Organizer: {e['organizer']}")
        print(f"Date & Time: {e.get('datetime', 'N/A')}")
        print('---')