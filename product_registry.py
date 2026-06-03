# Structured Item Master Registry (can be expanded with more products as needed)
registry = [
    # Newegg DDR5 Products
    {
        "mpn": "CMK32GX5M2B6000C30",
        "brand": "Corsair",
        "model": "Vengeance",
        "gen": "DDR5",
        "url": "https://www.newegg.com/corsair-vengeance-32gb-ddr5-6000-cas-latency-30-desktop-memory-black/p/N82E16820982007?Item=N82E16820982007&SoldByNewegg=1",
        "marketplace": "Newegg"
    },
    {
        "mpn": "F5-6000J3040F16GX2-RS5K",
        "brand": "G.Skill",
        "model": "Ripjaws S5",
        "gen": "DDR5",
        "url": "https://www.newegg.com/g-skill-ripjaws-s5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374369?Item=N82E16820374369&SoldByNewegg=1",
        "marketplace": "Newegg"
    },
    {
        "mpn": "F5-6000J3040F16GX2-TZ5K",
        "brand": "G.Skill",
        "model": "Trident Z5",
        "gen": "DDR5",
        "url": "https://www.newegg.com/g-skill-trident-z5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374381?Item=N82E16820374381&SoldByNewegg=1",
        "marketplace": "Newegg"
    },
    # Newegg DDR4 Products
    {
        "mpn": "CMK32GX4M2E3200C16",
        "brand": "Corsair",
        "model": "Vengeance LPX",
        "gen": "DDR4",
        "url" : "https://www.newegg.com/corsair-vengeance-lpx-32gb-ddr4-3200-cas-latency-cl16-desktop-memory-black/p/N82E16820236541?Item=N82E16820236541&SoldByNewegg=1",
        "marketplace": "Newegg"
    },
    {
        "mpn": "F5-3200J1640F16GX2-RS5K",
        "brand": "G.Skill",
        "model": "Ripjaws V",
        "gen": "DDR4",
        "url" : "https://www.newegg.com/g-skill-ripjaws-v-series-32gb-ddr4-3200-cas-latency-cl16-desktop-memory-black/p/N82E16820232091?Item=N82E16820232091&SoldByNewegg=1",
        "marketplace": "Newegg"
    },
    {
        "mpn": "F5-3600J1640F16GX2-TZ5K",
        "brand": "G.Skill",
        "model": "Trident Z RGB",
        "gen": "DDR4",
        "url" : "https://www.newegg.com/g-skill-tridentz-rgb-series-32gb-ddr4-3600-cas-latency-cl16-desktop-memory-black/p/N82E16820232906?Item=N82E16820232906&SoldByNewegg=1",
        "marketplace": "Newegg"
    },
    #Test
    {
        "mpn": "test-mpn",
        "brand": "test-brand",
        "model": "test-model",
        "gen": "test-gen",
        "url" : "https://www.newegg.com/corsair-32gb/p/0RN-001Y-00905",
        "marketplace": "test-market"
    }
]

# Function to retrieve the product registry for use in scraper.py
def get_product_registry():
    return registry
