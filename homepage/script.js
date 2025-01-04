document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling
    document.querySelectorAll('.navbar a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            document.getElementById(targetId).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Portfolio item hover effect
    const portfolioItems = document.querySelectorAll('.portfolio-section ul li');
    portfolioItems.forEach(item => {
        item.addEventListener('mouseover', function() {
            this.style.backgroundColor = '#f4f4f4';
            this.style.borderRadius = '5px';
            this.style.padding = '5px';
            this.style.transition = 'background-color 0.3s';
        });
        item.addEventListener('mouseout', function() {
            this.style.backgroundColor = 'transparent';
        });
    });

    // Homepage text animation
    const homeText = document.querySelector('.home-section h1');
    setTimeout(() => {
        homeText.style.opacity = 1;
        homeText.style.transform = 'translateY(0)';
        homeText.style.transition = 'opacity 1s, transform 1s';
    }, 500);

    homeText.style.opacity = 0;
    homeText.style.transform = 'translateY(20px)';
});

// Get the button:
let mybutton = document.getElementById("myBtn");

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {
    scrollFunction()
};

function scrollFunction() {
    if (document.body.scrollTop > 500 || document.documentElement.scrollTop > 500) {
        mybutton.style.display = "block";
    } else {
        mybutton.style.display = "none";
    }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}
// Plays the video automatically when it's in screen
var video = document.getElementById('Intro'),
    fraction = 0.8;

function checkScroll() {
    var x = video.offsetLeft,
        y = video.offsetTop,
        w = video.offsetWidth,
        h = video.offsetHeight,
        r = x + w, //right
        b = y + h, //bottom
        visibleX, visibleY, visible;

    visibleX = Math.max(0, Math.min(w, window.pageXOffset + window.innerWidth - x, r - window.pageXOffset));
    visibleY = Math.max(0, Math.min(h, window.pageYOffset + window.innerHeight - y, b - window.pageYOffset));

    visible = visibleX * visibleY / (w * h);

    if (visible > fraction) {
        video.play();
    } else {
        video.pause();
    }
}
checkScroll();
window.addEventListener('scroll', checkScroll, false);
window.addEventListener('resize', checkScroll, false);
