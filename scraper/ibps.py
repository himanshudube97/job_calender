from .base import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
import re
import logging

class IBPSScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.ibps.in")
        self.logger = logging.getLogger(__name__)

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape IBPS examination calendar
        """
        self.logger.info(f"Starting IBPS scraper - Fetching URL: {self.base_url}")
        exams = []
        
        try:
            # First try the main page for active notifications
            soup = self.get_soup(self.base_url)
            self.logger.info("Successfully fetched IBPS main page")
            
            # Look for the notification section
            notification_sections = soup.find_all('div', class_='inner_notification_title')
            self.logger.info(f"Found {len(notification_sections)} notification sections")
            
            for section in notification_sections:
                try:
                    # Get all notification links
                    links = section.find_all('a')
                    for link in links:
                        link_text = self.clean_text(link.get_text())
                        href = link.get('href', '')
                        
                        # Skip if not an exam notification
                        if not any(keyword in link_text.lower() for keyword in ['exam', 'recruitment', 'officer', 'clerk']):
                            continue
                            
                        self.logger.info(f"Processing notification: {link_text}")
                        
                        # Try to extract exam name and date from link text
                        exam_name = link_text
                        date_match = re.search(r'(\d{2}[-/.]\d{2}[-/.]\d{4}|\d{2}\s+[A-Za-z]+\s+\d{4})', link_text)
                        
                        if date_match:
                            date_text = date_match.group(1)
                            self.logger.info(f"Found date in notification: {date_text}")
                            
                            try:
                                # Try different date formats
                                date_formats = [
                                    "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y",
                                    "%d %B %Y", "%d %b %Y",
                                ]
                                exam_date = None
                                for fmt in date_formats:
                                    try:
                                        exam_date = datetime.strptime(date_text, fmt)
                                        break
                                    except ValueError:
                                        continue
                                
                                if exam_date:
                                    official_link = href if href.startswith('http') else self.base_url + href
                                    
                                    exam_data = {
                                        "exam_name": exam_name,
                                        "conducting_body": "IBPS",
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
                                        
                                        # Look for application start and end dates
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
                                    self.logger.info(f"Successfully added exam: {exam_name}")
                            except Exception as e:
                                self.logger.error(f"Error processing date {date_text}: {str(e)}")
                                continue
                except Exception as e:
                    self.logger.error(f"Error processing notification section: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping IBPS website: {str(e)}")
            raise
        
        self.logger.info(f"Completed IBPS scraper, found {len(exams)} exams")
        return exams 