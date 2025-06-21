from .base import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
import re
import logging

class EmploymentNewsScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.employmentnews.gov.in")
        self.logger = logging.getLogger(__name__)

    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape exam notifications from Employment News"""
        self.logger.info("Starting Employment News scraper")
        exams = []
        
        try:
            # Scrape latest notifications
            soup = self.get_soup(f"{self.base_url}/NewNotification.aspx")
            self.logger.info("Successfully fetched Employment News notifications page")
            
            # Find notification tables
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    try:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 3:
                            exam_info = self.extract_exam_from_row(cells)
                            if exam_info:
                                exams.append(exam_info)
                                self.logger.info(f"Successfully added exam: {exam_info['exam_name']}")
                    except Exception as e:
                        self.logger.error(f"Error processing row: {str(e)}")
                        continue
            
            # Also scrape from recent notifications section
            recent_exams = self.scrape_recent_notifications()
            exams.extend(recent_exams)
            
        except Exception as e:
            self.logger.error(f"Error scraping Employment News: {str(e)}")
        
        self.logger.info(f"Completed Employment News scraper, found {len(exams)} exams")
        return exams
    
    def scrape_recent_notifications(self) -> List[Dict[str, Any]]:
        """Scrape recent notifications section"""
        exams = []
        try:
            soup = self.get_soup(f"{self.base_url}")
            
            # Look for notification links
            notification_links = soup.find_all('a', href=True)
            
            for link in notification_links:
                link_text = self.clean_text(link.get_text())
                if self.is_exam_notification(link_text):
                    href = link.get('href', '')
                    if href and not href.startswith('http'):
                        href = self.base_url + '/' + href.lstrip('/')
                    
                    exam_info = self.extract_exam_info_from_text(link_text, href)
                    if exam_info:
                        exams.append(exam_info)
                        
        except Exception as e:
            self.logger.error(f"Error scraping recent notifications: {str(e)}")
        
        return exams
    
    def extract_exam_from_row(self, cells) -> Dict[str, Any]:
        """Extract exam information from table row"""
        try:
            cell_texts = [self.clean_text(cell.get_text()) for cell in cells]
            
            # Look for exam name and dates
            exam_name = None
            exam_date = None
            application_end = None
            
            for text in cell_texts:
                if not exam_name and self.is_exam_notification(text):
                    exam_name = text
                
                # Look for dates
                date_matches = re.findall(r'(\d{2})[-/.]\s*(\d{2})[-/.]\s*(\d{4})', text)
                for match in date_matches:
                    try:
                        day, month, year = match
                        parsed_date = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                        if not exam_date:
                            exam_date = parsed_date
                        elif not application_end:
                            application_end = parsed_date
                    except ValueError:
                        continue
            
            if exam_name and exam_date:
                return {
                    "exam_name": exam_name,
                    "conducting_body": self.get_conducting_body(exam_name),
                    "exam_date": exam_date,
                    "application_start": None,
                    "application_end": application_end,
                    "official_link": self.base_url,
                    "source_url": self.base_url
                }
                
        except Exception as e:
            self.logger.error(f"Error extracting exam from row: {str(e)}")
        
        return None
    
    def extract_exam_info_from_text(self, text: str, url: str) -> Dict[str, Any]:
        """Extract exam information from notification text"""
        try:
            # Look for dates in the text
            date_match = re.search(r'(\d{2})[-/.]\s*(\d{2})[-/.]\s*(\d{4})', text)
            
            if date_match:
                day, month, year = date_match.groups()
                exam_date = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                
                return {
                    "exam_name": text,
                    "conducting_body": self.get_conducting_body(text),
                    "exam_date": exam_date,
                    "application_start": None,
                    "application_end": None,
                    "official_link": url,
                    "source_url": self.base_url
                }
        except Exception as e:
            self.logger.error(f"Error extracting exam info from text: {str(e)}")
        
        return None
    
    def is_exam_notification(self, text: str) -> bool:
        """Check if text is an exam notification"""
        exam_keywords = [
            'recruitment', 'notification', 'exam', 'vacancy', 'post',
            'selection', 'test', 'interview', 'application', 'form',
            'upsc', 'ssc', 'ibps', 'sbi', 'railway', 'rrb', 'bank',
            'police', 'defence', 'teaching', 'clerk', 'officer'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in exam_keywords) and len(text) > 10
    
    def get_conducting_body(self, exam_name: str) -> str:
        """Determine conducting body from exam name"""
        exam_name_upper = exam_name.upper()
        
        if 'UPSC' in exam_name_upper:
            return 'UPSC'
        elif 'SSC' in exam_name_upper:
            return 'SSC'
        elif 'IBPS' in exam_name_upper or 'BANK' in exam_name_upper:
            return 'IBPS'
        elif 'SBI' in exam_name_upper:
            return 'SBI'
        elif 'RAILWAY' in exam_name_upper or 'RRB' in exam_name_upper:
            return 'RAILWAY'
        elif 'POLICE' in exam_name_upper:
            return 'POLICE'
        elif 'DEFENCE' in exam_name_upper or 'ARMY' in exam_name_upper or 'NAVY' in exam_name_upper:
            return 'DEFENCE'
        elif 'TEACHING' in exam_name_upper or 'TEACHER' in exam_name_upper:
            return 'TEACHING'
        else:
            return 'OTHER' 