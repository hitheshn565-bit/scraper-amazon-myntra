import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_amazon_products(search_query):
    """
    Scrapes Amazon for products based on a search query.

    Args:
        search_query (str): The product to search for.

    Returns:
        list: A list of dictionaries, where each dictionary represents a product
              with its name, price, rating, and number of reviews.
    """
    # Format the search query for the URL
    search_query = search_query.replace(' ', '+')
    # Use the IN site for consistency, as page layouts can vary by region.
    url = f"https://www.amazon.in/s?k={search_query}"
    print(f"Attempting to fetch data from: {url}")

    # Set headers to mimic a real browser request to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    products = []

    try:
        # Send a GET request to the Amazon search results page
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Response Status Code: {response.status_code}")

        if response.status_code != 200:
            print("Failed to retrieve the webpage. Amazon might be blocking the request.")
            with open("amazon_error_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("Response saved to amazon_error_page.html for inspection.")
            return []
        
        response.raise_for_status()

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all product containers on the page using a more stable selector (data-asin)
        results = soup.find_all('div', {'data-asin': True})
        print(f"Found {len(results)} potential product items.")

        if not results:
            print("No products found. Amazon might have changed its layout or blocked the request.")
            with open("amazon_no_results.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("Page content saved to amazon_no_results.html for debugging.")
            return []

        # Loop through each product container
        for item in results:
            # A crucial filter: A real product listing must have a price.
            # This skips video results, "related searches", etc.
            if not item.select_one('span.a-price'):
                continue

            product_data = {}

            # --- Extract Product Name ---
            try:
                # Corrected selector to find the name within the main H2 tag
                name_element = item.select_one('h2.a-size-medium.a-color-base.a-text-normal')
                product_data['name'] = name_element.get_text(strip=True) if name_element else 'N/A'
            except AttributeError:
                product_data['name'] = 'N/A'

            # --- Extract Product Price ---
            try:
                # The price is reliably found in the 'a-offscreen' span within the price block
                price_element = item.select_one('span.a-price span.a-offscreen')
                product_data['price'] = price_element.get_text(strip=True) if price_element else 'N/A'
            except AttributeError:
                product_data['price'] = 'N/A'

            # --- Extract Product Rating ---
            try:
                # The rating text is consistently in a span with the class 'a-icon-alt'
                rating_element = item.select_one('span.a-icon-alt')
                product_data['rating'] = rating_element.get_text(strip=True) if rating_element else 'N/A'
            except (AttributeError, KeyError):
                product_data['rating'] = 'N/A'

            # --- Extract Number of Reviews ---
            try:
                # The number of reviews is in a span with these specific classes
                reviews_element = item.select_one('span.a-size-base.s-underline-text')
                product_data['reviews'] = reviews_element.get_text(strip=True).replace(',', '') if reviews_element else 'N/A'
            except AttributeError:
                product_data['reviews'] = 'N/A'
            
            # --- Extract Product Image URL ---
            try:
                image_element = item.select_one('img.s-image')
                product_data['image_url'] = image_element['src'] if image_element else 'N/A'
            except (AttributeError, KeyError):
                product_data['image_url'] = 'N/A'


            # Add the product data to our list only if it has a valid name and price.
            if product_data.get('name') not in ['N/A', ''] and product_data.get('price') != 'N/A':
                products.append(product_data)
            
            time.sleep(0.05)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

    print(f"Successfully parsed {len(products)} products.")
    return products

def save_to_csv(products, filename="amazon_products_with_images.csv"):
    """
    Saves the scraped product data to a CSV file.
    """
    if not products:
        print("No valid product data was collected to save. The CSV file will not be created.")
        return

    headers = ['name', 'price', 'rating', 'reviews', 'image_url']

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(products)
        print(f"Successfully saved {len(products)} products to {filename}")
    except IOError as e:
        print(f"Error writing to file {filename}: {e}")

if __name__ == "__main__":
    query = input("Enter the product you want to search for on Amazon: ")
    
    if query:
        scraped_products = scrape_amazon_products(query)
        
        if scraped_products:
            save_to_csv(scraped_products)
    else:
        print("Please enter a valid search term.")
