document.addEventListener('DOMContentLoaded', function() {
    // Initialize calendar
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,listMonth'
        },
        events: function(info, successCallback, failureCallback) {
            fetchEvents(info, successCallback, failureCallback);
        },
        eventClick: handleEventClick,
        height: 'auto',
        firstDay: 1, // Start week on Monday
        displayEventTime: false,
        eventDisplay: 'block',
        dayMaxEvents: 3,
        moreLinkClick: 'popover',
        loading: function(isLoading) {
            console.log('Calendar loading:', isLoading);
        }
    });

    calendar.render();

    // Make calendar globally accessible for updateCalendar function
    window.calendar = calendar;

    // Handle conducting body filter changes
    const conductingBodySelect = document.getElementById('conducting_body');
    if (conductingBodySelect) {
        conductingBodySelect.addEventListener('change', function() {
            console.log('Filter changed to:', this.value);
            calendar.refetchEvents();
        });
    }

    // Fetch events for the calendar
    async function fetchEvents(info, successCallback, failureCallback) {
        try {
            console.log('=== CALENDAR EVENT FETCH ===');
            console.log('Fetching events for date range:', info.start.toISOString(), 'to', info.end.toISOString());
            
            const conductingBodyElement = document.getElementById('conducting_body');
            const conductingBody = conductingBodyElement ? conductingBodyElement.value : '';
            console.log('Conducting body filter:', conductingBody);
            
            // Get all months in the date range
            const months = getMonthsInRange(info.start, info.end);
            console.log('Months to fetch:', months);
            
            // Fetch data for all months
            const allEvents = [];
            
            for (const monthInfo of months) {
                let url = `/exams/month/${monthInfo.year}/${monthInfo.month}`;
                if (conductingBody && conductingBody !== '') {
                    url += `?conducting_body=${encodeURIComponent(conductingBody)}`;
                }
                
                console.log(`Fetching from URL: ${url}`);
                
                try {
                    const response = await fetch(url);
                    if (!response.ok) {
                        console.error(`HTTP error! status: ${response.status} for ${url}`);
                        continue;
                    }
                    
                    const exams = await response.json();
                    console.log(`✓ Received ${exams.length} exams for ${monthInfo.year}-${monthInfo.month}`);
                    
                    // Filter events to only include those in the requested date range
                    const filteredExams = exams.filter(exam => {
                        const examDate = new Date(exam.date);
                        return examDate >= info.start && examDate < info.end;
                    });
                    
                    console.log(`✓ Filtered to ${filteredExams.length} exams in date range`);
                    
                    const events = filteredExams.map(exam => {
                        const event = {
                            id: exam.id,
                            title: exam.name,
                            start: exam.date,
                            allDay: true,
                            backgroundColor: getEventColor(exam.body),
                            borderColor: getEventColor(exam.body),
                            textColor: '#ffffff',
                            extendedProps: {
                                body: exam.body,
                                link: exam.link,
                                app_start: exam.app_start,
                                app_end: exam.app_end,
                                app_start_formatted: exam.app_start_formatted,
                                app_end_formatted: exam.app_end_formatted,
                                exam_date_formatted: exam.exam_date_formatted
                            }
                        };
                        console.log(`✓ Created event: ${event.title} on ${event.start}`);
                        return event;
                    });
                    
                    allEvents.push(...events);
                    
                } catch (fetchError) {
                    console.error(`Error fetching ${url}:`, fetchError);
                }
            }
            
            console.log(`=== FINAL RESULT: ${allEvents.length} events ===`);
            allEvents.forEach(event => {
                console.log(`  - ${event.title} on ${event.start}`);
            });
            
            successCallback(allEvents);
            
        } catch (error) {
            console.error('Error in fetchEvents:', error);
            failureCallback(error);
        }
    }

    // Helper function to get all months in a date range
    function getMonthsInRange(startDate, endDate) {
        const months = [];
        const current = new Date(startDate);
        
        while (current <= endDate) {
            months.push({
                year: current.getFullYear(),
                month: current.getMonth() + 1
            });
            
            // Move to next month
            current.setMonth(current.getMonth() + 1);
        }
        
        return months;
    }

    // Handle event clicks - show detailed modal
    function handleEventClick(info) {
        const event = info.event;
        const extendedProps = event.extendedProps;
        
        // Create modal content with application dates
        const modalContent = `
            <div class="modal fade" id="examModal" tabindex="-1" aria-labelledby="examModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="examModalLabel">
                                <i class="fas fa-calendar-alt me-2"></i>Exam Details
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-12">
                                    <h4 class="text-primary mb-3">${event.title}</h4>
                                </div>
                            </div>
                            
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <div class="card border-primary">
                                        <div class="card-header bg-light">
                                            <i class="fas fa-building me-2"></i><strong>Conducting Body</strong>
                                        </div>
                                        <div class="card-body">
                                            <span class="badge bg-${getBodyColor(extendedProps.body)} fs-6">${extendedProps.body}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="card border-success">
                                        <div class="card-header bg-light">
                                            <i class="fas fa-calendar-check me-2"></i><strong>Exam Date</strong>
                                        </div>
                                        <div class="card-body">
                                            <span class="text-success fw-bold">${extendedProps.exam_date_formatted || event.start.toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <div class="card border-info">
                                        <div class="card-header bg-light">
                                            <i class="fas fa-play-circle me-2"></i><strong>Application Start</strong>
                                        </div>
                                        <div class="card-body">
                                            <span class="text-info">${extendedProps.app_start_formatted || 'Not Available'}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="card border-danger">
                                        <div class="card-header bg-light">
                                            <i class="fas fa-stop-circle me-2"></i><strong>Application Deadline</strong>
                                        </div>
                                        <div class="card-body">
                                            <span class="text-danger fw-bold">${extendedProps.app_end_formatted || 'Not Available'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            ${getApplicationStatus(extendedProps)}
                            
                            ${extendedProps.link ? `
                            <div class="row">
                                <div class="col-12">
                                    <div class="d-grid">
                                        <a href="${extendedProps.link}" target="_blank" class="btn btn-primary btn-lg">
                                            <i class="fas fa-external-link-alt me-2"></i>View Official Notification
                                        </a>
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('examModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalContent);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('examModal'));
        modal.show();
        
        // Clean up modal after hiding
        document.getElementById('examModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }
    
    // Get application status with visual indicators
    function getApplicationStatus(props) {
        if (!props.app_start || !props.app_end) {
            return `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Application Dates:</strong> Not yet announced. Keep checking official website.
                </div>
            `;
        }
        
        const now = new Date();
        const appStart = new Date(props.app_start);
        const appEnd = new Date(props.app_end);
        
        if (now < appStart) {
            const daysToStart = Math.ceil((appStart - now) / (1000 * 60 * 60 * 24));
            return `
                <div class="alert alert-info">
                    <i class="fas fa-clock me-2"></i>
                    <strong>Application Status:</strong> Applications will open in ${daysToStart} day(s)
                </div>
            `;
        } else if (now >= appStart && now <= appEnd) {
            const daysLeft = Math.ceil((appEnd - now) / (1000 * 60 * 60 * 24));
            return `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong>Application Status:</strong> Applications are OPEN! ${daysLeft} day(s) left to apply
                </div>
            `;
        } else {
            return `
                <div class="alert alert-danger">
                    <i class="fas fa-times-circle me-2"></i>
                    <strong>Application Status:</strong> Application deadline has passed
                </div>
            `;
        }
    }
    
    // Get color for conducting body badge
    function getBodyColor(body) {
        const colors = {
            'UPSC': 'primary',
            'SSC': 'success',
            'IBPS': 'info',
            'SBI': 'warning',
            'RAILWAY': 'danger',
            'POLICE': 'dark',
            'TEACHING': 'secondary',
            'DEFENCE': 'primary',
            'MEDICAL': 'success',
            'ENGINEERING': 'info',
            'STATE_PSC': 'warning',
            'BANKING': 'primary'
        };
        return colors[body] || 'secondary';
    }

    // Get color based on conducting body
    function getEventColor(conductingBody) {
        const colors = {
            'UPSC': '#28a745',      // Green
            'SSC': '#007bff',       // Blue
            'IBPS': '#dc3545',      // Red
            'SBI': '#fd7e14',       // Orange
            'RAILWAY': '#6f42c1',   // Purple
            'BANKING': '#20c997',   // Teal
            'DEFENCE': '#e83e8c',   // Pink
            'POLICE': '#6c757d',    // Gray
            'TEACHING': '#17a2b8',  // Cyan
            'MEDICAL': '#ffc107',   // Yellow
            'ENGINEERING': '#343a40', // Dark
            'STATE_PSC': '#795548', // Brown
            'OTHER': '#607d8b'      // Blue Gray
        };
        return colors[conductingBody] || '#6c757d';
    }

    // Add some debugging
    console.log('Calendar initialized');
});

// Global function to update calendar when filter changes
function updateCalendar() {
    if (window.calendar) {
        console.log('Updating calendar with new filter');
        window.calendar.refetchEvents();
    }
} 