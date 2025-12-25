import argparse
import json
from datetime import datetime
from utils.validators import validate_source, validate_dates

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--start_date", required=True)
    parser.add_argument("--end_date", required=True)

    args = parser.parse_args()

    start = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    end = datetime.strptime(args.end_date, "%Y-%m-%d").date()

    validate_source(args.source)
    validate_dates(start, end)

    if args.source == "g2":
        from scrapers.g2 import G2Scraper
        scraper = G2Scraper(args.company, start, end)

    elif args.source == "capterra":
        from scrapers.capterra import CapterraScraper
        scraper = CapterraScraper(args.company, start, end)

    else:
        raise ValueError("Unsupported source")

    reviews = scraper.scrape()
    # sanitize company string for filenames (slashes cause path errors)
    safe_company = args.company.replace('/', '_')
    filename = f"reviews_{safe_company}_{args.source}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2)

    print(f"Saved {len(reviews)} reviews to {filename}")

if __name__ == "__main__":
    main()
