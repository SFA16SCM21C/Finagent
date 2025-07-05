import time
import os
from playwright.sync_api import sync_playwright

def export_static_html():
    # Create docs directory if it doesn't exist
    os.makedirs("docs", exist_ok=True)
    
    with sync_playwright() as p:
        # Launch a browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Start Streamlit app
        os.system("streamlit run src/dashboard.py --server.port=8501 &")
        time.sleep(5)  # Wait for the app to start (adjust timing if needed)

        # Navigate to the app
        page.goto("http://localhost:8501")
        time.sleep(5)  # Wait for the page to fully render

        # Save the HTML
        with open("docs/index.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        # Close the browser and kill Streamlit process
        browser.close()
        os.system("pkill -f streamlit")

if __name__ == "__main__":
    export_static_html()