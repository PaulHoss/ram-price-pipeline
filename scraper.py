## Scraper for fetching RAM prices from [currently undecided] online retailers
import requests
from bs4 import BeautifulSoup

def scrape_ram_price():
    # Target URL: A popular Corsair Vengeance DDR5 32GB Kit on Newegg
    url = "https://www.newegg.com/corsair-vengeance-32gb-ddr5-6000-cas-latency-30-desktop-memory-black/p/N82E16820982007"
    
    # Standard headers to prevent immediate bot blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching data from: {url}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return

    # Parse HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract Product Title
    # Newegg typically stores product names in an h1 tag with class 'product-title'
    title_element = soup.find("h1", class_="product-title")
    product_title = title_element.text.strip() if title_element else "Title Not Found"
    
    # Extract Price
    # Prices on Newegg are often found in a list item with class 'price-current'
    price_element = soup.find("li", class_="price-current")
    if price_element:
        # Grabbing the strong text (dollars) and sup text (cents)
        price_text = price_element.text.strip()
        # Clean up string formatting (removing weird symbols/whitespaces)
        product_price = "".join(price_text.split())
    else:
        product_price = "Price Not Found"
        
    print("\n--- Scraping Results ---")
    print(f"Product: {product_title}")
    print(f"Price:   {product_price}")

if __name__ == "__main__":
    scrape_ram_price()