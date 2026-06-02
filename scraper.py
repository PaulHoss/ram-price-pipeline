## Scraper for fetching RAM prices from [currently undecided] online retailers
import requests
import json
import datetime
from bs4 import BeautifulSoup

# This function fetches the HTML content of a given URL and returns it as text. It includes error handling for network issues and non-200 HTTP responses.
def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        print(
            f"Failed to fetch. Status code: {response.status_code} for URL: {url}"
        )
    except Exception as e:
        print(f"Network error: {e}")
    return None

# This function takes the HTML content of a Newegg product page and extracts the product title and price using BeautifulSoup. It returns a dictionary with the extracted information.
def parse_newegg_price(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Product Title Extraction
    title_element = soup.find("h1", class_="product-title")
    product_title = (
        title_element.text.strip() if title_element else "Title Not Found"
    )

    # Price Extraction
    price_element = soup.find("li", class_="price-current")
    if price_element:
        price_text = price_element.text.strip()
        cleaned_price = "".join(
            c for c in price_text if c.isdigit() or c == "."
        )
        try:
            product_price = float(cleaned_price)
        except ValueError:
            product_price = None
    else:
        product_price = None

    return {"title": product_title, "price": product_price}

# Main execution block to run the scraper for a predefined list of products. It fetches the page, parses the price, and prints the results in a structured format.
if __name__ == "__main__":
    # The structured item master registry
    product_registry = [
        {
            "mpn": "CMK32GX5M2B6000C30",
            "brand": "Corsair",
            "model": "Vengeance",
            "url": "https://www.newegg.com/corsair-32gb-ddr5-intel-xmp-cmk32gx5m2b6000c30/p/N82E16820236931",
        },
        {
            "mpn": "F5-6000J3040F16GX2-RS5K",
            "brand": "G.Skill",
            "model": "Ripjaws S5",
            "url": "https://www.newegg.com/g-skill-32gb-ddr5-intel-xmp-f5-6000J3040F16GX2-RS5K/p/N82E16820374430",
        },
        {
            "mpn": "F5-6000J3040F16GX2-TZ5K",
            "brand": "G.Skill",
            "model": "Trident Z5",
            "url": "https://www.newegg.com/g-skill-32gb-ddr5-intel-xmp-f5-6000j3040F16GX2-TZ5K/p/N82E16820374358",
        },
    ]

    print("--- Starting Pipeline Processing Loop ---")

    # Loop through each product in the registry, fetch the page, parse the price, and print the results
    for item in product_registry:
        print(f"Processing MPN: {item['mpn']}...")
        html = fetch_page(item["url"])

        # Only proceed to parsing if we successfully fetched the page content
        if html:
            extracted_data = parse_newegg_price(html)

            # Combine metadata matrix with scraped real-time facts
            data_payload = {
                "timestamp": datetime.datetime.now(
                    datetime.timezone.utc
                    ).isoformat(),
                "mpn": item["mpn"],
                "brand": item["brand"],
                "model": item["model"],
                "scraped_title": extracted_data["title"],
                "price": extracted_data["price"],
                "retailer": "Newegg",
            }

            print(json.dumps(data_payload, indent=4))
            print("-" * 40)


'''Old code for parsing CSS-based price data (will be deleted later) keeping it here incase other pages do not have JSON-LD structured data and I need to fall back to this method.
def scrape_ram_price():
    # Target URL: A popular Corsair Vengeance DDR5 32GB Kit on Newegg
    url = "https://www.newegg.com/corsair-vengeance-32gb-ddr5-6000-cas-latency-30-desktop-memory-black/p/N82E16820982007"
    
    # Standard headers to prevent immediate bot blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Parse HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    
    #Isolate the script tag containing product data (if available)
    script_tag = soup.find("script", type="application/ld+json")
    if script_tag:
        #Extract and print the JSON-LD data for debugging purposes
        try:
            product_data = json.loads(script_tag.string)
            print("\n--- Product Data (from JSON-LD) ---")
            print(json.dumps(product_data, indent=2))
        except json.JSONDecodeError:
            print("Failed to parse JSON-LD data.")
    else:
        print("No JSON-LD script tag found on the page.")

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
'''