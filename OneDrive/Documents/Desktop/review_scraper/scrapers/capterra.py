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
        # Run headless to avoid GUI hangs and reduce detection surface
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        url = f"https://www.capterra.com/p/{self.company}/reviews/"
        print(f"[INFO] Opening {url}")
        driver.get(url)

        wait = WebDriverWait(driver, 20)

        # ✅ ACCEPT COOKIES (CRITICAL)
        try:
            accept_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            accept_btn.click()
            time.sleep(2)
        except Exception:
            pass  # cookie banner may not appear

        # If the direct /reviews/ page returns a 404 (site requires slug), try to discover the correct product slug
        page_src = driver.page_source
        if "This page could not be found" in page_src or "404" in page_src:
            try:
                base_url = f"https://www.capterra.com/p/{self.company}/"
                print(f"[INFO] Direct reviews URL 404; trying base URL {base_url}")
                driver.get(base_url)
                time.sleep(1)
                # look for a link to reviews with the product slug
                soup_tmp = BeautifulSoup(driver.page_source, "html.parser")
                a = None
                for tag in soup_tmp.select("a[href]"):
                    href = tag.get("href")
                    if href and f"/p/{self.company}/" in href and "/reviews/" in href:
                        a = href
                        break
                if a:
                    full = a if a.startswith("http") else f"https://www.capterra.com{a}"
                    print(f"[INFO] Navigating to discovered reviews URL: {full}")
                    driver.get(full)
                    time.sleep(1)
                else:
                    print("[WARN] Could not discover reviews slug from base page")
                    # Last resort: try site search for the company identifier
                    try:
                        search_url = f"https://www.capterra.com/search?q={self.company}"
                        print(f"[INFO] Trying search page {search_url}")
                        driver.get(search_url)
                        time.sleep(1)
                        soup_search = BeautifulSoup(driver.page_source, "html.parser")
                        a = None
                        for tag in soup_search.select("a[href]"):
                            href = tag.get("href")
                            if href and "/p/" in href and "/reviews/" in href:
                                a = href
                                break
                        if a:
                            full = a if a.startswith("http") else f"https://www.capterra.com{a}"
                            print(f"[INFO] Navigating to reviews URL from search: {full}")
                            driver.get(full)
                            time.sleep(1)
                        else:
                            print("[WARN] Search did not reveal reviews link")
                    except Exception:
                        pass
            except Exception:
                pass

        # Robustly wait for review blocks using multiple fallback selectors
        selectors = [
            'article[data-testid="review-card"]',
            'div.review',
            'article.review',
            'li.review',
            'div[data-testid="review"]',
            'div[itemprop="review"]',
            'div[data-test="review"]',
            'div[class*="review"]'
        ]

        combined_selector = ",".join(selectors)

        found = False
        # Try polling + scrolling for up to ~30 seconds
        for _ in range(30):
            try:
                count = driver.execute_script(f"return document.querySelectorAll('{combined_selector}').length || 0;")
            except Exception:
                count = 0

            if count and int(count) > 0:
                found = True
                break

            # scroll and wait a bit, pages often lazy-load reviews
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        if not found:
            print("[ERROR] Reviews did not load")
            # Save page source for debugging
            try:
                safe_name = str(self.company).replace('/', '_')
                debug_path = f"debug_capterra_{safe_name}.html"
                with open(debug_path, "w", encoding="utf-8") as fh:
                    fh.write(driver.page_source)
                print(f"[DEBUG] Saved page source to {debug_path}")
            except Exception as e:
                print(f"[DEBUG] Could not save page source: {e}")
            driver.quit()
            return self.reviews

        # Extra small scrolls to ensure content is fully rendered
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(0.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        reviews = soup.select(combined_selector)

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
