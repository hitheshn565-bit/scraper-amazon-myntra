from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

# --- Flask App Initialization ---
app = Flask(__name__)

def scrape_flipkart_products(search_query):
    """
    Scrapes Flipkart for products based on a search query using Selenium to bypass blocks.
    This function contains the core scraping logic.

    Args:
        search_query (str): The product to search for.

    Returns:
        list: A list of dictionaries, where each dictionary represents a product.
    """
    # Format the search query for the URL
    search_query = search_query.replace(' ', '+')
    url = f"https://www.flipkart.com/search?q={search_query}"
    print(f"Attempting to fetch data from: {url}")

    # --- Selenium Setup ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    
    # Let Selenium manage the ChromeDriver automatically
    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    products = []
    
    try:
        driver.get(url)
        print("Waiting for page to load...")
        time.sleep(5) 

        page_source = driver.page_source
        
        # --- BeautifulSoup Parsing ---
        soup = BeautifulSoup(page_source, 'html.parser')

        # Updated selectors to handle different page layouts (list vs. grid)
        results = soup.find_all('div', {'class': '_1AtVbE'}) # List view
        if not results:
            results = soup.find_all('div', {'class': '_1xHGtK _373qXS'}) # Grid view
        
        print(f"Found {len(results)} potential product items.")

        if not results:
            print("No products found. Flipkart might have changed its layout.")
            with open("flipkart_no_results.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("Page content saved to flipkart_no_results.html for debugging.")
            return []

        # Loop through each product container
        for item in results:
            product_data = {}

            # --- Extract Product Name ---
            # More robust selectors for different view types
            name_element = item.find('div', class_='_4rR01T') # List view
            if not name_element:
                name_element = item.find('a', class_='s1Q9rs') # Grid view title
            if not name_element:
                 name_element = item.find('div', class_='_2WkVRV') # Another grid view title
            product_data['name'] = name_element.get_text(strip=True) if name_element else 'N/A'

            # --- Extract Product Price ---
            price_element = item.find('div', class_='_30jeq3')
            product_data['price'] = price_element.get_text(strip=True) if price_element else 'N/A'

            # --- Extract Product Rating ---
            rating_element = item.find('div', class_='_3LWZlK')
            product_data['rating'] = rating_element.get_text(strip=True) if rating_element else 'N/A'

            # --- Extract Number of Reviews ---
            reviews_element = item.find('span', class_='_2_R_DZ')
            product_data['reviews'] = reviews_element.get_text(strip=True) if reviews_element else 'N/A'
            
            # --- Extract Product Image URL ---
            image_element = item.find('img', class_='_396cs4')
            product_data['image_url'] = image_element['src'] if image_element else 'N/A'

            # Add the product data to our list only if it has a valid name and price.
            if product_data.get('name') not in ['N/A', ''] and product_data.get('price') != 'N/A':
                products.append(product_data)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": str(e)} # Return error as JSON
    finally:
        driver.quit()

    print(f"Successfully parsed {len(products)} products.")
    return products

# --- API Endpoint ---
@app.route('/scrape/flipkart', methods=['GET'])
def scrape_api():
    """
    API endpoint to trigger the Flipkart scraper.
    Accepts a 'q' query parameter for the search term.
    Example: /scrape/flipkart?q=laptop
    """
    # Get the search query from the request arguments
    search_query = request.args.get('q')

    if not search_query:
        return jsonify({"error": "A search query 'q' is required."}), 400

    print(f"Received API request to scrape for: {search_query}")
    
    # Call the scraper function
    scraped_data = scrape_flipkart_products(search_query)

    if isinstance(scraped_data, dict) and "error" in scraped_data:
        return jsonify(scraped_data), 500

    return jsonify(scraped_data)

# --- Main execution block ---
if __name__ == "__main__":
    # Runs the Flask app on localhost, port 5000
    # The debug=True flag provides detailed error pages and auto-reloads the server when you save changes.
    app.run(debug=True)
