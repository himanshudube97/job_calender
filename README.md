# 🎓 Government Exam Calendar

A comprehensive web application that aggregates Indian government exam information from multiple sources and presents them in an interactive calendar interface. This platform solves the problem of students having to visit multiple websites to track government exam dates and application deadlines.

## ✨ Features

### 📅 Interactive Calendar
- **Monthly calendar view** with color-coded exam events
- **Event filtering** by conducting body (UPSC, SSC, IBPS, etc.)
- **Detailed exam modals** with application dates and official links
- **Application status indicators** (Open/Closed/Coming Soon)
- **Responsive design** for desktop and mobile

### 🔍 Data Sources
The application scrapes exam data from multiple official sources:
- **SarkariResult.com** ✅ (Working - 12+ exams)
- **FreeJobAlert** (Enhanced scraper)
- **GovtJobs** (Enhanced scraper)
- **FreshersLive** (Website access issues)
- **EmploymentNews** (Website access issues)
- **JagranJosh** (Website access issues)
- And more specialized scrapers for UPSC, SSC, IBPS, SBI

### 🏛️ Exam Categories Covered
- **UPSC**: Civil Services, Engineering Services, NDA, CDS, CAPF
- **SSC**: CGL, CHSL, MTS, JE, Stenographer
- **Banking**: IBPS PO/Clerk/SO, SBI PO/Clerk
- **Railway**: RRB NTPC, ALP, Group D, Technician
- **Defence**: Army/Navy/Air Force Agniveer, CAPF
- **Police**: State-wise police recruitments
- **Teaching**: CTET, UGC NET, DSSSB
- **Medical**: NEET PG, AIIMS, ESIC
- **Engineering**: GATE, JEE Main, DRDO SET
- **State PSC**: UPPSC, BPSC, MPSC, WBPSC
- **Others**: India Post, LIC, Insurance exams

### 🚀 Technical Features
- **RESTful API** built with FastAPI
- **SQLite database** with comprehensive exam data
- **Web scraping** with error handling and retry logic
- **Seed data** with 80+ realistic government exams
- **Real-time filtering** and search capabilities
- **Application deadline tracking**

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd calender
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Initialize the database:**
```bash
python seed_data.py
```

5. **Start the application:**
```bash
uvicorn app:app --reload
```

6. **Access the application:**
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Debug**: http://localhost:8000/api/debug/all-exams

## 🏗️ Project Structure

```
calender/
├── 📁 scraper/                 # Web scraping modules
│   ├── base.py                 # Base scraper class
│   ├── sarkari_result.py       # Working scraper ✅
│   ├── freejobalert.py         # Enhanced scraper
│   ├── govtjobs.py             # Enhanced scraper
│   ├── employment_news.py      # Scraper (issues)
│   ├── freshers_live.py        # Scraper (issues)
│   ├── job_alert.py            # Scraper (issues)
│   ├── jagran_josh.py          # Scraper (issues)
│   ├── upsc.py                 # UPSC specific scraper
│   ├── ssc.py                  # SSC specific scraper
│   ├── ibps.py                 # IBPS specific scraper
│   └── sbi.py                  # SBI specific scraper
├── 📁 static/                  # Frontend assets
│   ├── css/style.css           # Custom styles
│   └── js/calendar.js          # Calendar functionality
├── 📁 templates/               # HTML templates
│   └── index.html              # Main application page
├── app.py                      # FastAPI application
├── scraper.py                  # Main scraper orchestrator
├── db.py                       # Database models & operations
├── seed_data.py                # Database seeding script
├── requirements.txt            # Python dependencies
├── exams.db                    # SQLite database
└── README.md                   # This file
```

## 🔌 API Endpoints

### Exam Data
- `GET /` - Main web interface
- `GET /exams` - Get all exams with optional filters
- `GET /exams/month/{year}/{month}` - Get exams for specific month
- `GET /api/debug/all-exams` - Debug endpoint with all exam data

### Query Parameters
- `conducting_body`: Filter by conducting body (UPSC, SSC, IBPS, etc.)
- `date`: Filter by specific date (YYYY-MM-DD)

### Example API Calls
```bash
# Get all exams
curl http://localhost:8000/exams

# Get UPSC exams for June 2025
curl "http://localhost:8000/exams/month/2025/6?conducting_body=UPSC"

# Get all exams for December 2024
curl http://localhost:8000/exams/month/2024/12
```

## 🔧 Usage

### Running Scrapers
```bash
# Run all scrapers to fetch latest exam data
python scraper.py

# Seed database with sample data
python seed_data.py
```

### Development Server
```bash
# Start with auto-reload for development
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Database Schema

The application uses SQLite with the following schema:

```sql
CREATE TABLE exams (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    date DATE NOT NULL,
    body TEXT NOT NULL,
    link TEXT,
    application_start DATE,
    application_end DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🌐 Web Interface Features

### Calendar View
- **Monthly navigation** with prev/next buttons
- **Color-coded events** by conducting body
- **Event tooltips** with exam names
- **Click events** for detailed information

### Filtering
- **Conducting body filter** dropdown
- **Real-time filtering** without page reload
- **Statistics dashboard** showing exam counts

### Exam Details Modal
- **Exam name and date**
- **Conducting body information**
- **Application start and end dates**
- **Application status** (Open/Closed/Coming Soon)
- **Official notification links**

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Lightweight database
- **BeautifulSoup4** - Web scraping
- **Requests** - HTTP library
- **Uvicorn** - ASGI server

### Frontend
- **HTML5** - Semantic markup
- **Bootstrap 5** - CSS framework
- **FullCalendar** - Interactive calendar
- **Font Awesome** - Icons
- **Vanilla JavaScript** - Client-side logic

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use error:**
```bash
# Kill existing process
pkill -f uvicorn
# Or use different port
uvicorn app:app --port 8001
```

2. **Database not found:**
```bash
# Initialize database
python seed_data.py
```

3. **Scraper errors:**
```bash
# Check scraper.log for detailed error messages
tail -f scraper.log
```

4. **Calendar not showing events:**
- Check browser console for JavaScript errors
- Verify API endpoints are returning data
- Ensure correct element IDs in HTML/JavaScript

## 📈 Current Status

### Working Components ✅
- Web application with interactive calendar
- Database with 94 exams (12 scraped + 82 seeded)
- API endpoints with filtering
- Responsive UI with modern design
- Application deadline tracking

### Known Issues ⚠️
- Most scrapers fail due to website access restrictions
- Some websites block automated requests
- DNS resolution issues with certain domains
- Rate limiting on some sources

### Future Enhancements 🚀
- Email notifications for application deadlines
- Exam result tracking
- User accounts and personalized calendars
- Mobile app development
- Integration with more official sources

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive error handling
- Include logging for debugging
- Test scrapers with various scenarios
- Update documentation for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all the official government websites providing exam information
- FullCalendar.js for the excellent calendar component
- Bootstrap team for the responsive CSS framework
- FastAPI community for the amazing web framework

## 📞 Support

For support, issues, or feature requests:
1. Open an issue on GitHub
2. Check existing documentation
3. Review API documentation at `/docs`

---

**Made with ❤️ for Indian government exam aspirants** 