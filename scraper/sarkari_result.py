from .base import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
import re
import logging

class SarkariResultScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.sarkariresult.com")
        self.logger = logging.getLogger(__name__)
        
        # Common keywords to identify exam notifications
        self.exam_keywords = [
            'UPSC', 'IAS', 'SSC', 'IBPS', 'SBI', 'RRB', 'NTPC', 'RAILWAY',
            'BANK', 'PO', 'CLERK', 'JE', 'CGL', 'CHSL', 'MTS', 'NDA', 'CDS',
            'CIVIL SERVICES', 'ENGINEERING SERVICES'
        ]
        
        # Common date patterns in notifications
        self.date_patterns = [
            r'(\d{2})(?:th|st|nd|rd)?\s+([A-Za-z]+)\s+(\d{4})',  # 15th August 2024
            r'(\d{2})[-/.]\s*(\d{2})[-/.]\s*(\d{4})',  # 15-08-2024 or 15/08/2024
            r'(\d{2})\s+([A-Za-z]+)\s+(\d{4})',  # 15 August 2024
        ]
        
        # Month name variations
        self.month_names = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'sept': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }

    def parse_date(self, date_text: str) -> datetime:
        """Parse date from various formats"""
        for pattern in self.date_patterns:
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                day, month, year = match.groups()
                
                # Convert month name to number if it's text
                if month.isalpha():
                    month = str(self.month_names.get(month.lower(), 1)).zfill(2)
                
                try:
                    return datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                except ValueError:
                    continue
        return None

    def get_conducting_body(self, text: str) -> str:
        """Determine the conducting body from notification text"""
        text_upper = text.upper()
        
        if any(x in text_upper for x in ['UPSC', 'IAS', 'CIVIL SERVICE', 'ENGINEERING SERVICE']):
            return 'UPSC'
        elif any(x in text_upper for x in ['SSC', 'CGL', 'CHSL', 'MTS']):
            return 'SSC'
        elif 'IBPS' in text_upper:
            return 'IBPS'
        elif 'SBI' in text_upper:
            return 'SBI'
        elif any(x in text_upper for x in ['RAILWAY', 'RRB', 'NTPC']):
            return 'RAILWAY'
        elif 'BANK' in text_upper:
            return 'BANK'
        else:
            return 'OTHER'

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape exam notifications from Sarkari Result
        """
        self.logger.info(f"Starting Sarkari Result scraper - Fetching URL: {self.base_url}")
        exams = []
        
        try:
            # Get the main page
            soup = self.get_soup(self.base_url)
            self.logger.info("Successfully fetched main page")
            
            # Find all notification links
            notifications = soup.find_all('a', href=True)
            self.logger.info(f"Found {len(notifications)} potential notifications")
            
            for notification in notifications:
                try:
                    link_text = self.clean_text(notification.get_text())
                    href = notification.get('href', '')
                    
                    # Skip if not an exam notification
                    if not any(keyword in link_text.upper() for keyword in self.exam_keywords):
                        continue
                    
                    self.logger.info(f"Processing notification: {link_text}")
                    
                    # Try to get more details from the notification page
                    try:
                        notification_url = href if href.startswith('http') else (
                            self.base_url + href if href.startswith('/') else self.base_url + '/' + href
                        )
                        notification_soup = self.get_soup(notification_url)
                        content = notification_soup.get_text()
                        
                        # Extract dates
                        exam_date = None
                        application_start = None
                        application_end = None
                        
                        # Look for exam date
                        exam_date_patterns = [
                            r'[Ee]xam\s+[Dd]ate.*?(\d{2}[-/.]\d{2}[-/.]\d{4}|\d{2}\s+[A-Za-z]+\s+\d{4})',
                            r'[Ee]xamination\s+[Dd]ate.*?(\d{2}[-/.]\d{2}[-/.]\d{4}|\d{2}\s+[A-Za-z]+\s+\d{4})',
                            r'[Tt]est\s+[Dd]ate.*?(\d{2}[-/.]\d{2}[-/.]\d{4}|\d{2}\s+[A-Za-z]+\s+\d{4})'
                        ]
                        
                        for pattern in exam_date_patterns:
                            match = re.search(pattern, content)
                            if match:
                                exam_date = self.parse_date(match.group(1))
                                if exam_date:
                                    break
                        
                        # Look for application dates
                        start_match = re.search(
                            r'[Aa]pplication\s+[Ss]tarts?.*?(\d{2}[-/.]\d{2}[-/.]\d{4}|\d{2}\s+[A-Za-z]+\s+\d{4})',
                            content
                        )
                        end_match = re.search(
                            r'[Aa]pplication\s+[Ee]nds?.*?(\d{2}[-/.]\d{2}[-/.]\d{4}|\d{2}\s+[A-Za-z]+\s+\d{4})',
                            content
                        )
                        
                        if start_match:
                            application_start = self.parse_date(start_match.group(1))
                        if end_match:
                            application_end = self.parse_date(end_match.group(1))
                        
                        if exam_date:
                            conducting_body = self.get_conducting_body(link_text)
                            
                            exam_data = {
                                "exam_name": link_text,
                                "conducting_body": conducting_body,
                                "exam_date": exam_date,
                                "application_start": application_start,
                                "application_end": application_end,
                                "official_link": notification_url,
                                "source_url": self.base_url
                            }
                            
                            exams.append(exam_data)
                            self.logger.info(f"Successfully added exam: {link_text}")
                            
                    except Exception as e:
                        self.logger.error(f"Error processing notification page: {str(e)}")
                        continue
                        
                except Exception as e:
                    self.logger.error(f"Error processing notification: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping Sarkari Result website: {str(e)}")
            raise
        
        self.logger.info(f"Completed Sarkari Result scraper, found {len(exams)} exams")
        return exams 