import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_myntra_products(search_query):
    """
    Scrapes product information from Myntra by parsing embedded JSON data.
    
    Args:
        search_query (str): The product to search for.
        
    Returns:
        list: A list of dictionaries, where each dictionary represents a product.
              Returns a dictionary with an "error" key if scraping fails.
    """
    # Myntra's search URL structure
    url = f"https://www.myntra.com/{search_query.replace(' ', '-')}"
    
    # Headers to mimic a browser visit
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"Requesting Myntra URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the script tag containing the product data (window.__myx)
        script_tag = soup.find('script', string=re.compile('window.__myx ='))

        if not script_tag:
            print("Could not find the data script tag on the Myntra page.")
            return {"error": "Failed to find product data. The site structure may have changed."}
        
        # Extract the JSON string from the script tag's content
        script_content = script_tag.string
        # Isolate the JSON object by splitting the string
        json_str = script_content.split('window.__myx = ')[1].strip().rstrip(';')

        # Parse the JSON string into a Python dictionary
        data = json.loads(json_str)
        
        # Navigate through the dictionary to get the list of products
        products = data.get('searchData', {}).get('results', {}).get('products', [])

        if not products:
            print("No products found in the page's JSON data.")
            return []

        scraped_products = []
        for product in products:
            try:
                # Combine brand and product name to create a full name
                brand = product.get('brand', '')
                name = product.get('productName', '')
                full_name = f"{brand} {name}".strip()

                # Get the price (use the discounted price if available, otherwise the standard price)
                price = product.get('discountedPrice', product.get('price', 0))
                
                # Get the primary image URL
                image_info = product.get('images', [])
                image_url = image_info[0]['src'] if image_info and 'src' in image_info[0] else 'No Image Found'
                
                # Get rating and reviews, formatting them as requested and defaulting to 'N/A'
                rating_value = product.get('rating')
                rating = f"{rating_value:.1f} out of 5 stars" if rating_value else "N/A"
                
                review_count = product.get('ratingCount')
                reviews = str(review_count) if review_count else "N/A"

                # Get the product URL
                product_url = ''
                product_link = product.get('landingPageUrl', '')
                if product_link:
                    product_url = f"https://www.myntra.com/{product_link}"

                scraped_products.append({
                    'name': full_name,
                    'price': str(price),
                    'image_url': image_url,
                    'rating': rating,
                    'reviews': reviews,
                    'url': product_url
                })
            except (KeyError, IndexError, TypeError) as e:
                # This handles cases where a specific product in the JSON has missing fields
                print(f"Skipping a product due to a data parsing error: {e}")
                continue
                
        return scraped_products

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request to Myntra: {e}")
        return {"error": f"Failed to retrieve data from Myntra. Error: {e}"}
    except json.JSONDecodeError:
        return {"error": "Failed to parse product data from the page."}
    except Exception as e:
        print(f"An unexpected error occurred while scraping Myntra: {e}")
        return {"error": f"An unexpected error occurred. Error: {e}"}

