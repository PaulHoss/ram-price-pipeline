import json
from bs4 import BeautifulSoup
import requests
import time
import random
from curl_cffi import requests as curl_requests

# This script is a diagnostic tool to verify that the target product page contains JSON-LD structured data (specifically Product Schema) which can be used for more reliable price extraction in the future.
def check_json_ld(url, request_type):
    # Standard headers to prevent immediate bot blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    headers2 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }
    headers3 = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    headers4 = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "DNT": "1",
        "Priority": "u=0, i",
        "Referer": "https://www.bestbuy.com/",
        "Sec-CH-UA": '"Google Chrome";v="136", "Chromium";v="136", "Not.A/Brand";v="24"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        }

    # Fetch the page contents
    print(f"Fetching data from: {url}...")
    
    # Use Python's built-in requests or curl_cffi's requests
    # Use Python's requests 
    if request_type == "1":
        # Timeout if request gets stalled; If RequestException is raised, print exception 
        try:
            start = time.time()
            #response = session.get(url, headers=headers3, timeout=(5, 30), stream=True)
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Request complete in {time.time() - start:.2f}s")
        except requests.exceptions.Timeout as e:
            print(f"Timeout error: {e}")
            return
        except requests.exceptions.RequestException as e:
            print(f"Request failed in {time.time() - start:.2f}s")
            print(f"{type(e).__name__}: {e}")
            return
    # Use curl_cffi's requests
    elif request_type == "2":
        try:
            start = time.time()
            session = curl_requests.Session(impersonate="chrome146")
            home = session.get("https://www.bestbuy.com/", timeout=10)
            print(f"Homepage status: {home.status_code}")
            print(f"Cookies received: {len(session.cookies)}")
            time.sleep(random.uniform(1.5, 4.0))
            response = session.get(url, timeout=10)
            #print(response.cookies)
            print(f"Request complete in {time.time() - start:.2f}s")
        except curl_requests.exceptions.Timeout as e:
            print(f"Timeout error: {e}")
            return
        except curl_requests.exceptions.RequestException as e:
            print(f"Request failed in {time.time() - start:.2f}s")
            print(f"{type(e).__name__}: {e}")
            return
    else:
        print("Invalid request type")
        return
    
    # For investigative purposes, when having issues with response.
    # Will not print if request fails.
    print(f"{'History':-^40}")
    print(response.history)
    print(f"{'URL':-^40}")
    print(response.url)
    print(f"{'Length':-^40}")
    length = len(response.text)
    print(length)
    if length == 0:
        print("Empty Response")
    elif length < 5000:
        print("Error Page Sized Response")
    elif length < 50000:
        print("Suspected Bot Challenge")
    else:
        print("Normal Page Size")

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return
    else:
        print("Status code 200 received")

    # Parse HTML content
    print(f"{'Parsing HTML...':-^40}")
    soup = BeautifulSoup(response.text, "html.parser")
    print(f"{'Parsing complete.':-^40}")
 
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
newegg_vengeanceP = "https://www.newegg.com/corsair-vengeance-32gb-ddr5-6000-cas-latency-30-desktop-memory-black/p/N82E16820982007?Item=N82E16820982007&SoldByNewegg=1"
newegg_ripjawsP = "https://www.newegg.com/g-skill-ripjaws-s5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374369?Item=N82E16820374369&SoldByNewegg=1"
newegg_tridentP = "https://www.newegg.com/g-skill-trident-z5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374381?Item=N82E16820374381&SoldByNewegg=1"

bestbuy_vengeanceP = "https://www.bestbuy.com/product/corsair-vengeance-32gb-2-x-16gb-288-pin-pc-ram-ddr5-6000-pc5-48000-desktop-memory-model-cmk32gx5m2b6000c30-black/12076557"

# Product URLs for Secondary Scraping Targets (to be used in scraper.py)
newegg_vengeanceS = "https://www.newegg.com/corsair-vengeance-lpx-32gb-ddr4-3200-cas-latency-cl16-desktop-memory-black/p/N82E16820236541?Item=N82E16820236541&SoldByNewegg=1"
newegg_ripjawsS = "https://www.newegg.com/g-skill-ripjaws-v-series-32gb-ddr4-3200-cas-latency-cl16-desktop-memory-black/p/N82E16820232091?Item=N82E16820232091&SoldByNewegg=1"
newegg_tridentS = "https://www.newegg.com/g-skill-tridentz-rgb-series-32gb-ddr4-3600-cas-latency-cl16-desktop-memory-black/p/N82E16820232906?Item=N82E16820232906&SoldByNewegg=1"

# Test a new link here, paste over existing link
test = "https://www.bestbuy.com/"

# Dictionary to store product URLs
dict_product_urls = {
    "0": test,
    "1": newegg_vengeanceP,
    "2": newegg_ripjawsP,
    "3": newegg_tridentP,
    "4": newegg_vengeanceS,
    "5": newegg_ripjawsS,
    "6": newegg_tridentS,
    "7": bestbuy_vengeanceP
}

# 
def main():
    print("Select a product to check for JSON-LD structured data:")
    for key in dict_product_urls:
        print(f"{key}. {dict_product_urls[key]}")

    key = input("Enter the number of the product you want to check (q to quit): ")
    request_type = input("Enter 1 to use standard request or enter 2 to use curl_cffi's request: ")

    if key == "q":
        print("Quitting...")
    elif key in dict_product_urls:
        check_json_ld(dict_product_urls[key], request_type)
    else:
        print("Invalid selection.")

if __name__ == "__main__":
    main()