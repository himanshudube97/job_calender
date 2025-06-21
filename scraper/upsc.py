from .base import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
import re
import logging

class UPSCScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.upsc.gov.in")
        self.exam_url = f"{self.base_url}/examinations"
        self.logger = logging.getLogger(__name__)

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape UPSC examination calendar
        """
        self.logger.info(f"Starting UPSC scraper - Fetching URL: {self.exam_url}")
        exams = []
        
        try:
            # First try the examination page
            soup = self.get_soup(self.exam_url)
            self.logger.info("Successfully fetched UPSC examinations page")
            
            # Look for tables with examination data
            exam_tables = soup.find_all('table')
            self.logger.info(f"Found {len(exam_tables)} potential exam tables on the page")
            
            if not exam_tables:
                # Try the recruitment page as fallback
                self.logger.info("No exam tables found, trying recruitment page")
                recruitment_url = f"{self.base_url}/recruitment"
                soup = self.get_soup(recruitment_url)
                exam_tables = soup.find_all('table')
                self.logger.info(f"Found {len(exam_tables)} potential tables on recruitment page")
            
            for table_idx, table in enumerate(exam_tables):
                self.logger.info(f"Processing table {table_idx + 1}")
                
                # Try to determine if this is an exam table
                headers = [th.get_text().strip().lower() for th in table.find_all('th')]
                if not headers or not any(keyword in ' '.join(headers) for keyword in ['exam', 'date', 'notification']):
                    self.logger.info(f"Skipping table {table_idx + 1} - not an exam table")
                    continue
                
                rows = table.find_all('tr')
                self.logger.info(f"Found {len(rows)} rows in table {table_idx + 1}")
                
                for row_idx, row in enumerate(rows[1:], 1):  # Skip header row
                    cols = row.find_all(['td', 'th'])
                    if len(cols) < 2:  # Need at least name and date
                        continue
                    
                    try:
                        # Try different column combinations for exam name and date
                        exam_name = None
                        date_text = None
                        
                        # Try to find exam name and date in the columns
                        for col in cols:
                            text = self.clean_text(col.get_text())
                            if not text:
                                continue
                            
                            # Try to parse as date first
                            try:
                                # Common date formats in UPSC website
                                date_formats = [
                                    "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y",
                                    "%d %B %Y", "%d %b %Y", "%d %b, %Y",
                                    "%d-%b-%Y", "%d.%b.%Y"
                                ]
                                for fmt in date_formats:
                                    try:
                                        datetime.strptime(text, fmt)
                                        date_text = text
                                        break
                                    except ValueError:
                                        continue
                            except:
                                pass
                            
                            # If not a date and we don't have an exam name yet, it might be the exam name
                            if not date_text and not exam_name and len(text) > 5:  # Arbitrary minimum length for exam name
                                exam_name = text
                        
                        if not exam_name or not date_text:
                            self.logger.warning(f"Skipping row {row_idx} - couldn't find exam name or date")
                            continue
                            
                        self.logger.info(f"Processing exam: {exam_name}")
                        self.logger.info(f"Date text found: {date_text}")
                        
                        # Try to parse the date
                        try:
                            exam_date = None
                            for fmt in date_formats:
                                try:
                                    exam_date = datetime.strptime(date_text, fmt)
                                    break
                                except ValueError:
                                    continue
                            
                            if not exam_date:
                                raise ValueError(f"Could not parse date: {date_text}")
                                
                            self.logger.info(f"Successfully parsed date: {exam_date}")
                        except ValueError as e:
                            self.logger.warning(f"Could not parse date for exam: {exam_name}, date text: {date_text}")
                            continue
                        
                        # Try to find notification link
                        official_link = ""
                        for col in cols:
                            links = col.find_all('a')
                            for link in links:
                                href = link.get('href', '')
                                if href and ('notification' in href.lower() or 'advertisement' in href.lower()):
                                    official_link = href
                                    if not official_link.startswith('http'):
                                        official_link = self.base_url + official_link
                                    break
                            if official_link:
                                break
                                
                        if official_link:
                            self.logger.info(f"Found official link: {official_link}")
                        
                        exam_data = {
                            "exam_name": exam_name,
                            "conducting_body": "UPSC",
                            "exam_date": exam_date,
                            "official_link": official_link,
                            "source_url": self.exam_url,
                            "application_start": None,
                            "application_end": None
                        }
                        
                        exams.append(exam_data)
                        self.logger.info(f"Successfully added exam: {exam_name}")
                        
                    except Exception as e:
                        self.logger.error(f"Error processing row {row_idx}: {str(e)}")
                        continue
            
        except Exception as e:
            self.logger.error(f"Error scraping UPSC website: {str(e)}")
            raise
        
        self.logger.info(f"Completed UPSC scraper, found {len(exams)} exams")
        return exams 