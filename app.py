from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import Session as DBSession, Exam

# Initialize FastAPI app
app = FastAPI(title="Government Exam Calendar")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Pydantic models for data validation
class ExamBase(BaseModel):
    exam_name: str
    conducting_body: str
    exam_date: datetime
    application_start: Optional[datetime] = None
    application_end: Optional[datetime] = None
    official_link: Optional[str] = None
    source_url: Optional[str] = None

    class Config:
        from_attributes = True

# Database session dependency
def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(
    request: Request,
    db: Session = Depends(get_db),
    conducting_body: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None
):
    """Render the main calendar page"""
    try:
        # Get current month and year if not specified
        now = datetime.now()
        current_month = month or now.month
        current_year = year or now.year

        # Build date range for the selected month
        start_date = datetime(current_year, current_month, 1)
        if current_month == 12:
            end_date = datetime(current_year + 1, 1, 1)
        else:
            end_date = datetime(current_year, current_month + 1, 1)

        # Query exams for the selected month and upcoming exams
        month_query = db.query(Exam).filter(
            Exam.exam_date >= start_date,
            Exam.exam_date < end_date
        )

        # Get upcoming exams (next 3 months)
        upcoming_end_date = now + timedelta(days=90)
        upcoming_query = db.query(Exam).filter(
            Exam.exam_date >= now,
            Exam.exam_date <= upcoming_end_date
        ).order_by(Exam.exam_date)

        # Apply conducting body filter if specified
        if conducting_body:
            month_query = month_query.filter(Exam.conducting_body == conducting_body)
            upcoming_query = upcoming_query.filter(Exam.conducting_body == conducting_body)

        month_exams = month_query.all()
        upcoming_exams = upcoming_query.limit(20).all()  # Limit to 20 upcoming exams

        # Get list of conducting bodies for the filter dropdown
        conducting_bodies = [body[0] for body in db.query(Exam.conducting_body).distinct().all()]
        conducting_bodies.sort()

        # Get exam statistics
        total_exams = db.query(Exam).count()
        total_upcoming = db.query(Exam).filter(Exam.exam_date >= now).count()

        # Get recent exams (for display)
        recent_exams = db.query(Exam).order_by(Exam.created_at.desc()).limit(10).all()

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "exams": upcoming_exams,  # Use upcoming exams for the table
                "month_exams": month_exams,  # Exams for current month
                "conducting_bodies": conducting_bodies,
                "selected_body": conducting_body,
                "current_month": current_month,
                "current_year": current_year,
                "total_exams": total_exams,
                "upcoming_exams": total_upcoming,
                "recent_exams": recent_exams
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/exams/month/{year}/{month}")
async def get_month_exams(
    year: int,
    month: int,
    conducting_body: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get exams for a specific month (AJAX endpoint for calendar updates)"""
    try:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        query = db.query(Exam).filter(
            Exam.exam_date >= start_date,
            Exam.exam_date < end_date
        )

        if conducting_body:
            query = query.filter(Exam.conducting_body == conducting_body)

        exams = query.all()
        return [
            {
                "id": exam.id,
                "name": exam.exam_name,
                "date": exam.exam_date.strftime("%Y-%m-%d"),
                "body": exam.conducting_body,
                "link": exam.official_link,
                "app_start": exam.application_start.strftime("%Y-%m-%d") if exam.application_start else None,
                "app_end": exam.application_end.strftime("%Y-%m-%d") if exam.application_end else None,
                "app_start_formatted": exam.application_start.strftime("%d %b %Y") if exam.application_start else "Not Available",
                "app_end_formatted": exam.application_end.strftime("%d %b %Y") if exam.application_end else "Not Available",
                "exam_date_formatted": exam.exam_date.strftime("%d %b %Y") if exam.exam_date else "TBA"
            }
            for exam in exams
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/exams/search")
async def search_exams(
    q: Optional[str] = None,
    conducting_body: Optional[str] = None,
    days: Optional[int] = 90,
    db: Session = Depends(get_db)
):
    """Search exams with filters"""
    try:
        query = db.query(Exam)
        
        # Apply date filter
        if days:
            end_date = datetime.now() + timedelta(days=days)
            query = query.filter(
                Exam.exam_date >= datetime.now(),
                Exam.exam_date <= end_date
            )
        
        # Apply conducting body filter
        if conducting_body:
            query = query.filter(Exam.conducting_body == conducting_body)
        
        # Apply text search
        if q:
            query = query.filter(Exam.exam_name.contains(q))
        
        exams = query.order_by(Exam.exam_date).all()
        
        return [
            {
                "id": exam.id,
                "name": exam.exam_name,
                "date": exam.exam_date.strftime("%Y-%m-%d"),
                "body": exam.conducting_body,
                "link": exam.official_link,
                "app_start": exam.application_start.strftime("%Y-%m-%d") if exam.application_start else None,
                "app_end": exam.application_end.strftime("%Y-%m-%d") if exam.application_end else None
            }
            for exam in exams
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get exam statistics"""
    try:
        now = datetime.now()
        
        total_exams = db.query(Exam).count()
        upcoming_exams = db.query(Exam).filter(Exam.exam_date >= now).count()
        this_month_exams = db.query(Exam).filter(
            Exam.exam_date >= datetime(now.year, now.month, 1),
            Exam.exam_date < datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
        ).count()
        
        # Get conducting body stats
        body_stats = {}
        for body in db.query(Exam.conducting_body).distinct().all():
            count = db.query(Exam).filter(
                Exam.conducting_body == body[0],
                Exam.exam_date >= now
            ).count()
            body_stats[body[0]] = count
        
        return {
            "total_exams": total_exams,
            "upcoming_exams": upcoming_exams,
            "this_month_exams": this_month_exams,
            "body_stats": body_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/debug/all-exams")
async def get_all_exams(db: Session = Depends(get_db)):
    """Debug endpoint to see all exams in the database"""
    try:
        exams = db.query(Exam).order_by(Exam.exam_date).all()
        return [
            {
                "id": exam.id,
                "name": exam.exam_name,
                "date": exam.exam_date.strftime("%Y-%m-%d"),
                "body": exam.conducting_body,
                "link": exam.official_link
            }
            for exam in exams
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 