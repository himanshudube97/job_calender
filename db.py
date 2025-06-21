from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Create the base class for declarative models
Base = declarative_base()

class Exam(Base):
    __tablename__ = 'exams'
    
    id = Column(Integer, primary_key=True)
    exam_name = Column(String, nullable=False)
    conducting_body = Column(String, nullable=False)
    exam_date = Column(DateTime, nullable=True)
    application_start = Column(DateTime, nullable=True)
    application_end = Column(DateTime, nullable=True)
    official_link = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

# Create database engine
engine = create_engine('sqlite:///exams.db')

# Create a session factory
Session = sessionmaker(bind=engine)

def init_db():
    """Initialize the database tables"""
    logger.info("Initializing database tables")
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def add_or_update_exam(exam_data):
    """Add a new exam or update existing one"""
    session = Session()
    try:
        # Check if exam already exists
        existing_exam = session.query(Exam).filter(
            Exam.exam_name == exam_data['exam_name'],
            Exam.conducting_body == exam_data['conducting_body'],
            Exam.exam_date == exam_data['exam_date']
        ).first()
        
        if existing_exam:
            # Update existing exam
            for key, value in exam_data.items():
                setattr(existing_exam, key, value)
            existing_exam.updated_at = datetime.now()
            logger.info(f"Updated exam: {exam_data['exam_name']}")
        else:
            # Add new exam
            new_exam = Exam(**exam_data)
            session.add(new_exam)
            logger.info(f"Added new exam: {exam_data['exam_name']}")
        
        session.commit()
        
    except Exception as e:
        logger.error(f"Error adding/updating exam {exam_data.get('exam_name', '')}: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

def get_all_exams():
    """Retrieve all exams from the database"""
    session = Session()
    try:
        exams = session.query(Exam).all()
        return exams
    except Exception as e:
        logger.error(f"Error retrieving exams: {str(e)}")
        raise
    finally:
        session.close()

def get_exams_by_conducting_body(conducting_body):
    """Retrieve exams for a specific conducting body"""
    session = Session()
    try:
        exams = session.query(Exam).filter(Exam.conducting_body == conducting_body).all()
        return exams
    except Exception as e:
        logger.error(f"Error retrieving exams for {conducting_body}: {str(e)}")
        raise
    finally:
        session.close()

def get_upcoming_exams(days=30):
    """Retrieve upcoming exams within specified days"""
    session = Session()
    try:
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() + timedelta(days=days)
        exams = session.query(Exam).filter(
            Exam.exam_date >= datetime.now(),
            Exam.exam_date <= cutoff_date
        ).all()
        return exams
    except Exception as e:
        logger.error(f"Error retrieving upcoming exams: {str(e)}")
        raise
    finally:
        session.close()

def delete_old_exams(days=90):
    """Delete exams older than specified days"""
    session = Session()
    try:
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        session.query(Exam).filter(Exam.exam_date < cutoff_date).delete()
        session.commit()
        logger.info(f"Deleted exams older than {days} days")
    except Exception as e:
        logger.error(f"Error deleting old exams: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close() 