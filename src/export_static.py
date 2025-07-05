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
        time.sleep(10)  # Increased wait for app startup

        # Navigate to the app
        page.goto("http://localhost:8501")
        # Wait for a key element (e.g., a chart or header) to ensure full render
        page.wait_for_selector(".section-header", timeout=30000)  # 30 seconds timeout
        time.sleep(10)  # Additional wait for charts to render

        # Save the HTML with assets
        with open("docs/index.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        # Copy static assets (e.g., CSS from Streamlit)
        os.makedirs("docs/static", exist_ok=True)
        page.eval_on_selector_all("link[rel=stylesheet]", """
            links => {
                links.forEach(link => {
                    fetch(link.href).then(resp => resp.text()).then(css => {
                        const filename = link.href.split('/').pop();
                        require('fs').writeFileSync(`docs/static/${filename}`, css);
                    });
                });
            }
        """)
        # Note: This requires Node.js integration for fs, so we'll handle CSS manually below

        # Close the browser and kill Streamlit process
        browser.close()
        os.system("pkill -f streamlit")

if __name__ == "__main__":
    export_static_html()