import logging
from scraper.sarkari_result import SarkariResultScraper
from scraper.freshers_live import FreshersLiveScraper
from scraper.employment_news import EmploymentNewsScraper
from scraper.job_alert import JobAlertScraper
from scraper.jagran_josh import JagranJoshScraper
from scraper.ibps import IBPSScraper
from scraper.sbi import SBIScraper
from scraper.ssc import SSCScraper
from scraper.upsc import UPSCScraper
from scraper.freejobalert import FreeJobAlertScraper
from scraper.govtjobs import GovtJobsScraper
from db import add_or_update_exam

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_all_scrapers():
    """Run all available scrapers and collect exam data"""
    
    # Initialize all scrapers
    scrapers = [
        SarkariResultScraper(),
        FreeJobAlertScraper(),
        GovtJobsScraper(),
        FreshersLiveScraper(),
        EmploymentNewsScraper(),
        JobAlertScraper(),
        JagranJoshScraper(),
        IBPSScraper(),
        SBIScraper(),
        SSCScraper(),
        UPSCScraper(),
    ]
    
    total_exams_added = 0
    successful_scrapers = []
    failed_scrapers = []
    
    logger.info("Starting comprehensive exam data scraping...")
    
    for scraper in scrapers:
        scraper_name = scraper.__class__.__name__
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {scraper_name}")
        logger.info(f"{'='*50}")
        
        try:
            exams = scraper.scrape()
            
            if exams:
                logger.info(f"{scraper_name} found {len(exams)} exams")
                
                # Add exams to database
                added_count = 0
                for exam in exams:
                    try:
                        add_or_update_exam(exam)
                        added_count += 1
                        logger.info(f"Added/Updated: {exam['exam_name']}")
                    except Exception as e:
                        logger.error(f"Error adding exam to database: {str(e)}")
                        continue
                
                total_exams_added += added_count
                successful_scrapers.append((scraper_name, added_count))
                logger.info(f"{scraper_name} successfully added {added_count} exams to database")
                
            else:
                logger.warning(f"{scraper_name} found no exams")
                failed_scrapers.append((scraper_name, "No exams found"))
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"{scraper_name} failed with error: {error_msg}")
            failed_scrapers.append((scraper_name, error_msg))
            continue
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("SCRAPING SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total exams added to database: {total_exams_added}")
    logger.info(f"Successful scrapers: {len(successful_scrapers)}")
    logger.info(f"Failed scrapers: {len(failed_scrapers)}")
    
    if successful_scrapers:
        logger.info("\nSUCCESSFUL SCRAPERS:")
        for scraper_name, count in successful_scrapers:
            logger.info(f"  - {scraper_name}: {count} exams")
    
    if failed_scrapers:
        logger.info("\nFAILED SCRAPERS:")
        for scraper_name, error in failed_scrapers:
            logger.info(f"  - {scraper_name}: {error}")
    
    logger.info(f"\nDetailed logs available in scraper.log")
    logger.info(f"{'='*60}")
    
    return total_exams_added

if __name__ == "__main__":
    run_all_scrapers() 