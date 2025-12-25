from abc import ABC, abstractmethod

class BaseScraper(ABC):

    def __init__(self, company, start_date, end_date):
        self.company = company
        self.start_date = start_date
        self.end_date = end_date
        self.reviews = []

    @abstractmethod
    def scrape(self):
        pass

    def save_review(self, review):
        self.reviews.append(review)
