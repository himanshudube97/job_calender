from .base import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
import re
import logging

class FreshersLiveScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.fresherslive.com")
        # Update to the correct URL
        self.exam_calendar_url = "https://www.fresherslive.com/government-jobs/exam-calendar"
        self.latest_jobs_url = "https://www.fresherslive.com/government-jobs/latest"
        self.logger = logging.getLogger(__name__)
        
        # Common exam categories
        self.exam_categories = [
            'UPSC', 'SSC', 'BANK', 'RAILWAY', 'DEFENCE', 'TEACHING',
            'STATE PSC', 'POLICE', 'ENGINEERING', 'MEDICAL'
        ]

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape exam notifications from FreshersLive
        """
        self.logger.info(f"Starting FreshersLive scraper")
        exams = []
        
        try:
            # Try exam calendar page first
            try:
                self.logger.info(f"Fetching exam calendar URL: {self.exam_calendar_url}")
                exams.extend(self.scrape_calendar_page())
            except Exception as e:
                self.logger.error(f"Error scraping exam calendar page: {str(e)}")
            
            # Try latest jobs page as backup
            try:
                self.logger.info(f"Fetching latest jobs URL: {self.latest_jobs_url}")
                exams.extend(self.scrape_latest_jobs())
            except Exception as e:
                self.logger.error(f"Error scraping latest jobs page: {str(e)}")
            
            if not exams:
                self.logger.warning("No exams found from any source")
            
        except Exception as e:
            self.logger.error(f"Error in FreshersLive scraper: {str(e)}")
            raise
        
        self.logger.info(f"Completed FreshersLive scraper, found {len(exams)} exams")
        return exams
    
    def scrape_calendar_page(self) -> List[Dict[str, Any]]:
        """Scrape the exam calendar page"""
        exams = []
        soup = self.get_soup(self.exam_calendar_url)
        
        # Look for tables and divs with exam information
        exam_sections = soup.find_all(['table', 'div'], class_=lambda x: x and any(
            keyword.lower() in x.lower() for keyword in ['exam', 'schedule', 'calendar']
        ))
        
        self.logger.info(f"Found {len(exam_sections)} exam sections in calendar")
        
        for section in exam_sections:
            try:
                if section.name == 'table':
                    exams.extend(self.process_table(section))
                else:
                    exams.extend(self.process_div(section))
            except Exception as e:
                self.logger.error(f"Error processing section: {str(e)}")
                continue
        
        return exams
    
    def scrape_latest_jobs(self) -> List[Dict[str, Any]]:
        """Scrape the latest jobs page for exam notifications"""
        exams = []
        soup = self.get_soup(self.latest_jobs_url)
        
        # Look for job/exam cards or listings
        job_sections = soup.find_all(['div', 'article'], class_=lambda x: x and any(
            keyword.lower() in x.lower() for keyword in ['job', 'vacancy', 'notification']
        ))
        
        self.logger.info(f"Found {len(job_sections)} job sections")
        
        for section in job_sections:
            try:
                # Process each job listing
                title = section.find(['h2', 'h3', 'h4', 'a'])
                if not title:
                    continue
                    
                title_text = self.clean_text(title.get_text())
                
                # Skip if not an exam notification
                if not any(category.lower() in title_text.lower() for category in self.exam_categories):
                    continue
                
                self.logger.info(f"Processing job listing: {title_text}")
                
                # Get the detailed page URL
                link = title.get('href', '') if title.name == 'a' else title.find_parent('a', href=True)
                if link:
                    href = link.get('href', '') if isinstance(link, str) else link
                    notification_url = href if href.startswith('http') else (
                        self.base_url + href if href.startswith('/') else self.base_url + '/' + href
                    )
                    
                    exam_info = self.extract_exam_info_from_page(notification_url, title_text)
                    if exam_info:
                        exams.append(exam_info)
                        
            except Exception as e:
                self.logger.error(f"Error processing job section: {str(e)}")
                continue
        
        return exams
    
    def process_table(self, table) -> List[Dict[str, Any]]:
        """Process a table containing exam information"""
        exams = []
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Skip header row
            try:
                cols = row.find_all(['td', 'th'])
                if len(cols) < 2:
                    continue
                
                exam_info = self.extract_exam_info_from_cols(cols)
                if exam_info:
                    exams.append(exam_info)
                    
            except Exception as e:
                self.logger.error(f"Error processing table row: {str(e)}")
                continue
        
        return exams
    
    def process_div(self, div) -> List[Dict[str, Any]]:
        """Process a div containing exam information"""
        exams = []
        links = div.find_all('a', href=True)
        
        for link in links:
            try:
                link_text = self.clean_text(link.get_text())
                href = link.get('href', '')
                
                if not any(category.lower() in link_text.lower() for category in self.exam_categories):
                    continue
                
                self.logger.info(f"Processing notification: {link_text}")
                
                notification_url = href if href.startswith('http') else (
                    self.base_url + href if href.startswith('/') else self.base_url + '/' + href
                )
                
                exam_info = self.extract_exam_info_from_page(notification_url, link_text)
                if exam_info:
                    exams.append(exam_info)
                    
            except Exception as e:
                self.logger.error(f"Error processing link: {str(e)}")
                continue
        
        return exams
    
    def extract_exam_info_from_cols(self, cols) -> Dict[str, Any]:
        """Extract exam information from table columns"""
        try:
            cols_text = [self.clean_text(col.get_text()) for col in cols]
            
            exam_name = None
            exam_date = None
            conducting_body = None
            
            for text in cols_text:
                if any(category in text.upper() for category in self.exam_categories):
                    exam_name = text
                    conducting_body = text.split()[0]
                
                date_match = re.search(
                    r'(\d{2})[-/.]\s*(\d{2})[-/.]\s*(\d{4})',
                    text
                )
                if date_match and not exam_date:
                    try:
                        day, month, year = date_match.groups()
                        exam_date = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                    except ValueError:
                        continue
            
            if exam_name and exam_date:
                return {
                    "exam_name": exam_name,
                    "conducting_body": conducting_body or "OTHER",
                    "exam_date": exam_date,
                    "application_start": None,
                    "application_end": None,
                    "official_link": self.exam_calendar_url,
                    "source_url": self.base_url
                }
                
        except Exception as e:
            self.logger.error(f"Error extracting info from columns: {str(e)}")
        
        return None
    
    def extract_exam_info_from_page(self, url: str, title: str) -> Dict[str, Any]:
        """Extract exam information from a notification page"""
        try:
            soup = self.get_soup(url)
            content = soup.get_text()
            
            # Look for exam date
            date_match = re.search(
                r'[Ee]xam\s+[Dd]ate.*?(\d{2})[-/.]\s*(\d{2})[-/.]\s*(\d{4})',
                content
            )
            
            if date_match:
                try:
                    day, month, year = date_match.groups()
                    exam_date = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                    
                    # Look for application dates
                    start_match = re.search(
                        r'[Aa]pplication\s+[Ss]tarts?.*?(\d{2})[-/.]\s*(\d{2})[-/.]\s*(\d{4})',
                        content
                    )
                    end_match = re.search(
                        r'[Aa]pplication\s+[Ee]nds?.*?(\d{2})[-/.]\s*(\d{2})[-/.]\s*(\d{4})',
                        content
                    )
                    
                    application_start = None
                    application_end = None
                    
                    if start_match:
                        day, month, year = start_match.groups()
                        application_start = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                    
                    if end_match:
                        day, month, year = end_match.groups()
                        application_end = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                    
                    # Determine conducting body from title
                    conducting_body = "OTHER"
                    for category in self.exam_categories:
                        if category in title.upper():
                            conducting_body = category
                            break
                    
                    return {
                        "exam_name": title,
                        "conducting_body": conducting_body,
                        "exam_date": exam_date,
                        "application_start": application_start,
                        "application_end": application_end,
                        "official_link": url,
                        "source_url": self.base_url
                    }
                    
                except ValueError:
                    self.logger.error(f"Error parsing date from {url}")
            
        except Exception as e:
            self.logger.error(f"Error extracting info from page {url}: {str(e)}")
        
        return None 