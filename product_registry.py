# Structured Item Master Registry (can be expanded with more products as needed)
registry = [
    {
        "mpn": "CMK32GX5M2B6000C30",
        "brand": "Corsair",
        "model": "Vengeance",
        "gen": "DDR5",
        "url": "https://www.newegg.com/corsair-vengeance-32gb-ddr5-6000-cas-latency-30-desktop-memory-black/p/N82E16820982007",
    },
    {
        "mpn": "F5-6000J3040F16GX2-RS5K",
        "brand": "G.Skill",
        "model": "Ripjaws S5",
        "gen": "DDR5",
        "url": "https://www.newegg.com/g-skill-ripjaws-s5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374369?Item=N82E16820374369&SoldByNewegg=1",
    },
    {
        "mpn": "F5-6000J3040F16GX2-TZ5K",
        "brand": "G.Skill",
        "model": "Trident Z5",
        "gen": "DDR5",
        "url": "https://www.newegg.com/g-skill-trident-z5-series-32gb-ddr5-6000-cas-latency-cl30-desktop-memory-black/p/N82E16820374381?Item=N82E16820374381&SoldByNewegg=1",
    },
]

# Function to retrieve the product registry for use in scraper.py
def get_product_registry():
    return registry
