## Scraper for fetching RAM prices from Newegg, [more retailers to be added in future iterations].
import requests
import json
import datetime
from bs4 import BeautifulSoup
from product_registry import get_product_registry

# URL fetching function with error handling and standard headers to prevent bot blocking
def fetch_page(url):
    '''Fetches the HTML content of a given URL and returns it as text. Handles network errors and non-200 HTTP responses.'''
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

# Newegg parsing function
def parse_newegg(html):
    '''
    Parses the HTML content of a Newegg product page to extract the product title and price.
    Returns a dictionary with the extracted data.
    '''
    soup = BeautifulSoup(html, "html.parser")

    # Initialize variables for use with visual extraction
    scraped_condition = None 
    scraped_seller = None 

    # Find all script blocks built for search spiders (Googlebot, Bingbot, etc.) that contain JSON-LD structured data.
    script_tag = soup.find_all("script", type="application/ld+json")
    product_data = None

    # Loop through all JSON-LD script tags to find the one containing Product Schema dictionary
    for tag in script_tag:
        try:
            data = json.loads(tag.string) #Convert JSON string to Python dictionary
            if isinstance(data, dict) and data.get("@type") == "Product":
                product_data = data
                break
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing JSON: {e}")
            continue

    # If we did not find Product Schema JSON-LD, we return a dictionary with "Unknown" values to indicate 
    # that the scraper failed to find structured data on this page.
    if not product_data:
        print("Warning: Product Schema JSON-LD not found.")
        return {
            "mpn": None, 
            "brand": None, 
            "title": None, 
            "currency": None, 
            "price": None, 
            "availability": None
        }

    # Extract core text directly without .strip() cleanups since we want to preserve the original formatting 
    # as much as possible for debugging purposes. We can always clean it up later if needed.
    scraped_title = product_data.get("name", "TITLE_NOT_FOUND")
    scraped_brand = product_data.get("brand", "BRAND_NOT_FOUND")
    scraped_mpn = product_data.get("mpn", "MPN_NOT_FOUND")

    # Extract price and currency from the offers sub-dictionary of the Product Schema if available
    offers = product_data.get("offers", {})
    raw_price = offers.get("price") if isinstance(offers, dict) else None
    currency = offers.get("priceCurrency") if isinstance(offers, dict) else None
    availability = offers.get("availability") if isinstance(offers, dict) else None

    # Clean and cast data types for downstream analytics storage (SQL, data warehouses, etc.)
    product_price = None
    if raw_price is not None:
        try:
            product_price = float(str(raw_price).strip()) # Cast directly to decimal float and handle any leading/trailing whitespaces
        except ValueError:
            print(f"Price parsing error: {raw_price} is not a valid number.")
            product_price = None
    
    cleaned_availability = "UNKNOWN"
    if availability:
        cleaned_availability = availability.split("/")[-1] if "/" in availability else availability

    # Visual extraction of condition and seller information, this information is not held in the structured data on Newegg
    # Condition block
    try:
        # Find parent container
        condition_container = soup.find("div", class_="product-condition")
        if condition_container:
            # Find strong tag inside container if container exists
            strong_tag = condition_container.find("strong")
            if strong_tag and strong_tag.text.strip():
                scraped_condition = strong_tag.text.strip()
        # Default to "New" if condition is not explicitly stated because Newegg does not list a condition for new products.
            else:
                scraped_condition = "New"
        else:
            scraped_condition = "New" 
    # If the HTML structure shifted we log it instead of crashing the scraper
    except Exception as e:
        scraped_condition = "PARSE_ERROR"
    # Seller block
    try:
        # Find parent container
        seller_container = soup.find("div", class_="product-seller-sold-by")
        if seller_container:
            # Find strong tag inside container if container exists
            strong_tag = seller_container.find("strong")
            if strong_tag and strong_tag.text.strip():
                scraped_seller = strong_tag.text.strip()
        # In event of failure to extract seller create status tokens to be handled downsteam 
            elif strong_tag is None:
                scraped_seller = "ERR_INNER_TAG_MISSING"
            else:
                scraped_seller = "ERR_INNER_TAG_EMPTY"
        else:
            scraped_seller = "DEFAULT_NEWEGG" 
    # If the HTML structure shifted we log it instead of crashing the scraper
    except Exception as e:
        scraped_seller = "PARSE_ERROR"

    # Return clean structured dictionary for downstream analytics layers
    return {
        "mpn": scraped_mpn,
        "brand": scraped_brand,
        "title": scraped_title,
        "currency": currency,
        "price": product_price,
        "availability": cleaned_availability,
        "condition": scraped_condition,
        "seller": scraped_seller
    }


