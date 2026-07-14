from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def scrape_flipkart_products(search_query):
    """
    Scrapes Flipkart for products using Selenium with explicit waits for more reliability.
    """
    search_query = search_query.replace(' ', '+')
    url = f"https://www.flipkart.com/search?q={search_query}"
    print(f"Attempting to fetch data from Flipkart: {url}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    
    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    products = []
    try:
        driver.get(url)
        print("Waiting for Flipkart page to load...")

        # --- Close Login Popup (if it appears) ---
        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "._2KpZ6l._2doB4z, ._30XB9F")))
            close_button.click()
            print("Login popup closed.")
        except TimeoutException:
            print("No login popup appeared.")

        # --- Wait for Product Listings to be Present ---
        # A more reliable wait condition: wait for at least one product title to be visible.
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div._4rR01T, a.s1Q9rs, a.WKTcLC"))
            )
            print("Product listings found.")
        except TimeoutException:
            print("Timed out waiting for product listings to appear.")
            return []

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Using a more general selector that covers multiple layouts
        results = soup.find_all('div', class_=['_1xHGtK _373qXS', '_1AtVbE', 'cPHDOP'])
        if not results:
             results = soup.find_all('div', {'data-id': True})


        print(f"Found {len(results)} potential product items.")

        if not results:
            print("No products found. Flipkart might have changed its layout.")
            with open("flipkart_no_results.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("Page content saved to flipkart_no_results.html for debugging.")
            return []

        for item in results:
            # --- Name Selector (with multiple fallbacks) ---
            name_element = item.find('a', class_='WKTcLC') 
            if not name_element:
                name_element = item.find('div', class_='_4rR01T')
            if not name_element:
                name_element = item.find('a', class_='s1Q9rs')
            
            # --- Price Cleaning Logic (with multiple fallbacks) ---
            price_text = 'N/A'
            price_element = item.find('div', class_='Nx9bqj')
            if not price_element:
                price_element = item.find('div', class_='_30jeq3')
            
            if price_element:
                price_text = price_element.get_text(strip=True).replace('\u20b9', '').replace('₹', '').replace(',', '')

            # --- Image Selector (with multiple fallbacks) ---
            image_element = item.find('img', class_='_53J4C-')
            if not image_element:
                image_element = item.find('img', class_='_396cs4')

            product_data = {
                'name': name_element.get_text(strip=True) if name_element else 'N/A',
                'price': price_text,
                'rating': item.find('div', class_='_3LWZlK').get_text(strip=True) if item.find('div', class_='_3LWZlK') else 'N/A',
                'reviews': item.find('span', class_='_2_R_DZ').get_text(strip=True) if item.find('span', class_='_2_R_DZ') else 'N/A',
                'image_url': image_element['src'] if image_element else 'N/A'
            }

            if product_data['name'] != 'N/A' and product_data['price'] != 'N/A':
                products.append(product_data)

    except Exception as e:
        print(f"An unexpected error occurred during Flipkart scraping: {e}")
        return {"error": str(e)}
    finally:
        driver.quit()

    print(f"Successfully parsed {len(products)} products from Flipkart.")
    return products
