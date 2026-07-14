import requests
from bs4 import BeautifulSoup

def scrape_amazon_products(search_query):
    """
    Scrapes Amazon.in for products based on a search query.
    Note: This uses 'requests' and is faster but more likely to be blocked.
    """
    search_query = search_query.replace(' ', '+')
    url = f"https://www.amazon.in/s?k={search_query}"
    print(f"Attempting to fetch data from Amazon: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    products = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Amazon Response Status Code: {response.status_code}")
        if response.status_code != 200:
            return {"error": f"Failed to retrieve page, status code: {response.status_code}"}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('div', {'data-asin': True})
        
        for item in results:
            if not item.select_one('span.a-price'):
                continue

            # --- Price Cleaning Logic ---
            price_text = 'N/A'
            price_element = item.select_one('span.a-price span.a-offscreen')
            if price_element:
                # Remove currency symbols and commas, then strip whitespace
                price_text = price_element.get_text(strip=True).replace('\u20b9', '').replace('₹', '').replace(',', '')

            # Get product URL
            product_url = 'N/A'
            title_element = item.select_one('h2.a-size-medium.a-color-base.a-text-normal')
            if title_element and title_element.parent:
                if title_element.parent.name == 'a':
                    product_url = 'https://www.amazon.in' + title_element.parent.get('href', '')
                else:
                    url_element = item.select_one('a.a-link-normal.s-no-outline')
                    if url_element:
                        product_url = 'https://www.amazon.in' + url_element.get('href', '')

            product_data = {
                'name': title_element.get_text(strip=True) if title_element else 'N/A',
                'price': price_text,
                'rating': item.select_one('span.a-icon-alt').get_text(strip=True) if item.select_one('span.a-icon-alt') else 'N/A',
                'reviews': item.select_one('span.a-size-base.s-underline-text').get_text(strip=True).replace(',', '') if item.select_one('span.a-size-base.s-underline-text') else 'N/A',
                'image_url': item.select_one('img.s-image')['src'] if item.select_one('img.s-image') else 'N/A',
                'url': product_url
            }

            if product_data['name'] != 'N/A' and product_data['price'] != 'N/A':
                products.append(product_data)
    
    except Exception as e:
        print(f"An unexpected error occurred during Amazon scraping: {e}")
        return {"error": str(e)}

    print(f"Successfully parsed {len(products)} products from Amazon.")
    return products
