import json
from bs4 import BeautifulSoup
import requests

# This script is a diagnostic tool to verify that the target product page contains JSON-LD structured data (specifically Product Schema) which can be used for more reliable price extraction in the future.
def check_json_ld(url):
    # Target URL
    # url = "https://www.newegg.com/corsair-vengeance-32gb-ddr5-6000-cas-latency-30-desktop-memory-black/p/N82E16820982007"
    
    # Standard headers to prevent immediate bot blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    
    # Fetch the page contents
    print(f"Fetching data from: {url}...")
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return

    # Parse HTML content
    soup = BeautifulSoup(response.text, "html.parser")
 
    # BeautifulSoup search for all script tags with type 'application/ld+json'
    script_tags = soup.find_all('script', type='application/ld+json')
 
    print(f"Diagnostic: Found {len(script_tags)} JSON-LD blocks on this page.")

    # Loop through each script tag and check if it contains Product Schema data
    for index, tag in enumerate(script_tags):
        if tag.string and "Product" in tag.string:
            print(f"--> Success! Block #{index} contains our Product Schema.")
            try:
                product_data = json.loads(tag.string)
                print(json.dumps(product_data, indent=2))
            except json.JSONDecodeError as e:
                print(f"JSON parsing error in block #{index}: {e}")
        else:
            print(f"Block #{index} does not contain Product Schema.")

# Product URLs for Primary Scraping Targets (to be used in scraper.py)
newegg_vengeanceP = "https://www.newegg.com/corsair-vengeance-32gb-ddr5-6000-cas-latency-30-desktop-memory-black/p/N82E16820982007"
newegg_ripjawsP = "https://www.newegg.com/g-skill-ripjaws-s5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374369?Item=N82E16820374369&SoldByNewegg=1"
newegg_tridentP = "https://www.newegg.com/g-skill-trident-z5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374381?Item=N82E16820374381&SoldByNewegg=1"

# Product URLs for Secondary Scraping Targets (to be used in scraper.py)
newegg_vengeanceS = "https://www.newegg.com/corsair-vengeance-lpx-32gb-ddr4-3200-cas-latency-cl16-desktop-memory-black/p/N82E16820236541?Item=N82E16820236541&SoldByNewegg=1"
newegg_ripjawsS = "https://www.newegg.com/g-skill-ripjaws-v-series-32gb-ddr4-3200-cas-latency-cl16-desktop-memory-black/p/N82E16820232091"
newegg_tridentS = "https://www.newegg.com/g-skill-tridentz-rgb-series-32gb-ddr4-3600-cas-latency-cl16-desktop-memory-black/p/N82E16820232906"

dict_product_urls = {
    "1": newegg_vengeanceP,
    "2": newegg_ripjawsP,
    "3": newegg_tridentP,
    "4": newegg_vengeanceS,
    "5": newegg_ripjawsS,
    "6": newegg_tridentS
}

# 
def main():
    print("Select a product to check for JSON-LD structured data:")
    for key in dict_product_urls:
        print(f"{key}. {dict_product_urls[key]}")

    key = input("Enter the number of the product you want to check (q to quit): ")

    if key == "q":
        print("Quitting...")
    elif key in dict_product_urls:
        check_json_ld(dict_product_urls[key])
    else:
        print("Invalid selection.")

if __name__ == "__main__":
    main()