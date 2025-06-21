from .base import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
import re
import logging

class JobAlertScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://jobalert.gov.in")
        self.logger = logging.getLogger(__name__)

    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape exam notifications from JobAlert"""
        self.logger.info("Starting JobAlert scraper")
        exams = []
        
        try:
            # Scrape from different sections
            sections = [
                "/govt-jobs",
                "/latest-jobs", 
                "/exam-calendar",
                "/notifications"
            ]
            
            for section in sections:
                try:
                    section_exams = self.scrape_section(section)
                    exams.extend(section_exams)
                    self.logger.info(f"Found {len(section_exams)} exams in section {section}")
                except Exception as e:
                    self.logger.error(f"Error scraping section {section}: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping JobAlert: {str(e)}")
        
        self.logger.info(f"Completed JobAlert scraper, found {len(exams)} exams")
        return exams
    
    def scrape_section(self, section: str) -> List[Dict[str, Any]]:
        """Scrape a specific section of the website"""
        exams = []
        try:
            url = f"{self.base_url}{section}"
            soup = self.get_soup(url)
            
            # Look for job/exam cards or listings
            job_containers = soup.find_all(['div', 'article', 'li'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['job', 'exam', 'notification', 'vacancy', 'post']
            ))
            
            for container in job_containers:
                try:
                    # Extract title
                    title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'a'])
                    if not title_elem:
                        continue
                    
                    title = self.clean_text(title_elem.get_text())
                    if not self.is_valid_exam_title(title):
                        continue
                    
                    # Extract link
                    link_elem = title_elem if title_elem.name == 'a' else container.find('a', href=True)
                    link = None
                    if link_elem:
                        href = link_elem.get('href', '')
                        if href:
                            link = href if href.startswith('http') else f"{self.base_url}{href}"
                    
                    # Extract dates from container text
                    container_text = container.get_text()
                    exam_info = self.extract_dates_from_text(container_text, title, link or url)
                    
                    if exam_info:
                        exams.append(exam_info)
                        self.logger.info(f"Successfully added exam: {exam_info['exam_name']}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing container: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping section {section}: {str(e)}")
        
        return exams
    
    def extract_dates_from_text(self, text: str, title: str, link: str) -> Dict[str, Any]:
        """Extract exam information and dates from text"""
        try:
            # Look for various date patterns
            date_patterns = [
                r'exam\s+date[:\s]*(\d{1,2})[-/.]\s*(\d{1,2})[-/.]\s*(\d{4})',
                r'date[:\s]*(\d{1,2})[-/.]\s*(\d{1,2})[-/.]\s*(\d{4})',
                r'(\d{1,2})[-/.]\s*(\d{1,2})[-/.]\s*(\d{4})',
                r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{4})',
                r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})'
            ]
            
            exam_date = None
            application_start = None
            application_end = None
            
            text_lower = text.lower()
            
            # Try to find exam date
            for pattern in date_patterns:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    try:
                        if len(match.groups()) == 3:
                            if match.group(2).isalpha():  # Month name format
                                month_map = {
                                    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                                    'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                                    'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
                                    'january': '01', 'february': '02', 'march': '03', 'april': '04',
                                    'may': '05', 'june': '06', 'july': '07', 'august': '08',
                                    'september': '09', 'october': '10', 'november': '11', 'december': '12'
                                }
                                day = match.group(1).zfill(2)
                                month = month_map.get(match.group(2)[:3].lower(), '01')
                                year = match.group(3)
                                date_str = f"{day}-{month}-{year}"
                            else:  # Numeric format
                                day, month, year = match.groups()
                                date_str = f"{day.zfill(2)}-{month.zfill(2)}-{year}"
                            
                            parsed_date = datetime.strptime(date_str, "%d-%m-%Y")
                            
                            # Determine if it's exam date or application date based on context
                            context_before = text_lower[max(0, match.start()-50):match.start()]
                            context_after = text_lower[match.end():match.end()+50]
                            context = context_before + context_after
                            
                            if any(keyword in context for keyword in ['exam', 'test', 'written']):
                                if not exam_date:
                                    exam_date = parsed_date
                            elif any(keyword in context for keyword in ['application', 'apply', 'last date']):
                                if not application_end:
                                    application_end = parsed_date
                            elif not exam_date:
                                exam_date = parsed_date
                                
                    except (ValueError, AttributeError):
                        continue
            
            # If we found at least an exam date, create the exam info
            if exam_date:
                return {
                    "exam_name": title,
                    "conducting_body": self.get_conducting_body(title),
                    "exam_date": exam_date,
                    "application_start": application_start,
                    "application_end": application_end,
                    "official_link": link,
                    "source_url": self.base_url
                }
                
        except Exception as e:
            self.logger.error(f"Error extracting dates from text: {str(e)}")
        
        return None
    
    def is_valid_exam_title(self, title: str) -> bool:
        """Check if title is a valid exam notification"""
        if len(title) < 10 or len(title) > 200:
            return False
        
        exam_keywords = [
            'recruitment', 'notification', 'exam', 'vacancy', 'post',
            'selection', 'test', 'interview', 'application', 'form',
            'upsc', 'ssc', 'ibps', 'sbi', 'railway', 'rrb', 'bank',
            'police', 'defence', 'teaching', 'clerk', 'officer',
            'admit card', 'result', 'answer key', 'syllabus'
        ]
        
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in exam_keywords)
    
    def get_conducting_body(self, exam_name: str) -> str:
        """Determine conducting body from exam name"""
        exam_name_upper = exam_name.upper()
        
        if 'UPSC' in exam_name_upper:
            return 'UPSC'
        elif 'SSC' in exam_name_upper:
            return 'SSC'
        elif 'IBPS' in exam_name_upper:
            return 'IBPS'
        elif 'SBI' in exam_name_upper:
            return 'SBI'
        elif any(keyword in exam_name_upper for keyword in ['RAILWAY', 'RRB', 'RAIL']):
            return 'RAILWAY'
        elif 'POLICE' in exam_name_upper:
            return 'POLICE'
        elif any(keyword in exam_name_upper for keyword in ['DEFENCE', 'ARMY', 'NAVY', 'AIR FORCE']):
            return 'DEFENCE'
        elif any(keyword in exam_name_upper for keyword in ['TEACHING', 'TEACHER', 'EDUCATION']):
            return 'TEACHING'
        elif any(keyword in exam_name_upper for keyword in ['BANK', 'BANKING']):
            return 'BANKING'
        else:
            return 'OTHER' 