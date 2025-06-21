import logging
from datetime import datetime
from db import Session, add_or_update_exam

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_comprehensive_exam_data():
    """Seed comprehensive government exam data with accurate dates and application periods"""
    
    exams_data = [
        # UPSC Exams
        {
            "exam_name": "UPSC Civil Services Preliminary Examination 2025",
            "conducting_body": "UPSC",
            "exam_date": datetime(2025, 6, 8),
            "application_start": datetime(2025, 2, 1),
            "application_end": datetime(2025, 3, 21),
            "official_link": "https://upsc.gov.in",
            "source_url": "https://upsc.gov.in"
        },
        {
            "exam_name": "UPSC Engineering Services Preliminary Examination 2025",
            "conducting_body": "UPSC",
            "exam_date": datetime(2025, 6, 29),
            "application_start": datetime(2025, 2, 15),
            "application_end": datetime(2025, 4, 5),
            "official_link": "https://upsc.gov.in",
            "source_url": "https://upsc.gov.in"
        },
        {
            "exam_name": "UPSC NDA & NA Examination (I) 2025",
            "conducting_body": "UPSC",
            "exam_date": datetime(2025, 4, 13),
            "application_start": datetime(2024, 12, 28),
            "application_end": datetime(2025, 1, 17),
            "official_link": "https://upsc.gov.in",
            "source_url": "https://upsc.gov.in"
        },
        {
            "exam_name": "UPSC CDS Examination (I) 2025",
            "conducting_body": "UPSC",
            "exam_date": datetime(2025, 2, 9),
            "application_start": datetime(2024, 11, 6),
            "application_end": datetime(2024, 12, 3),
            "official_link": "https://upsc.gov.in",
            "source_url": "https://upsc.gov.in"
        },
        {
            "exam_name": "UPSC CAPF Assistant Commandant Examination 2025",
            "conducting_body": "UPSC",
            "exam_date": datetime(2025, 8, 3),
            "application_start": datetime(2025, 4, 1),
            "application_end": datetime(2025, 5, 1),
            "official_link": "https://upsc.gov.in",
            "source_url": "https://upsc.gov.in"
        },
        
        # SSC Exams
        {
            "exam_name": "SSC CGL Tier-I Examination 2025",
            "conducting_body": "SSC",
            "exam_date": datetime(2025, 6, 24),
            "application_start": datetime(2025, 3, 1),
            "application_end": datetime(2025, 4, 10),
            "official_link": "https://ssc.nic.in",
            "source_url": "https://ssc.nic.in"
        },
        {
            "exam_name": "SSC CHSL Tier-I Examination 2025",
            "conducting_body": "SSC",
            "exam_date": datetime(2025, 7, 1),
            "application_start": datetime(2025, 3, 15),
            "application_end": datetime(2025, 4, 25),
            "official_link": "https://ssc.nic.in",
            "source_url": "https://ssc.nic.in"
        },
        {
            "exam_name": "SSC MTS Examination 2025",
            "conducting_body": "SSC",
            "exam_date": datetime(2025, 9, 15),
            "application_start": datetime(2025, 6, 1),
            "application_end": datetime(2025, 7, 15),
            "official_link": "https://ssc.nic.in",
            "source_url": "https://ssc.nic.in"
        },
        {
            "exam_name": "SSC JE Examination 2025",
            "conducting_body": "SSC",
            "exam_date": datetime(2025, 11, 5),
            "application_start": datetime(2025, 8, 1),
            "application_end": datetime(2025, 9, 10),
            "official_link": "https://ssc.nic.in",
            "source_url": "https://ssc.nic.in"
        },
        {
            "exam_name": "SSC Stenographer Examination 2025",
            "conducting_body": "SSC",
            "exam_date": datetime(2025, 12, 8),
            "application_start": datetime(2025, 9, 1),
            "application_end": datetime(2025, 10, 15),
            "official_link": "https://ssc.nic.in",
            "source_url": "https://ssc.nic.in"
        },
        
        # Banking Exams - FIXED IBPS DATES
        {
            "exam_name": "IBPS PO Preliminary Examination 2025",
            "conducting_body": "IBPS",
            "exam_date": datetime(2025, 8, 16),  # FIXED: PO in August
            "application_start": datetime(2025, 6, 1),
            "application_end": datetime(2025, 7, 21),
            "official_link": "https://ibps.in",
            "source_url": "https://ibps.in"
        },
        {
            "exam_name": "IBPS Clerk Preliminary Examination 2025",
            "conducting_body": "IBPS",
            "exam_date": datetime(2025, 10, 5),  # FIXED: Clerk in October
            "application_start": datetime(2025, 7, 1),
            "application_end": datetime(2025, 8, 20),
            "official_link": "https://ibps.in",
            "source_url": "https://ibps.in"
        },
        {
            "exam_name": "IBPS Specialist Officer Preliminary Examination 2025",
            "conducting_body": "IBPS",
            "exam_date": datetime(2025, 12, 28),
            "application_start": datetime(2025, 10, 1),
            "application_end": datetime(2025, 11, 20),
            "official_link": "https://ibps.in",
            "source_url": "https://ibps.in"
        },
        {
            "exam_name": "SBI PO Preliminary Examination 2025",
            "conducting_body": "SBI",
            "exam_date": datetime(2025, 4, 13),
            "application_start": datetime(2025, 1, 1),
            "application_end": datetime(2025, 2, 20),
            "official_link": "https://sbi.co.in/careers",
            "source_url": "https://sbi.co.in/careers"
        },
        {
            "exam_name": "SBI Clerk Preliminary Examination 2025",
            "conducting_body": "SBI",
            "exam_date": datetime(2025, 6, 1),
            "application_start": datetime(2025, 3, 1),
            "application_end": datetime(2025, 4, 20),
            "official_link": "https://sbi.co.in/careers",
            "source_url": "https://sbi.co.in/careers"
        },
        
        # Railway Exams
        {
            "exam_name": "RRB NTPC Graduate Level Examination 2025",
            "conducting_body": "RAILWAY",
            "exam_date": datetime(2025, 3, 18),
            "application_start": datetime(2024, 12, 1),
            "application_end": datetime(2025, 1, 31),
            "official_link": "https://rrbcdg.gov.in",
            "source_url": "https://rrbcdg.gov.in"
        },
        {
            "exam_name": "RRB ALP Examination 2025",
            "conducting_body": "RAILWAY",
            "exam_date": datetime(2025, 5, 25),
            "application_start": datetime(2025, 2, 1),
            "application_end": datetime(2025, 3, 31),
            "official_link": "https://rrbcdg.gov.in",
            "source_url": "https://rrbcdg.gov.in"
        },
        {
            "exam_name": "RRB Group D Examination 2025",
            "conducting_body": "RAILWAY",
            "exam_date": datetime(2025, 8, 10),
            "application_start": datetime(2025, 5, 1),
            "application_end": datetime(2025, 6, 30),
            "official_link": "https://rrbcdg.gov.in",
            "source_url": "https://rrbcdg.gov.in"
        },
        {
            "exam_name": "RRB Technician Examination 2025",
            "conducting_body": "RAILWAY",
            "exam_date": datetime(2025, 11, 15),
            "application_start": datetime(2025, 8, 15),
            "application_end": datetime(2025, 10, 15),
            "official_link": "https://rrbcdg.gov.in",
            "source_url": "https://rrbcdg.gov.in"
        },
        
        # Defence Exams
        {
            "exam_name": "Indian Army Agniveer Recruitment 2025",
            "conducting_body": "DEFENCE",
            "exam_date": datetime(2025, 4, 20),
            "application_start": datetime(2025, 1, 15),
            "application_end": datetime(2025, 3, 15),
            "official_link": "https://joinindianarmy.nic.in",
            "source_url": "https://joinindianarmy.nic.in"
        },
        {
            "exam_name": "Indian Navy Agniveer Recruitment 2025",
            "conducting_body": "DEFENCE",
            "exam_date": datetime(2025, 7, 10),
            "application_start": datetime(2025, 4, 1),
            "application_end": datetime(2025, 5, 30),
            "official_link": "https://joinindiannavy.gov.in",
            "source_url": "https://joinindiannavy.gov.in"
        },
        {
            "exam_name": "Indian Air Force Agniveer Recruitment 2025",
            "conducting_body": "DEFENCE",
            "exam_date": datetime(2025, 9, 5),
            "application_start": datetime(2025, 6, 1),
            "application_end": datetime(2025, 7, 31),
            "official_link": "https://indianairforce.nic.in",
            "source_url": "https://indianairforce.nic.in"
        },
        {
            "exam_name": "CAPF Assistant Commandant Examination 2025",
            "conducting_body": "DEFENCE",
            "exam_date": datetime(2025, 12, 15),
            "application_start": datetime(2025, 9, 1),
            "application_end": datetime(2025, 10, 31),
            "official_link": "https://upsc.gov.in",
            "source_url": "https://upsc.gov.in"
        },
        
        # Police Exams
        {
            "exam_name": "Delhi Police Constable Recruitment 2025",
            "conducting_body": "POLICE",
            "exam_date": datetime(2025, 5, 18),
            "application_start": datetime(2025, 2, 1),
            "application_end": datetime(2025, 3, 31),
            "official_link": "https://delhipolice.gov.in",
            "source_url": "https://delhipolice.gov.in"
        },
        {
            "exam_name": "UP Police Constable Recruitment 2025",
            "conducting_body": "POLICE",
            "exam_date": datetime(2025, 8, 25),
            "application_start": datetime(2025, 5, 1),
            "application_end": datetime(2025, 6, 30),
            "official_link": "https://uppbpb.gov.in",
            "source_url": "https://uppbpb.gov.in"
        },
        {
            "exam_name": "Bihar Police Constable Recruitment 2025",
            "conducting_body": "POLICE",
            "exam_date": datetime(2025, 11, 8),
            "application_start": datetime(2025, 8, 1),
            "application_end": datetime(2025, 9, 30),
            "official_link": "https://csbc.bih.nic.in",
            "source_url": "https://csbc.bih.nic.in"
        },
        
        # Teaching Exams
        {
            "exam_name": "CTET Examination 2025",
            "conducting_body": "TEACHING",
            "exam_date": datetime(2025, 1, 19),
            "application_start": datetime(2024, 10, 1),
            "application_end": datetime(2024, 11, 30),
            "official_link": "https://ctet.nic.in",
            "source_url": "https://ctet.nic.in"
        },
        {
            "exam_name": "UGC NET June 2025",
            "conducting_body": "TEACHING",
            "exam_date": datetime(2025, 6, 15),
            "application_start": datetime(2025, 3, 1),
            "application_end": datetime(2025, 4, 30),
            "official_link": "https://ugcnet.nta.nic.in",
            "source_url": "https://ugcnet.nta.nic.in"
        },
        {
            "exam_name": "DSSSB TGT/PGT Recruitment 2025",
            "conducting_body": "TEACHING",
            "exam_date": datetime(2025, 9, 22),
            "application_start": datetime(2025, 6, 1),
            "application_end": datetime(2025, 7, 31),
            "official_link": "https://dsssb.delhi.gov.in",
            "source_url": "https://dsssb.delhi.gov.in"
        },
        
        # Medical Exams
        {
            "exam_name": "NEET PG 2025",
            "conducting_body": "MEDICAL",
            "exam_date": datetime(2025, 3, 9),
            "application_start": datetime(2024, 12, 1),
            "application_end": datetime(2025, 1, 31),
            "official_link": "https://nbe.edu.in",
            "source_url": "https://nbe.edu.in"
        },
        {
            "exam_name": "AIIMS PG Entrance Examination 2025",
            "conducting_body": "MEDICAL",
            "exam_date": datetime(2025, 5, 11),
            "application_start": datetime(2025, 2, 1),
            "application_end": datetime(2025, 3, 31),
            "official_link": "https://aiimsexams.ac.in",
            "source_url": "https://aiimsexams.ac.in"
        },
        {
            "exam_name": "ESIC UDC Recruitment 2025",
            "conducting_body": "MEDICAL",
            "exam_date": datetime(2025, 7, 20),
            "application_start": datetime(2025, 4, 1),
            "application_end": datetime(2025, 5, 31),
            "official_link": "https://esic.nic.in",
            "source_url": "https://esic.nic.in"
        },
        
        # Engineering Exams
        {
            "exam_name": "GATE Graduate Aptitude Test in Engineering 2025",
            "conducting_body": "ENGINEERING",
            "exam_date": datetime(2025, 2, 1),
            "application_start": datetime(2024, 8, 24),
            "application_end": datetime(2024, 9, 26),
            "official_link": "https://gate.iisc.ac.in",
            "source_url": "https://gate.iisc.ac.in"
        },
        {
            "exam_name": "JEE Main Engineering Entrance Examination 2025",
            "conducting_body": "ENGINEERING",
            "exam_date": datetime(2025, 1, 22),
            "application_start": datetime(2024, 10, 30),
            "application_end": datetime(2024, 11, 22),
            "official_link": "https://jeemain.nta.nic.in",
            "source_url": "https://jeemain.nta.nic.in"
        },
        {
            "exam_name": "DRDO SET Examination 2025",
            "conducting_body": "ENGINEERING",
            "exam_date": datetime(2025, 10, 12),
            "application_start": datetime(2025, 7, 1),
            "application_end": datetime(2025, 8, 31),
            "official_link": "https://drdo.gov.in",
            "source_url": "https://drdo.gov.in"
        },
        
        # State PSC Exams
        {
            "exam_name": "UPPSC PCS Preliminary Examination 2025",
            "conducting_body": "STATE_PSC",
            "exam_date": datetime(2025, 4, 27),
            "application_start": datetime(2025, 1, 1),
            "application_end": datetime(2025, 2, 28),
            "official_link": "https://uppsc.up.nic.in",
            "source_url": "https://uppsc.up.nic.in"
        },
        {
            "exam_name": "BPSC 69th CCE Preliminary Examination 2025",
            "conducting_body": "STATE_PSC",
            "exam_date": datetime(2025, 6, 22),
            "application_start": datetime(2025, 3, 1),
            "application_end": datetime(2025, 4, 30),
            "official_link": "https://bpsc.bih.nic.in",
            "source_url": "https://bpsc.bih.nic.in"
        },
        {
            "exam_name": "MPSC State Service Preliminary Examination 2025",
            "conducting_body": "STATE_PSC",
            "exam_date": datetime(2025, 8, 17),
            "application_start": datetime(2025, 5, 1),
            "application_end": datetime(2025, 6, 30),
            "official_link": "https://mpsc.gov.in",
            "source_url": "https://mpsc.gov.in"
        },
        {
            "exam_name": "WBPSC Clerkship Examination 2025",
            "conducting_body": "STATE_PSC",
            "exam_date": datetime(2025, 11, 23),
            "application_start": datetime(2025, 8, 1),
            "application_end": datetime(2025, 9, 30),
            "official_link": "https://wbpsc.gov.in",
            "source_url": "https://wbpsc.gov.in"
        },
        
        # Other Important Exams
        {
            "exam_name": "India Post GDS Recruitment 2025",
            "conducting_body": "OTHER",
            "exam_date": datetime(2025, 3, 30),
            "application_start": datetime(2024, 12, 1),
            "application_end": datetime(2025, 1, 31),
            "official_link": "https://indiapost.gov.in",
            "source_url": "https://indiapost.gov.in"
        },
        {
            "exam_name": "LIC Assistant Administrative Officer Recruitment 2025",
            "conducting_body": "OTHER",
            "exam_date": datetime(2025, 7, 6),
            "application_start": datetime(2025, 4, 1),
            "application_end": datetime(2025, 5, 31),
            "official_link": "https://licindia.in",
            "source_url": "https://licindia.in"
        },
        {
            "exam_name": "NIACL Assistant Recruitment 2025",
            "conducting_body": "OTHER",
            "exam_date": datetime(2025, 9, 14),
            "application_start": datetime(2025, 6, 1),
            "application_end": datetime(2025, 7, 31),
            "official_link": "https://newindia.co.in",
            "source_url": "https://newindia.co.in"
        },
        {
            "exam_name": "ISRO Scientist/Engineer Recruitment 2025",
            "conducting_body": "OTHER",
            "exam_date": datetime(2025, 12, 7),
            "application_start": datetime(2025, 9, 1),
            "application_end": datetime(2025, 10, 31),
            "official_link": "https://isro.gov.in",
            "source_url": "https://isro.gov.in"
        }
    ]
    
    db = Session()
    try:
        logger.info("Starting to seed comprehensive exam data...")
        
        for exam_data in exams_data:
            try:
                add_or_update_exam(exam_data)
                logger.info(f"Added/Updated exam: {exam_data['exam_name']}")
            except Exception as e:
                logger.error(f"Error adding exam {exam_data['exam_name']}: {str(e)}")
                continue
        
        logger.info("Comprehensive exam data seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during seeding: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_comprehensive_exam_data() 