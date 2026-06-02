from json_checker import check_json_ld

# Product URLs for Primary Scraping Targets (to be used in scraper.py)
newegg_vengeanceP = "https://www.newegg.com/corsair-vengeance-32gb-ddr5-6000-cas-latency-30-desktop-memory-black/p/N82E16820982007"
newegg_ripjawsP = "https://www.newegg.com/g-skill-ripjaws-s5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374369?Item=N82E16820374369&SoldByNewegg=1"
newegg_tridentP = "https://www.newegg.com/g-skill-trident-z5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374381?Item=N82E16820374381&SoldByNewegg=1"

# Product URLs for Secondary Scraping Targets (to be used in scraper.py)
newegg_vengeanceS = "https://www.newegg.com/corsair-vengeance-lpx-32gb-ddr4-3200-cas-latency-cl16-desktop-memory-black/p/N82E16820236541?Item=N82E16820236541&SoldByNewegg=1"
newegg_ripjawsS = "https://www.newegg.com/g-skill-ripjaws-v-series-32gb-ddr4-3200-cas-latency-cl16-desktop-memory-black/p/N82E16820232091"
newegg_tridentS = "https://www.newegg.com/g-skill-tridentz-rgb-series-32gb-ddr4-3600-cas-latency-cl16-desktop-memory-black/p/N82E16820232906"

# Dictionary to store product URLs for easy access in scraper.py
dict_product_urls = {
    "1": newegg_vengeanceP,
    "2": newegg_ripjawsP,
    "3": newegg_tridentP,
    "4": newegg_vengeanceS,
    "5": newegg_ripjawsS,
    "6": newegg_tridentS
}

# Function to call the JSON-LD checker for a selected product URL
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