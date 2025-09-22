# from playwright.sync_api import sync_playwright
# import time
# import csv

# START_URL = "https://data-airparif-asso.opendata.arcgis.com/search?tags=2025%2Crn2"
# OUTPUT_FILE = "article_pages.csv"

# def main():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()
#         page.goto(START_URL)

#         # Charger tous les résultats en cliquant sur "Plus de résultats"
#         while True:
#             try:
#                 load_more = page.locator("calcite-button:has-text('Plus de résultats')")
#                 if load_more.is_visible():
#                     load_more.click()
#                     time.sleep(2)  # attendre un peu pour que les nouveaux résultats se chargent
#                 else:
#                     break
#             except:
#                 break

#         # Extraire tous les liens vers les pages de détail
#         article_links = page.locator("calcite-card h3.title a").all()
#         rows = []

#         for link in article_links:
#             url = link.get_attribute("href")
#             title = link.inner_text().strip()
#             rows.append({"title": title, "page_url": url})
#             print(f"{title} -> {url}")

#         # Sauvegarder dans un CSV
#         with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
#             writer = csv.DictWriter(f, fieldnames=["title", "page_url"])
#             writer.writeheader()
#             writer.writerows(rows)

#         browser.close()
#         print(f"\n✅ {len(rows)} URLs sauvegardées dans {OUTPUT_FILE}")





# if __name__ == "__main__":
#     main()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, csv

START_URL = "https://data-airparif-asso.opendata.arcgis.com/search?tags=2025%2Crn2"
OUTPUT_FILE = "article_pages.csv"

def main():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(START_URL)
    time.sleep(5)  # laisser le temps au JS de charger

    # cliquer sur "Plus de résultats" jusqu'à disparition
    while True:
        try:
            load_more = driver.find_element("xpath", "//calcite-button[contains(., 'Plus de résultats')]")
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more)
            time.sleep(1)
            load_more.click()
            time.sleep(3)
        except:
            break

    # récupérer tous les liens <a> dans le shadow DOM
    article_links = driver.execute_script("""
    let results = [];
    document.querySelectorAll('arcgis-hub-entity-card').forEach(card => {
        try {
            const hubCard = card.shadowRoot.querySelector('arcgis-hub-card');
            const calciteCard = hubCard.shadowRoot.querySelector('calcite-card');
            const link = calciteCard.shadowRoot.querySelector('h3.title a');
            if (link) results.push({title: link.textContent.trim(), href: link.href});
        } catch(e){}
    });
    return results;
    """)

    # sauvegarder dans un CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "page_url"])
        writer.writeheader()
        for l in article_links:
            writer.writerow({"title": l["title"], "page_url": l["href"]})
            print(f"{l['title']} -> {l['href']}")

    driver.quit()
    print(f"\n{len(article_links)} URLs sauvegardées dans {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
