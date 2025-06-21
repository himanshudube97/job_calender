from .base import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
import re
import logging

class SBIScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://sbi.co.in")
        self.careers_url = "https://bank.sbi/web/careers"
        self.logger = logging.getLogger(__name__)

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape SBI examination calendar
        """
        self.logger.info(f"Starting SBI scraper - Fetching URL: {self.careers_url}")
        exams = []
        
        try:
            # Fetch the careers page
            soup = self.get_soup(self.careers_url)
            self.logger.info("Successfully fetched SBI careers page")
            
            # Look for the current openings/advertisements section
            # SBI usually puts recruitment notices in tables or specific divs
            recruitment_sections = soup.find_all(['div', 'table'], class_=lambda x: x and ('recruitment' in x.lower() or 'current' in x.lower()))
            self.logger.info(f"Found {len(recruitment_sections)} potential recruitment sections")
            
            for section in recruitment_sections:
                try:
                    # Get all links in the section
                    links = section.find_all('a')
                    for link in links:
                        link_text = self.clean_text(link.get_text())
                        href = link.get('href', '')
                        
                        # Skip if not a recruitment notification
                        if not any(keyword in link_text.lower() for keyword in [
                            'recruitment', 'officer', 'clerk', 'probationary', 'po ', 'specialist'
                        ]):
                            continue
                            
                        self.logger.info(f"Processing notification: {link_text}")
                        
                        # Try to extract exam name and date from link text
                        exam_name = link_text
                        
                        # Try to get more details from the notification page
                        try:
                            notification_url = href if href.startswith('http') else (
                                self.careers_url + href if href.startswith('/') else self.careers_url + '/' + href
                            )
                            notification_soup = self.get_soup(notification_url)
                            content = notification_soup.get_text()
                            
                            # Look for exam date
                            date_patterns = [
                                r'[Ee]xam(?:ination)?\s+[Dd]ate.*?(\d{2}[-/.]\d{2}[-/.]\d{4})',
                                r'[Ee]xam(?:ination)?\s+[Ss]chedule.*?(\d{2}[-/.]\d{2}[-/.]\d{4})',
                                r'[Tt]est\s+[Dd]ate.*?(\d{2}[-/.]\d{2}[-/.]\d{4})',
                            ]
                            
                            exam_date = None
                            for pattern in date_patterns:
                                date_match = re.search(pattern, content)
                                if date_match:
                                    date_text = date_match.group(1)
                                    try:
                                        exam_date = datetime.strptime(date_text, "%d-%m-%Y")
                                        break
                                    except ValueError:
                                        continue
                            
                            if not exam_date:
                                self.logger.warning(f"Could not find exam date in notification: {link_text}")
                                continue
                                
                            # Look for application dates
                            start_match = re.search(r'[Aa]pplication\s+[Ss]tarts?.*?(\d{2}[-/.]\d{2}[-/.]\d{4})', content)
                            end_match = re.search(r'[Aa]pplication\s+[Ee]nds?.*?(\d{2}[-/.]\d{2}[-/.]\d{4})', content)
                            
                            exam_data = {
                                "exam_name": exam_name,
                                "conducting_body": "SBI",
                                "exam_date": exam_date,
                                "official_link": notification_url,
                                "source_url": self.careers_url,
                                "application_start": None,
                                "application_end": None
                            }
                            
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
                            self.logger.error(f"Error processing notification page: {str(e)}")
                            continue
                            
                except Exception as e:
                    self.logger.error(f"Error processing recruitment section: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping SBI website: {str(e)}")
            raise
        
        self.logger.info(f"Completed SBI scraper, found {len(exams)} exams")
        return exams 