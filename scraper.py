"""
Scraper module for extracting RAM pricing and product metadata from online retailers.
Currently supports Newegg and Best Buy, with architecture designed for future expansions.
"""

import datetime
import json
import random
import time
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests
import requests

from data_lake_manager import bronze_lake_append
from product_registry import get_product_registry


def fetch_page(url, marketplace):
    """
    Fetches the HTML content of a given URL, implementing automated fallback
    mechanisms between standard requests and curl_cffi to bypass anti-bot protections.

    Args:
        url (str): The target product page URL.
        marketplace (str): The name of the retailer marketplace.

    Returns:
        tuple: (html_content, fetch_method_token, error_message)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Enforce curl_cffi for platforms known to heavily block standard HTTP libraries
    if marketplace.lower() in ["best buy", "microcenter"]:
        html, token, msg = fetch_page_with_curl_cffi(url)
        return html, token or "DETERMINISTIC_CURL_CFFI", msg

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text, "STANDARD_REQUESTS", None
        
        # Handle rate-limiting or forbidden access via curl_cffi fallback
        if response.status_code in [403, 429]:
            html, token, msg = fetch_page_with_curl_cffi(url)
            return html, token + "_FALLBACK_STATUS_CODE", msg
        
        msg = f"Failed to fetch page. Status code: {response.status_code} for URL: {url}"
        print(msg)
        return None, "FAILED_STANDARD_REQUESTS", msg

    except requests.exceptions.Timeout as e:
        print(f"Timeout error: {e}")
        time.sleep(random.uniform(1.5, 4.0))  # Backoff delay before retry
        html, token, msg = fetch_page_with_curl_cffi(url)
        return html, token + "_FALLBACK_TIMEOUT", msg

    except requests.exceptions.RequestException as e:
        msg = f"Request failed {type(e).__name__}: {e}"
        print(msg)
        html, token, curl_cffi_msg = fetch_page_with_curl_cffi(url)
        curl_cffi_msg = curl_cffi_msg or "N/A"
        return html, token + "_FALLBACK_OTHER", f"Standard requests exception: {msg} | curl_cffi error: {curl_cffi_msg}"

    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        print(msg)
        return None, "FAILED_STANDARD_REQUESTS", msg


def fetch_page_with_curl_cffi(url):
    """
    Executes a hardened TLS-impersonated HTTP request using curl_cffi.

    Args:
        url (str): The target product page URL.

    Returns:
        tuple: (html_content, fetch_method_token, error_message)
    """
    try:
        session = curl_requests.Session(impersonate="chrome")
        # Initialize session state against the host domain to establish valid cookies/tokens
        session.get("https://www.bestbuy.com/", timeout=10)
        
        response = curl_requests.get(url, impersonate="chrome")
        if response.status_code == 200:
            return response.text, "CURL_CFFI", None
            
        msg = f"Failed to fetch page. Status code: {response.status_code} for URL: {url}"
        print(msg)
        return None, "FAILED_CURL_CFFI_STATUS_CODE", msg

    except curl_requests.exceptions.Timeout as e:
        msg = f"Timeout error: {e}"
        print(msg)
        return None, "FAILED_CURL_CFFI_TIMEOUT", msg

    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        print(msg)
        return None, "FAILED_CURL_CFFI_OTHER", msg


def parse_newegg(html):
    """
    Parses Newegg HTML to extract structured metadata from JSON-LD schema objects 
    and targets DOM elements for supplemental visual data.

    Args:
        html (str): Raw HTML content.

    Returns:
        dict: Standardized product metadata block.
    """
    soup = BeautifulSoup(html, "html.parser")
    scraped_seller = None 

    # Extract JSON-LD script elements containing search-crawler schema structured data
    script_tags = soup.find_all("script", type="application/ld+json")
    product_data = None

    for tag in script_tags:
        try:
            if not tag.string:
                continue
            data = json.loads(tag.string)
            if isinstance(data, dict) and data.get("@type") == "Product":
                product_data = data
                break
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing JSON: {e}")
            continue

    # Return safe null defaults if structured data schema cannot be isolated
    if not product_data:
        # TODO: Return error token
        print("Warning: Product Schema JSON-LD not found.")
        return {
            "mpn": None, "brand": None, "title": None, "currency": None, 
            "price": None, "availability": None, "condition": None, "seller": None
        }

    # Extract raw core metadata text directly to preserve structural integrity for debugging
    scraped_title = product_data.get("name", "TITLE_NOT_FOUND")
    scraped_brand = product_data.get("brand", "BRAND_NOT_FOUND")
    scraped_mpn = product_data.get("mpn", "MPN_NOT_FOUND")
    scraped_condition = product_data.get("itemCondition", "CONDITION_NOT_FOUND")

    # Extract commercial availability and offering conditions
    offers = product_data.get("offers", {})
    raw_price = offers.get("price") if isinstance(offers, dict) else None
    currency = offers.get("priceCurrency") if isinstance(offers, dict) else None
    availability = offers.get("availability") if isinstance(offers, dict) else None

    # Cast raw price string into a validated downstream decimal float type
    product_price = None
    if raw_price is not None:
        try:
            product_price = float(str(raw_price).strip())
        except ValueError:
            print(f"Price parsing error: {raw_price} is not a valid number.")
            product_price = None
    
    cleaned_availability = "UNKNOWN"
    if availability:
        cleaned_availability = availability.split("/")[-1] if "/" in availability else availability

    # Target DOM elements for third-party marketplace seller details missing from schema
    try:
        seller_container = soup.find("div", class_="product-seller-sold-by")
        if seller_container:
            strong_tag = seller_container.find("strong")
            if strong_tag and strong_tag.text.strip():
                scraped_seller = strong_tag.text.strip()
            elif strong_tag is None:
                scraped_seller = "ERR_INNER_TAG_MISSING"
            else:
                scraped_seller = "ERR_INNER_TAG_EMPTY"
        else:
            scraped_seller = "DEFAULT_NEWEGG" 
    except Exception as e:
        scraped_seller = "PARSE_ERROR"
        print(f"Parsing error: {str(e)}")

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


def parse_bestbuy(html):
    """
    Parses Best Buy HTML to extract product details from structured JSON-LD data.

    Args:
        html (str): Raw HTML content.

    Returns:
        dict: Standardized product metadata block.
    """
    soup = BeautifulSoup(html, "html.parser")
    script_tags = soup.find_all("script", type="application/ld+json")
    product_data = None

    for tag in script_tags:
        try:
            if not tag.string:
                continue
            data = json.loads(tag.string)
            if isinstance(data, dict) and data.get("@type") == "Product":
                product_data = data
                break
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing JSON: {e}")
            continue

    if not product_data:
        print("Warning: Product Schema JSON-LD not found.")
        return {
            "mpn": None, 
            "brand": None, 
            "title": None, 
            "currency": None, 
            "price": None, 
            "availability": None, 
            "condition": None, 
            "seller": None
        }

    scraped_title = product_data.get("name", "TITLE_NOT_FOUND")
    scraped_mpn = product_data.get("model", "MPN_NOT_FOUND")

    # Resolve various flexible data typing structures for the 'brand' schema key
    brand_raw = product_data.get("brand")
    scraped_brand = "BRAND_NOT_FOUND"

    if brand_raw:
        if isinstance(brand_raw, dict):
            scraped_brand = brand_raw.get("name", "BRAND_NOT_FOUND")
        elif isinstance(brand_raw, list) and len(brand_raw) > 0:
            first_element = brand_raw[0]
            if isinstance(first_element, dict):
                scraped_brand = first_element.get("name", "BRAND_NOT_FOUND")
            elif isinstance(first_element, str):
                scraped_brand = first_element
        elif isinstance(brand_raw, str):
            scraped_brand = brand_raw

    # Best Buy lists active schema offers within an array block
    offers = product_data.get("offers", [])
    offer = offers[0] if offers else {}
    
    raw_price = offer.get("price") if isinstance(offer, dict) else None
    currency = offer.get("priceCurrency") if isinstance(offer, dict) else None
    availability = offer.get("availableDeliveryMethod") if isinstance(offer, dict) else None
    scraped_condition = offer.get("description") if isinstance(offer, dict) else None
    scraped_seller = offer.get("seller", {}).get("name") if isinstance(offer, dict) else None

    product_price = None
    if raw_price is not None:
        try:
            product_price = float(str(raw_price).strip())
        except ValueError:
            print(f"Price parsing error: {raw_price} is not a valid number.")
            product_price = None
    
    # Infer stock availability based on presence of delivery and fulfillment options
    determined_availability = "UNKNOWN"
    if availability == []:
        determined_availability = "OutOfStock"
    elif availability and any(x.upper() in ["PICKUP", "SHIPPING"] for x in availability):
        determined_availability = "InStock"
    else:
        determined_availability = availability

    return {
        "mpn": scraped_mpn,
        "brand": scraped_brand,
        "title": scraped_title,
        "currency": currency,
        "price": product_price,
        "availability": determined_availability,
        "condition": scraped_condition,
        "seller": scraped_seller
    }


def run_pipeline():
    """
    Main orchestration function. Executes the continuous retrieval and normalization 
    pipeline across the structured catalog registry before staging payloads into 
    the data lake.
    """
    registry = get_product_registry()
    print("--- Starting Structured JSON-LD Scraper Pipeline ---")

    for item in registry:
        # Gracefully pass over unmapped platform targets
        if item["url"] == "PRODUCT_NOT_ON_SITE":
            print(f"Skipping MPN: {item['mpn']} - Not mapped for {item['marketplace']}")
            continue

        print(f"Processing MPN: {item['mpn']}...")
        html, requests_type, fetch_error = fetch_page(item["url"], item["marketplace"])

        # Timestamp tracking for analytical ingestion temporal processing
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        date = timestamp.date().isoformat()

        extracted_data = {
            "mpn": None, 
            "brand": None, 
            "title": None, 
            "currency": None, 
            "price": None, 
            "availability": None, 
            "condition": None, 
            "seller": None
        }
        parsed_data = extracted_data
        error_msg = None

        if html:
            try:
                marketplace = item["marketplace"].lower()
                if marketplace == "newegg":
                    parsed_data = parse_newegg(html)
                elif marketplace == "best buy":
                    parsed_data = parse_bestbuy(html)
                else:
                    error_msg = f"No parser registered for {marketplace}"
                                
                if parsed_data:
                    extracted_data = parsed_data
                    if extracted_data["price"] is None:
                        error_msg = "Price not found in JSON-LD schema or fetch failed."
                else:
                    error_msg = "Page loaded, but failed to parse JSON-LD data."
            except Exception as e:
                error_msg = f"Parsing code crashed: {str(e)}"
        else:
            error_msg = "Network request failed (bad status code or timeout)"

        # Set evaluation binary flag for downstream pipeline observability metrics
        pipeline_status = "Pass" if extracted_data["price"] is not None else "Fail"

        # Construct comprehensive schema entity merging master references with operational runtime metrics
        data_payload = {
            "mpn": extracted_data["mpn"],
            "brand": extracted_data["brand"],
            "gen": item["gen"],
            "model": item["model"],
            "scraped_title": extracted_data["title"],
            "currency": extracted_data["currency"],
            "price": extracted_data["price"],
            "availability": extracted_data["availability"],
            "condition": extracted_data["condition"],
            "seller": extracted_data["seller"],
            "marketplace": item["marketplace"],
            "date": date,
            "timestamp": timestamp.isoformat(),
            "pipeline_status": pipeline_status,
            "url_fetch_method": requests_type,
            "fetch_error": fetch_error,
            "parse_error": error_msg
        }
        
        # Persistent storage operation into Bronze storage layer
        try:
            saved_path = bronze_lake_append(data_payload, date)
            print(f"-> Successfully appended to Bronze Lake: {saved_path}")
        except Exception as e:
            print(f"CRITICAL: Failed to write to Bronze data lake: {e}")

        print(json.dumps(data_payload, indent=4))
        print("-" * 40)
        
        # Adaptive throttling threshold to protect script execution and distribution footprint
        time.sleep(random.uniform(1.5, 4.0))


if __name__ == "__main__":
    run_pipeline()