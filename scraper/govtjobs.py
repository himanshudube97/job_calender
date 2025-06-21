from .base import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
import re
import logging

class GovtJobsScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.govtjobs.in")
        self.logger = logging.getLogger(__name__)
        
        # Exam-related keywords
        self.exam_keywords = [
            'UPSC', 'SSC', 'IBPS', 'SBI', 'RRB', 'RAILWAY', 'BANK', 'POLICE',
            'EXAM', 'RECRUITMENT', 'NOTIFICATION', 'VACANCY', 'ADMIT CARD',
            'RESULT', 'CGL', 'CHSL', 'MTS', 'PO', 'CLERK', 'JE', 'NDA', 'CDS'
        ]

    def parse_date(self, date_text: str) -> datetime:
        """Parse date from text"""
        if not date_text:
            return None
            
        # Common date patterns
        patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})',  # DD Month YYYY
            r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})',  # Month DD, YYYY
        ]
        
        month_names = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
            'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
            'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
            'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
            'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        
        for pattern in patterns:
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    if groups[0].isdigit() and groups[2].isdigit():  # DD/MM/YYYY
                        day, month, year = groups
                        if groups[1].isalpha():  # Month name
                            month_num = month_names.get(groups[1].lower())
                            if month_num:
                                return datetime(int(year), month_num, int(day))
                        else:  # Month number
                            return datetime(int(year), int(month), int(day))
                    elif groups[0].isalpha():  # Month DD, YYYY
                        month, day, year = groups
                        month_num = month_names.get(month.lower())
                        if month_num:
                            return datetime(int(year), month_num, int(day))
                except (ValueError, TypeError):
                    continue
        return None

    def get_conducting_body(self, text: str) -> str:
        """Determine conducting body from text"""
        text_upper = text.upper()
        
        if 'UPSC' in text_upper or 'CIVIL SERVICE' in text_upper:
            return 'UPSC'
        elif 'SSC' in text_upper:
            return 'SSC'
        elif 'IBPS' in text_upper:
            return 'IBPS'
        elif 'SBI' in text_upper:
            return 'SBI'
        elif 'RRB' in text_upper or 'RAILWAY' in text_upper:
            return 'RAILWAY'
        elif 'POLICE' in text_upper:
            return 'POLICE'
        elif 'BANK' in text_upper:
            return 'BANKING'
        elif 'TEACHER' in text_upper or 'CTET' in text_upper:
            return 'TEACHING'
        elif 'DEFENCE' in text_upper or 'ARMY' in text_upper:
            return 'DEFENCE'
        elif 'MEDICAL' in text_upper or 'NEET' in text_upper:
            return 'MEDICAL'
        elif 'ENGINEERING' in text_upper or 'GATE' in text_upper:
            return 'ENGINEERING'
        else:
            return 'OTHER'

    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape government job notifications"""
        self.logger.info("Starting GovtJobs scraper")
        exams = []
        
        # URLs to scrape
        urls = [
            f"{self.base_url}/government-jobs",
            f"{self.base_url}/latest-government-jobs",
            f"{self.base_url}/admit-card",
            f"{self.base_url}/results"
        ]
        
        for url in urls:
            try:
                self.logger.info(f"Scraping: {url}")
                soup = self.get_soup(url)
                
                # Find job links
                links = soup.find_all('a', href=True)
                
                for link in links:
                    try:
                        title = self.clean_text(link.get_text())
                        href = link.get('href', '')
                        
                        # Filter relevant notifications
                        if len(title) < 10 or not any(keyword in title.upper() for keyword in self.exam_keywords):
                            continue
                        
                        # Build full URL
                        if href.startswith('http'):
                            full_url = href
                        elif href.startswith('/'):
                            full_url = self.base_url + href
                        else:
                            continue
                        
                        self.logger.info(f"Processing: {title[:50]}...")
                        
                        # Get detailed information
                        try:
                            detail_soup = self.get_soup(full_url)
                            content = detail_soup.get_text()
                            
                            # Extract dates
                            exam_date = None
                            application_start = None
                            application_end = None
                            
                            # Look for exam date
                            exam_patterns = [
                                r'[Ee]xam\s+[Dd]ate[:\s-]*([^\n.]+)',
                                r'[Tt]est\s+[Dd]ate[:\s-]*([^\n.]+)',
                                r'[Ee]xamination\s+[Dd]ate[:\s-]*([^\n.]+)'
                            ]
                            
                            for pattern in exam_patterns:
                                match = re.search(pattern, content)
                                if match:
                                    exam_date = self.parse_date(match.group(1))
                                    if exam_date:
                                        break
                            
                            # Look for application dates
                            start_patterns = [
                                r'[Aa]pplication\s+[Ss]tart[:\s-]*([^\n.]+)',
                                r'[Oo]nline\s+[Aa]pplication[:\s-]*([^\n.]+)',
                                r'[Rr]egistration\s+[Ss]tart[:\s-]*([^\n.]+)'
                            ]
                            
                            end_patterns = [
                                r'[Aa]pplication\s+[Ee]nd[:\s-]*([^\n.]+)',
                                r'[Ll]ast\s+[Dd]ate[:\s-]*([^\n.]+)',
                                r'[Dd]eadline[:\s-]*([^\n.]+)'
                            ]
                            
                            for pattern in start_patterns:
                                match = re.search(pattern, content)
                                if match:
                                    application_start = self.parse_date(match.group(1))
                                    if application_start:
                                        break
                            
                            for pattern in end_patterns:
                                match = re.search(pattern, content)
                                if match:
                                    application_end = self.parse_date(match.group(1))
                                    if application_end:
                                        break
                            
                            # Add exam if we have useful information
                            if exam_date or application_start or application_end:
                                conducting_body = self.get_conducting_body(title)
                                
                                exam_data = {
                                    "exam_name": title,
                                    "conducting_body": conducting_body,
                                    "exam_date": exam_date,
                                    "application_start": application_start,
                                    "application_end": application_end,
                                    "official_link": full_url,
                                    "source_url": url
                                }
                                
                                exams.append(exam_data)
                                self.logger.info(f"Added: {title}")
                                
                        except Exception as e:
                            self.logger.error(f"Error processing {full_url}: {str(e)}")
                            continue
                            
                    except Exception as e:
                        self.logger.error(f"Error processing link: {str(e)}")
                        continue
                        
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {str(e)}")
                continue
        
        self.logger.info(f"GovtJobs scraper completed, found {len(exams)} exams")
        return exams 