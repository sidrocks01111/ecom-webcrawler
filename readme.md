Documentation

Web crawler in python to crawl ecommerce websites for product urls
Crawler smartly handles both static and dynamic loaded websites and saves in product_urls.json file

create virtual environment
python3 -m venv .venv

Run the crawler
pip install -r requirements.txt
python crawler.py

Enter the details and press enter to continue

Note: This script requires internet connection to fetch data.

Output:
product_urls.json

Approach on finding the product url

1. Matching the usual patterns in product url like "product", "item", "itm" etc.
2. Checking iif url contain keywords like "buy", "sku" which may indicate its a product url
3. Excluding patterns which contain keywords like "blog", "documentation"