const Sunday =[
    {   
        time: 'Sunday',
        roomNumber: 'Holiday',
        subject: 'No class Available',
        type: ''
    }
]
const Monday =[
    {   
        time: '09-10 AM',
        roomNumber: '38-718',
        subject: 'DBMS130',
        type: 'Lecture'
    },
    {   
        time: '10-11 AM',
        roomNumber: '38-718',
        subject: 'MTH166',
        type: 'Tutorial'
    },
    {   
        time: '12-01 PM',
        roomNumber: '38-718',
        subject: 'NS200',
        type: 'Lecture'
    }
]
const Tuesday =[
    {   
        time: '09-10 AM',
        roomNumber: '27-304Y',
        subject: 'MTH166',
        type: 'Tutorial'
    },
    {   
        time: '11-12 AM',
        roomNumber: '28-107',
        subject: 'CS849',
        type: 'Lecture'
    },
    {   
        time: '12-01 PM',
        roomNumber: '28-107',
        subject: 'CS849',
        type: 'Lecture'
    },
    {   
        time: '02-03 PM',
        roomNumber: '38-718',
        subject: 'NS200',
        type: 'Lecture'
    }
]

const Wednesday =[
    {   
        time: '10-11 AM',
        roomNumber: '33-309',
        subject: 'DBMS130',
        type: 'Lecture'
    },
    {   
        time: '11-12 AM',
        roomNumber: '38-719',
        subject: 'CS200',
        type: 'Lecture'
    }
]

const Thursday =[
    {   
        time: '11-12 AM',
        roomNumber: '33-309',
        subject: 'MTH166',
        type: 'Lecture'
    },
    {   
        time: '01-02 PM',
        roomNumber: '38-719',
        subject: 'CS849',
        type: 'Lecture'
    },
    {   
        time: '02-03 PM',
        roomNumber: '38-718',
        subject: 'NS200',
        type: 'Lecture'
    }
]

const Friday =[
    {   
        time: '10-11 AM',
        roomNumber: '33-309',
        subject: 'MEC103',
        type: 'Lecture'
    },
    {   
        time: '11-12 AM',
        roomNumber: '33-309',
        subject: 'MEC103',
        type: 'Lecture'
    },
    {   
        time: '02-03 PM',
        roomNumber: '33-601',
        subject: 'CS849',
        type: 'Tutorial'
    },

]

const Saturday =[
    {   
        time: '09-10 AM',
        roomNumber: '34-604',
        subject: 'DBMS130',
        type: 'Tutorial'
    },
    {   
        time: '10-11 AM',
        roomNumber: '34-604',
        subject: 'DBMS130',
        type: 'Lecture'
    },
    {   
        time: '01-02 PM',
        roomNumber: '33-309',
        subject: 'MTH166',
        type: 'Lecture'
    }
]

// Timetable navigation and display
document.addEventListener('DOMContentLoaded', function() {
    const prevWeekBtn = document.getElementById('prevWeek');
    const nextWeekBtn = document.getElementById('nextWeek');
    const currentWeekDisplay = document.getElementById('currentWeek');
    
    if (prevWeekBtn && nextWeekBtn && currentWeekDisplay) {
        let currentDate = new Date();
        
        function updateWeekDisplay() {
            const startOfWeek = new Date(currentDate);
            startOfWeek.setDate(currentDate.getDate() - currentDate.getDay() + 1); // Start from Monday
            
            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(startOfWeek.getDate() + 4); // End on Friday
            
            const options = { month: 'long', day: 'numeric', year: 'numeric' };
            currentWeekDisplay.textContent = `Week of ${startOfWeek.toLocaleDateString('en-US', options)}`;
        }
        
        prevWeekBtn.addEventListener('click', function() {
            currentDate.setDate(currentDate.getDate() - 7);
            updateWeekDisplay();
            // Here you would typically make an AJAX call to get the previous week's schedule
        });
        
        nextWeekBtn.addEventListener('click', function() {
            currentDate.setDate(currentDate.getDate() + 7);
            updateWeekDisplay();
            // Here you would typically make an AJAX call to get the next week's schedule
        });
        
        // Initialize the display
        updateWeekDisplay();
    }
    
    // Handle lesson slot clicks
    const lessonSlots = document.querySelectorAll('.lesson-slot');
    lessonSlots.forEach(slot => {
        slot.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                // Let the link handle the navigation
                return;
            }
            
            const lessonTitle = this.querySelector('h4').textContent;
            const lessonType = this.classList.contains('online') ? 'Online' : 'Pre-recorded';
            const unitName = this.querySelector('p:nth-of-type(2)').textContent;
            
            // You could show a modal or tooltip with more details
            alert(`${lessonTitle}\nType: ${lessonType}\nUnit: ${unitName}`);
        });
    });
    
    // Handle free slot clicks
    const freeSlots = document.querySelectorAll('.free-slot');
    freeSlots.forEach(slot => {
        slot.addEventListener('click', function() {
            const day = this.parentElement.dataset.day;
            const time = this.parentElement.dataset.time;
            
            // You could show a modal to add a new lesson here
            alert(`Free slot on ${day} at ${time}`);
        });
    });
});