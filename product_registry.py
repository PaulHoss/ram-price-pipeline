# Structured Item Master Registry (can be expanded with more products as needed)

# Function to retrieve the product registry for use in scraper.py
def get_product_registry():
    """
    Returns a master array of target hardware configurations.
    """
    products = [
        # DDR5 Products
        {
            "mpn": "CMK32GX5M2B6000C30",
            "brand": "Corsair",
            "model": "Vengeance",
            "gen": "DDR5"
        },
        {
            "mpn": "F5-6000J3040F16GX2-RS5K",
            "brand": "G.Skill",
            "model": "Ripjaws S5",
            "gen": "DDR5"
        },
        {
            "mpn": "F5-6000J3040F16GX2-TZ5K",
            "brand": "G.Skill",
            "model": "Trident Z5",
            "gen": "DDR5"
        },
        # DDR4 Products
        {
            "mpn": "CMK32GX4M2E3200C16",
            "brand": "Corsair",
            "model": "Vengeance LPX",
            "gen": "DDR4"
        },
        {
            "mpn": "F5-3200J1640F16GX2-RS5K",
            "brand": "G.Skill",
            "model": "Ripjaws V",
            "gen": "DDR4"
        },
        {
            "mpn": "F5-3600J1640F16GX2-TZ5K",
            "brand": "G.Skill",
            "model": "Trident Z RGB",
            "gen": "DDR4"
        }
    ]

    # Explicit lookup map for URLs that actually exist
    url_matrix = {
        ("CMK32GX5M2B6000C30", "Newegg"):  "https://www.newegg.com/corsair-vengeance-32gb-ddr5-6000-cas-latency-30-desktop-memory-black/p/N82E16820982007?Item=N82E16820982007&SoldByNewegg=1",
        #("CMK32GX5M2B6000C30", "Best Buy"): ,
        #("CMK32GX5M2B6000C30", ""): ,
        
        ("F5-6000J3040F16GX2-RS5K", "Newegg"): "https://www.newegg.com/g-skill-ripjaws-s5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374369?Item=N82E16820374369&SoldByNewegg=1",
        #("F5-6000J3040F16GX2-RS5K", "Best Buy"): ,
        #("F5-6000J3040F16GX2-RS5K", ""): ,
        
        ("F5-6000J3040F16GX2-TZ5K", "Newegg"): "https://www.newegg.com/g-skill-trident-z5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374381?Item=N82E16820374381&SoldByNewegg=1",
        #("F5-6000J3040F16GX2-TZ5K", "Best Buy"): ,
        #("F5-6000J3040F16GX2-TZ5K", ""): ,

        ("CMK32GX4M2E3200C16", "Newegg"): "https://www.newegg.com/corsair-vengeance-lpx-32gb-ddr4-3200-cas-latency-cl16-desktop-memory-black/p/N82E16820236541?Item=N82E16820236541&SoldByNewegg=1",
        #("CMK32GX4M2E3200C16", "Best Buy"): ,
        #("CMK32GX4M2E3200C16", ""): ,

        ("F5-3200J1640F16GX2-RS5K", "Newegg"): "https://www.newegg.com/g-skill-ripjaws-v-series-32gb-ddr4-3200-cas-latency-cl16-desktop-memory-black/p/N82E16820232091?Item=N82E16820232091&SoldByNewegg=1",
        #("F5-3200J1640F16GX2-RS5K", "Best Buy"): ,
        #("F5-3200J1640F16GX2-RS5K", ""): ,

        ("F5-3600J1640F16GX2-TZ5K", "Newegg"): "https://www.newegg.com/g-skill-tridentz-rgb-series-32gb-ddr4-3600-cas-latency-cl16-desktop-memory-black/p/N82E16820232906?Item=N82E16820232906&SoldByNewegg=1",
        #("F5-3600J1640F16GX2-TZ5K", "Best Buy"): ,
        #("F5-3600J1640F16GX2-TZ5K", ""): ,
    }

    retailers = ["Newegg", "Best Buy"]
    registry_matrix = []

    # Perform a programmatic cross-join tracking combination layers
    for product in products:
        for retailer in retailers:
            # Look up the URL using a safe .get() default if it's missing
            target_url = url_matrix.get((product["mpn"], retailer), "PRODUCT_NOT_ON_SITE")
            
            # Build the combined entry item
            item_entry = product.copy()
            item_entry["marketplace"] = retailer
            item_entry["url"] = target_url
            
            registry_matrix.append(item_entry)
            
    return registry_matrix