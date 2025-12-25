from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from utils.date_utils import parse_date, is_within_range
import time

class CapterraScraper(BaseScraper):

    def scrape(self):
        options = Options()
        options.add_argument("--start-maximized")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        # Example: hubspot → https://www.capterra.com/p/17415/HubSpot/reviews/
        url = f"https://www.capterra.com/p/{self.company}/reviews/"
        print(f"[INFO] Opening {url}")
        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception:
            print("[ERROR] Page did not load")
            driver.quit()
            return self.reviews

        # Scroll to load reviews
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        reviews = soup.select("div.review")

        print(f"[INFO] Found {len(reviews)} review blocks")

        for r in reviews:
            try:
                title = r.select_one("h3").get_text(strip=True)
                text = r.select_one("p").get_text(strip=True)
                date_str = r.select_one("time").get_text(strip=True)
                date = parse_date(date_str)

                if is_within_range(date, self.start_date, self.end_date):
                    self.save_review({
                        "title": title,
                        "review": text,
                        "date": str(date),
                        "source": "Capterra"
                    })

            except Exception:
                continue

        driver.quit()
        return self.reviews
