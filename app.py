from flask import Flask, request, jsonify
from flask_cors import CORS
# Import the scraper functions from their respective modules
from scraper_api.amazon import scrape_amazon_products
# from scraper_api.flipkart import scrape_flipkart_products
from scraper_api.myntra_scraper import scrape_myntra_products

# --- Flask App Initialization ---
app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

#==============================================================================
# API ENDPOINTS
#==============================================================================
@app.route('/scrape/amazon', methods=['GET'])
def scrape_amazon_api():
    """ API endpoint for Amazon. Ex: /scrape/amazon?q=laptop """
    search_query = request.args.get('q')
    if not search_query:
        return jsonify({"error": "A search query 'q' is required."}), 400
    
    print(f"Received API request to scrape Amazon for: {search_query}")
    scraped_data = scrape_amazon_products(search_query)
    
    if isinstance(scraped_data, dict) and "error" in scraped_data:
        return jsonify(scraped_data), 500
    return jsonify(scraped_data)


@app.route('/scrape/myntra', methods=['GET'])
def scrape_myntra_api():
    """ API endpoint for Myntra. Ex: /scrape/myntra?q=shirts """
    search_query = request.args.get('q')
    if not search_query:
        return jsonify({"error": "A search query 'q' is required."}), 400
    
    print(f"Received API request to scrape Myntra for: {search_query}")
    scraped_data = scrape_myntra_products(search_query)

    if isinstance(scraped_data, dict) and "error" in scraped_data:
        return jsonify(scraped_data), 500
    return jsonify(scraped_data)

# @app.route('/scrape/flipkart', methods=['GET'])
# def scrape_flipkart_api():
#     """ API endpoint for Flipkart. Ex: /scrape/flipkart?q=mobile """
#     search_query = request.args.get('q')
#     if not search_query:
#         return jsonify({"error": "A search query 'q' is required."}), 400
    
#     print(f"Received API request to scrape Flipkart for: {search_query}")
#     scraped_data = scrape_flipkart_products(search_query)

#     if isinstance(scraped_data, dict) and "error" in scraped_data:
#         return jsonify(scraped_data), 500
#     return jsonify(scraped_data)

# --- Main execution block ---
if __name__ == "__main__":
    # To run this app:
    # 1. Make sure you have the folder structure correct.
    # 2. Run 'python app.py' in your terminal.
    app.run(host='0.0.0.0', port=5000, debug=True)
