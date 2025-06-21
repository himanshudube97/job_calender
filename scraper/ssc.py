from .base import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
import re
import logging

class SSCScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://ssc.nic.in")
        self.exam_calendar_url = "https://ssc.nic.in/Portal/ExamCalendar"
        self.logger = logging.getLogger(__name__)

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape SSC examination calendar and notifications
        """
        self.logger.info(f"Starting SSC scraper - Fetching URL: {self.exam_calendar_url}")
        exams = []
        
        try:
            # First try the exam calendar page
            soup = self.get_soup(self.exam_calendar_url)
            self.logger.info("Successfully fetched SSC exam calendar page")
            
            # SSC usually displays exam calendar in tables
            calendar_tables = soup.find_all('table')
            self.logger.info(f"Found {len(calendar_tables)} calendar tables")
            
            for table in calendar_tables:
                try:
                    rows = table.find_all('tr')
                    for row in rows[1:]:  # Skip header row
                        try:
                            cols = row.find_all(['td', 'th'])
                            if len(cols) < 3:  # Need at least exam name and date
                                continue
                                
                            # Clean and extract text from columns
                            cols_text = [self.clean_text(col.get_text()) for col in cols]
                            
                            # Try to identify columns based on content
                            exam_name = None
                            exam_date = None
                            
                            for i, text in enumerate(cols_text):
                                # Look for exam name (usually contains common SSC exam abbreviations)
                                if any(keyword in text.upper() for keyword in ['CGL', 'CHSL', 'MTS', 'CPO', 'JE', 'STENO']):
                                    exam_name = text
                                
                                # Look for date patterns
                                date_match = re.search(r'(\d{2}[-/.]\d{2}[-/.]\d{4}|\d{2}\s+[A-Za-z]+\s+\d{4})', text)
                                if date_match and not exam_date:  # Take first date as exam date
                                    date_text = date_match.group(1)
                                    try:
                                        # Try different date formats
                                        date_formats = [
                                            "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y",
                                            "%d %B %Y", "%d %b %Y"
                                        ]
                                        for fmt in date_formats:
                                            try:
                                                exam_date = datetime.strptime(date_text, fmt)
                                                break
                                            except ValueError:
                                                continue
                                    except Exception as e:
                                        self.logger.error(f"Error parsing date {date_text}: {str(e)}")
                            
                            if exam_name and exam_date:
                                exam_data = {
                                    "exam_name": exam_name,
                                    "conducting_body": "SSC",
                                    "exam_date": exam_date,
                                    "official_link": self.exam_calendar_url,
                                    "source_url": self.base_url,
                                    "application_start": None,
                                    "application_end": None
                                }
                                
                                # Try to find application dates in the row
                                for text in cols_text:
                                    start_match = re.search(r'[Aa]pplication\s+[Ss]tarts?.*?(\d{2}[-/.]\d{2}[-/.]\d{4})', text)
                                    end_match = re.search(r'[Aa]pplication\s+[Ee]nds?.*?(\d{2}[-/.]\d{2}[-/.]\d{4})', text)
                                    
                                    if start_match:
                                        try:
                                            start_date = datetime.strptime(start_match.group(1), "%d-%m-%Y")
                                            exam_data["application_start"] = start_date
                                        except:
                                            pass
                                            
                                    if end_match:
                                        try:
                                            end_date = datetime.strptime(end_match.group(1), "%d-%m-%Y")
                                            exam_data["application_end"] = end_date
                                        except:
                                            pass
                                
                                exams.append(exam_data)
                                self.logger.info(f"Successfully added exam: {exam_name}")
                                
                        except Exception as e:
                            self.logger.error(f"Error processing row: {str(e)}")
                            continue
                            
                except Exception as e:
                    self.logger.error(f"Error processing table: {str(e)}")
                    continue
            
            # Also check the main page for latest notifications
            main_soup = self.get_soup(self.base_url)
            notifications = main_soup.find_all('a', href=True)
            
            for notification in notifications:
                try:
                    link_text = self.clean_text(notification.get_text())
                    href = notification.get('href', '')
                    
                    # Check if it's an exam notification
                    if any(keyword in link_text.upper() for keyword in ['CGL', 'CHSL', 'MTS', 'CPO', 'JE', 'STENO']):
                        # Try to extract exam name and date
                        date_match = re.search(r'(\d{2}[-/.]\d{2}[-/.]\d{4}|\d{2}\s+[A-Za-z]+\s+\d{4})', link_text)
                        if date_match:
                            date_text = date_match.group(1)
                            try:
                                exam_date = datetime.strptime(date_text, "%d-%m-%Y")
                                
                                official_link = href if href.startswith('http') else (
                                    self.base_url + href if href.startswith('/') else self.base_url + '/' + href
                                )
                                
                                exam_data = {
                                    "exam_name": link_text,
                                    "conducting_body": "SSC",
                                    "exam_date": exam_date,
                                    "official_link": official_link,
                                    "source_url": self.base_url,
                                    "application_start": None,
                                    "application_end": None
                                }
                                
                                # Try to get application dates from the notification page
                                try:
                                    notification_soup = self.get_soup(official_link)
                                    content = notification_soup.get_text()
                                    
                                    start_match = re.search(r'[Aa]pplication\s+[Ss]tarts?.*?(\d{2}[-/.]\d{2}[-/.]\d{4})', content)
                                    end_match = re.search(r'[Aa]pplication\s+[Ee]nds?.*?(\d{2}[-/.]\d{2}[-/.]\d{4})', content)
                                    
                                    if start_match:
                                        start_date = datetime.strptime(start_match.group(1), "%d-%m-%Y")
                                        exam_data["application_start"] = start_date
                                        
                                    if end_match:
                                        end_date = datetime.strptime(end_match.group(1), "%d-%m-%Y")
                                        exam_data["application_end"] = end_date
                                except:
                                    self.logger.warning(f"Could not fetch application dates from {official_link}")
                                
                                exams.append(exam_data)
                                self.logger.info(f"Successfully added exam from notification: {link_text}")
                                
                            except Exception as e:
                                self.logger.error(f"Error processing notification date {date_text}: {str(e)}")
                                continue
                                
                except Exception as e:
                    self.logger.error(f"Error processing notification: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping SSC website: {str(e)}")
            raise
        
        self.logger.info(f"Completed SSC scraper, found {len(exams)} exams")
        return exams 