def run_pipeline():
    '''
    Main execution block to run the scraper for a predefined list of products.
    It fetches the page, parses the price, and prints the results in a structured format.
    This is where we (not at this phase in development yet) push the data to a database, data warehouse, or analytics platform instead of just printing it.
    '''
    # Load the product registry from the product_registry module.
    registry = get_product_registry()
    
    print("--- Starting Structured JSON-LD Scraper Pipeline ---")

    # Loop through each product in the registry, fetch the page, parse the price, and print the results
    for item in registry:
        print(f"Processing MPN: {item['mpn']}...")
        html = fetch_page(item["url"])

        # Default values for the data payload in case of any failures during fetching or parsing. 
        # This ensures that we have a consistent data structure for downstream processing and analytics,
        # even if some fields are missing due to scraping issues.
        extracted_data = {"title": None, "currency": None, "price": None, "availability": None}
        error_msg = None

        # Attempt to parse the HTML content if the network request was successful.
        # We wrap this in a defensive try/except block to isolate layout errors or data discrepancies
        # from breaking the overall extraction pipeline. This way, if we encounter a page that has changed 
        # its structure or is missing expected data, we can log the error and continue processing the rest 
        # of the products in our registry without crashing the entire scraper.
        if html:
            try:
                parsed_data = parse_newegg(html)
                if parsed_data:
                    extracted_data = parsed_data
                    # If the page loaded successfully but we couldn't find a price in the JSON-LD, we want to 
                    # flag that as a specific error case in our analytics so we can track how often this happens 
                    # and potentially identify patterns (e.g., certain products or retailers that frequently fail 
                    # to include price data in their structured data).
                    if extracted_data["price"] is None:
                        error_msg = "Page loaded, but price not found in JSON-LD schema."
                else:
                    error_msg = "Page loaded, but failed to parse JSON-LD data."
            except Exception as e:
                error_msg = f"Parsing code crashed: {str(e)}"
        else:
            error_msg = "Network request failed (bad status code or timeout)"

        # Set status based on whether we successfully extracted a price. This is a simple pass/fail status that can 
        # be used in our analytics to track the overall success rate of our scraper and identify any trends or issues 
        # with specific products or retailers.
        pipeline_status = "Pass" if extracted_data["price"] is not None else "Fail"

        # Combine steady structural dimensions with real-time facts and operation metadata into a single payload for 
        # downstream analytics. This structured format allows us to easily store and analyze the data in a database 
        # or data warehouse, and also provides rich context for each price point we collect (e.g., which product it is, 
        # when we collected it, whether the scraper succeeded or failed, etc.).
        data_payload = {
            "mpn": extracted_data["mpn"],
            "brand": extracted_data["brand"],
            "gen": item["gen"],
            "model": item["model"],
            "scraped_title": extracted_data["title"],
            "currency": extracted_data["currency"],
            "price": extracted_data["price"],
            "availability": extracted_data["availability"],
            "condition" : extracted_data["condition"], # Condition of the product (e.g., New, Used, Refurbished, etc.)
            "seller": extracted_data["seller"], # Seller of product on the marketplace (e.g., Newegg, Amazon, etc.) 
            "marketplace": item["marketplace"], # Website/marketplace where product is sold (e.g., Newegg, Amazon, etc.)
            "timestamp": datetime.datetime.now(
                datetime.timezone.utc
                ).isoformat(),
            "pipeline_status": pipeline_status,
            "error": error_msg
            }
        
        # For demonstration purposes, we print the structured data payload. In a production pipeline, this would be where 
        # we push the data to a database, data warehouse, or analytics platform.
        print(json.dumps(data_payload, indent=4))
        print("-" * 40)

if __name__ == "__main__":
    run_pipeline()