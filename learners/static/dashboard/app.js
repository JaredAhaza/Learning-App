const sideMenu = document.querySelector("aside");
const profileBtn = document.querySelector("#profile-btn");
const themeToggler = document.querySelector(".theme-toggler");
const nextDay = document.getElementById('nextDay');
const prevDay = document.getElementById('prevDay');
const navbar = document.querySelector("header .navbar");

// Only add event listener if profile button exists (mobile only)
if (profileBtn) {
    profileBtn.onclick = function() {
        if (sideMenu) {
            sideMenu.classList.toggle('active');
        }
        // Also toggle navbar on mobile
        if (navbar) {
            navbar.classList.toggle('active');
        }
    }
}

// Close aside and navbar when clicking outside on mobile
document.addEventListener('click', function(event) {
    if (sideMenu && sideMenu.classList.contains('active')) {
        if (!sideMenu.contains(event.target) && !profileBtn.contains(event.target)) {
            sideMenu.classList.remove('active');
        }
    }
    
    if (navbar && navbar.classList.contains('active')) {
        if (!navbar.contains(event.target) && !profileBtn.contains(event.target)) {
            navbar.classList.remove('active');
        }
    }
});

window.onscroll = () => {
    if (sideMenu) {
        sideMenu.classList.remove('active');
    }
    if(window.scrollY > 0){
        const header = document.querySelector('header');
        if (header) {
            header.classList.add('active');
        }
    } else {
        const header = document.querySelector('header');
        if (header) {
            header.classList.remove('active');
        }
    }
}

if (themeToggler) {
    themeToggler.onclick = function() {
        document.body.classList.toggle('dark-theme');
        
        themeToggler.querySelector('span:nth-child(1)').classList.toggle('active');
        themeToggler.querySelector('span:nth-child(2)').classList.toggle('active');
    }
}

let setData = (day) =>{
    document.querySelector('table tbody').innerHTML = ' '; //To clear out previous table data;  
    let daylist = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    document.querySelector('.timetable div h2').innerHTML = daylist[day];
    switch(day){
        case(0): day = Sunday; break;
        case(1): day = Monday; break;
        case(2): day = Tuesday; break;
        case(3): day = Wednesday; break;
        case(4): day = Thursday; break;
        case(5): day = Friday; break;
        case(6): day = Saturday; break;
    }

    day.forEach(sub => {
        const tr = document.createElement('tr');
        const trContent = `
                            <td>${sub.time}</td>
                            <td>${sub.roomNumber}</td>
                            <td>${sub.subject}</td>
                            <td>${sub.type}</td>
                        `
        tr.innerHTML = trContent;
        document.querySelector('table tbody').appendChild(tr)                        
    });
}

let now = new Date();
let today = now.getDay(); // Will return the present day in numerical value; 
let day = today; //To prevent the today value from changing;

function timeTableAll(){
    document.getElementById('timetable').classList.toggle('active');
    setData(today);
    document.querySelector('.timetable div h2').innerHTML = "Today's Timetable";
}
nextDay.onclick = function() {
    day<=5 ? day++ : day=0;  // If else one liner
    setData(day);
}
prevDay.onclick = function() {
    day>=1 ? day-- : day=6;    
    setData(day);
}

setData(day); //To set the data in the table on loading window.
document.querySelector('.timetable div h2').innerHTML = "Today's Timetable"; //To prevent overwriting the heading on loading;

// Handle progress circles
document.addEventListener('DOMContentLoaded', function() {
    const progressCircles = document.querySelectorAll('circle[data-progress]');
    progressCircles.forEach(function(circle) {
        const progress = parseFloat(circle.getAttribute('data-progress'));
        const strokeDashoffset = 226.08 - (226.08 * progress) / 100;
        circle.style.strokeDashoffset = strokeDashoffset;
    });
    
    // Add smooth scrolling for mobile
    if (window.innerWidth <= 768) {
        document.documentElement.style.scrollBehavior = 'smooth';
    }
});

// Handle window resize
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        // Reset mobile states on desktop
        if (sideMenu) {
            sideMenu.classList.remove('active');
        }
        if (navbar) {
            navbar.classList.remove('active');
        }
    }
});
