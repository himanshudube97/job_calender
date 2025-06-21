from .base import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
import re
import logging

class JagranJoshScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.jagranjosh.com")
        self.logger = logging.getLogger(__name__)

    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape exam notifications from Jagran Josh"""
        self.logger.info("Starting Jagran Josh scraper")
        exams = []
        
        try:
            # Scrape from different sections
            sections = [
                "/jobs",
                "/government-jobs",
                "/current-affairs/exam-calendar",
                "/latest-govt-jobs"
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
            self.logger.error(f"Error scraping Jagran Josh: {str(e)}")
        
        self.logger.info(f"Completed Jagran Josh scraper, found {len(exams)} exams")
        return exams
    
    def scrape_section(self, section: str) -> List[Dict[str, Any]]:
        """Scrape a specific section of the website"""
        exams = []
        try:
            url = f"{self.base_url}{section}"
            soup = self.get_soup(url)
            
            # Look for article containers or job listings
            containers = soup.find_all(['article', 'div'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['article', 'job', 'news', 'content', 'item']
            ))
            
            # Also look for direct links
            if not containers:
                containers = soup.find_all('a', href=True)
            
            for container in containers:
                try:
                    # Extract title
                    if container.name == 'a':
                        title = self.clean_text(container.get_text())
                        link = container.get('href', '')
                    else:
                        title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'a'])
                        if not title_elem:
                            continue
                        title = self.clean_text(title_elem.get_text())
                        
                        # Extract link
                        link_elem = title_elem if title_elem.name == 'a' else container.find('a', href=True)
                        link = link_elem.get('href', '') if link_elem else ''
                    
                    if not self.is_valid_exam_title(title):
                        continue
                    
                    # Make link absolute
                    if link and not link.startswith('http'):
                        link = f"{self.base_url}{link}" if link.startswith('/') else f"{self.base_url}/{link}"
                    
                    # Try to extract more details if we have a link
                    exam_info = None
                    if link:
                        exam_info = self.extract_exam_details_from_page(link, title)
                    
                    # If we couldn't get details from page, extract from container text
                    if not exam_info:
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
    
    def extract_exam_details_from_page(self, url: str, title: str) -> Dict[str, Any]:
        """Extract detailed exam information from individual page"""
        try:
            soup = self.get_soup(url)
            content = soup.get_text()
            
            # Look for exam dates in the content
            exam_info = self.extract_dates_from_text(content, title, url)
            return exam_info
            
        except Exception as e:
            self.logger.error(f"Error extracting details from page {url}: {str(e)}")
        
        return None
    
    def extract_dates_from_text(self, text: str, title: str, link: str) -> Dict[str, Any]:
        """Extract exam information and dates from text"""
        try:
            # Enhanced date patterns
            date_patterns = [
                r'exam\s+date[:\s]*(\d{1,2})[-/.]\s*(\d{1,2})[-/.]\s*(\d{4})',
                r'written\s+exam[:\s]*(\d{1,2})[-/.]\s*(\d{1,2})[-/.]\s*(\d{4})',
                r'test\s+date[:\s]*(\d{1,2})[-/.]\s*(\d{1,2})[-/.]\s*(\d{4})',
                r'exam\s+on[:\s]*(\d{1,2})[-/.]\s*(\d{1,2})[-/.]\s*(\d{4})',
                r'(\d{1,2})[-/.]\s*(\d{1,2})[-/.]\s*(\d{4})',
                r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})',
                r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})'
            ]
            
            exam_date = None
            application_start = None
            application_end = None
            
            text_lower = text.lower()
            
            # Try to find dates
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
                                month_key = match.group(2)[:3].lower()
                                month = month_map.get(month_key, '01')
                                year = match.group(3)
                                date_str = f"{day}-{month}-{year}"
                            else:  # Numeric format
                                day, month, year = match.groups()
                                date_str = f"{day.zfill(2)}-{month.zfill(2)}-{year}"
                            
                            parsed_date = datetime.strptime(date_str, "%d-%m-%Y")
                            
                            # Skip dates that are too far in the past
                            if parsed_date.year < 2024:
                                continue
                            
                            # Determine type of date based on context
                            context_before = text_lower[max(0, match.start()-100):match.start()]
                            context_after = text_lower[match.end():match.end()+100]
                            context = context_before + context_after
                            
                            if any(keyword in context for keyword in ['exam', 'test', 'written', 'mains', 'prelims']):
                                if not exam_date:
                                    exam_date = parsed_date
                            elif any(keyword in context for keyword in ['application', 'apply', 'last date', 'deadline']):
                                if 'start' in context or 'begin' in context:
                                    if not application_start:
                                        application_start = parsed_date
                                else:
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
        if len(title) < 15 or len(title) > 300:
            return False
        
        # Skip common non-exam content
        skip_keywords = [
            'advertisement', 'contact us', 'about us', 'privacy policy',
            'terms', 'disclaimer', 'home', 'login', 'register'
        ]
        
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in skip_keywords):
            return False
        
        exam_keywords = [
            'recruitment', 'notification', 'exam', 'vacancy', 'post',
            'selection', 'test', 'interview', 'application', 'form',
            'upsc', 'ssc', 'ibps', 'sbi', 'railway', 'rrb', 'bank',
            'police', 'defence', 'teaching', 'clerk', 'officer',
            'admit card', 'result', 'answer key', 'syllabus',
            'government job', 'govt job', 'bharti', 'naukri'
        ]
        
        return any(keyword in title_lower for keyword in exam_keywords)
    
    def get_conducting_body(self, exam_name: str) -> str:
        """Determine conducting body from exam name"""
        exam_name_upper = exam_name.upper()
        
        conducting_bodies = {
            'UPSC': ['UPSC', 'UNION PUBLIC SERVICE COMMISSION'],
            'SSC': ['SSC', 'STAFF SELECTION COMMISSION'],
            'IBPS': ['IBPS', 'INSTITUTE OF BANKING PERSONNEL SELECTION'],
            'SBI': ['SBI', 'STATE BANK OF INDIA'],
            'RAILWAY': ['RAILWAY', 'RRB', 'RAIL', 'INDIAN RAILWAY'],
            'POLICE': ['POLICE', 'CONSTABLE', 'SI ', 'SUB INSPECTOR'],
            'DEFENCE': ['DEFENCE', 'ARMY', 'NAVY', 'AIR FORCE', 'MILITARY', 'SOLDIER'],
            'TEACHING': ['TEACHING', 'TEACHER', 'EDUCATION', 'SCHOOL', 'TET', 'B.ED'],
            'BANKING': ['BANK', 'BANKING', 'CLERK', 'PO ', 'PROBATIONARY OFFICER'],
            'MEDICAL': ['MEDICAL', 'DOCTOR', 'NURSE', 'AIIMS', 'NEET'],
            'ENGINEERING': ['ENGINEERING', 'ENGINEER', 'JEE', 'GATE', 'TECHNICAL']
        }
        
        for body, keywords in conducting_bodies.items():
            if any(keyword in exam_name_upper for keyword in keywords):
                return body
        
        return 'OTHER' 