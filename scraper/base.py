from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseScraper(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        # Common headers to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Disable SSL verification
        self.session.verify = False

    def get_soup(self, url: str) -> BeautifulSoup:
        """
        Fetch a URL and return BeautifulSoup object
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            raise

    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Implement this method in each scraper to return a list of exam dictionaries
        
        Returns:
            List of dictionaries with keys:
            - exam_name (str)
            - conducting_body (str)
            - exam_date (datetime)
            - application_start (datetime, optional)
            - application_end (datetime, optional)
            - official_link (str)
            - source_url (str)
        """
        pass

    def parse_date(self, date_str: str, formats: List[str]) -> datetime:
        """
        Try to parse a date string using multiple formats
        """
        for date_format in formats:
            try:
                return datetime.strptime(date_str.strip(), date_format)
            except ValueError:
                continue
        
        self.logger.error(f"Could not parse date: {date_str}")
        raise ValueError(f"Could not parse date: {date_str}")

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        """
        if not text:
            return ""
        return " ".join(text.strip().split()) 