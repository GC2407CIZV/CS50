// LIGHTBOX
let currentIndex = 0;
const items = []; // Store gallery items

// Preload images to improve performance
function preloadImage(src) {
    const img = new Image();
    img.src = src;
}

function preloadNextAndPrevious(index) {
    const nextIndex = getNextVisibleIndex(index, 1);
    const prevIndex = getNextVisibleIndex(index, -1);
    preloadImage(items[nextIndex].src);
    preloadImage(items[prevIndex].src);
}

// Open the lightbox and display the selected image or video
function openLightbox(src, type) {
    currentIndex = items.findIndex(item => item.src === src && item.type === type && !item.hidden);
    document.getElementById("lightbox").style.display = "flex";
    updateLightboxMedia(currentIndex);
}

// Close the lightbox and stop any playing videos
function closeLightbox() {
    document.getElementById("lightbox").style.display = "none";
    const videoElement = document.getElementById("lightbox-video");
    if (videoElement) {
        videoElement.pause();
        videoElement.src = ""; // Clear video source to stop it from loading
    }
}

// Get the next visible index
function getNextVisibleIndex(current, direction) {
    let newIndex = current;
    do {
        newIndex = (newIndex + direction + items.length) % items.length;
    } while (items[newIndex].hidden);
    return newIndex;
}

// Change to the next or previous media item
function changeSlide(direction) {
    currentIndex = getNextVisibleIndex(currentIndex, direction);
    updateLightboxMedia(currentIndex);
}

// Update the lightbox with the current media (image or video)
function updateLightboxMedia(index) {
    const currentItem = items[index];

    // Preload adjacent images for faster transitions
    preloadNextAndPrevious(index);

    // Stop and clear the current video if it is playing
    const videoElement = document.getElementById("lightbox-video");
    const imgElement = document.getElementById("lightbox-img");
    if (videoElement && !videoElement.paused) {
        videoElement.pause();
        videoElement.src = ""; // Clear the video source to stop it
    }

    if (currentItem.type === "video") {
        videoElement.src = currentItem.src; // Set the new video source
        videoElement.style.display = "block"; // Show the video element
        videoElement.play(); // Play the new video
        imgElement.style.display = "none"; // Hide the image element
    } else {
        imgElement.src = currentItem.src; // Set the new image source
        imgElement.style.display = "block"; // Show the image element
        videoElement.style.display = "none"; // Hide the video element
    }
}

// Add media items (images or videos) to the gallery
function addItem(src, type, hidden = false) {
    items.push({
        src,
        type,
        hidden
    });
}

// Initialize gallery items and set up event listeners after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const galleryItems = document.querySelectorAll('.gallery-item img, .gallery-item video');
    galleryItems.forEach(item => {
        const type = item.tagName.toLowerCase() === 'video' ? 'video' : 'image';
        const hidden = item.closest('.gallery-item').classList.contains('hiddenImage');
        addItem(type === 'video' ? item.querySelector('source').src : item.src, type, hidden);

        // Attach click event to each visible gallery item
        if (!hidden) {
            item.addEventListener('click', function() {
                openLightbox(type === 'video' ? item.querySelector('source').src : item.src, type);
            });
        }
    });

    // Close lightbox when close button is clicked
    document.getElementById("close-button").addEventListener('click', closeLightbox);

    setupSlideNavigation();
});

// Add event listener for keyboard arrow keys
document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") {
        changeSlide(-1); // Left arrow key
    } else if (event.key === "ArrowRight") {
        changeSlide(1); // Right arrow key
    } else if (event.key === "Escape") {
        closeLightbox(); // Close lightbox when 'Escape' key is pressed
    }
});

function setupSlideNavigation() {
    document.getElementById("prev-btn").addEventListener("click", () => changeSlide(-1));
    document.getElementById("next-btn").addEventListener("click", () => changeSlide(1));
}

// CHATBOX CHAT ON FAKEBOOK AND BAR
// Toggle chat box visibility
function toggleChatBox() {
    var chatBox = document.getElementById('chatBox');
    var chatButton = document.getElementById('chatButton');

    console.log('Toggling chat box...'); // Debugging line

    if (chatBox.classList.contains('hidden')) {
        chatBox.classList.remove('hidden');
        chatButton.classList.add('hidden');
    } else {
        chatBox.classList.add('hidden');
        chatButton.classList.remove('hidden');
    }
}

// Function to minimize or maximize the chat box
function toggleMinimize() {
    var chatBox = document.getElementById('chatBox');
    var minimizeButton = document.querySelector('.minimize-btn');

    if (chatBox.classList.contains('minimized')) {
        chatBox.classList.remove('minimized');
        minimizeButton.innerText = '_'; // Or set to a different icon if preferred
    } else {
        chatBox.classList.add('minimized');
        minimizeButton.innerText = '+'; // Or set to a different icon if preferred
    }
}

function sendMessage() {
    const input = document.querySelector('.chat-input');
    const message = input.value.trim();
    const chatButton = document.getElementById('chatButton');
    const source = chatButton.getAttribute('data-source'); // Get the source

    if (message) {
        const chatBody = document.querySelector('.chat-body');

        // Check if the source is Fakebook
        if (source === 'fakebook') {
            // Add a line break before the sender message
            chatBody.appendChild(document.createElement('br'));
        }

        // Create and append the user message
        const userMessage = createMessageElement('sender-message', message);
        chatBody.appendChild(userMessage);

        // Check if the source is Fakebook to add another <br> after sender-message
        if (source === 'fakebook') {
            // Add a line break after the sender message
            chatBody.appendChild(document.createElement('br'));
        }

        // Generate bot response based on source
        const botResponse = generateBotResponse(source, message);

        // Create and append the bot message if there's a response
        if (botResponse) {
            const botMessage = createMessageElement('responder-message', botResponse);
            chatBody.appendChild(botMessage);
        } else {
            console.error("Bot response is empty or undefined.");
        }

        // Scroll to the bottom of the chat
        chatBody.scrollTop = chatBody.scrollHeight;
        input.value = ''; // Clear input
    } else {
        console.log("Please enter a message.");
    }
}

// Function to create a message element
function createMessageElement(className, text) {
    const messageElement = document.createElement('div');
    messageElement.className = className;
    const sentences = text.split(/(?<=[.!?'])(\s+)/); // Split on punctuation followed by space or apostrophe
    messageElement.innerHTML = sentences.map(sentence => `<p>${sentence.trim()}</p>`).join('');
    return messageElement;
}

// Function to generate bot responses based on the source
function generateBotResponse(source, message) {
    if (source === 'fakebook') {
        return generateFakebookResponse(message);

    } else if (source === 'bar') {
        return generateBarResponse(message);
    }
}

document.querySelector('.chat-input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') { // Check if Enter key is pressed
        event.preventDefault(); // Prevent default action (optional, may stop a newline)
        sendMessage(); // Call sendMessage function
    }
});

function generateFakebookResponse(message) {
    if (message.toLowerCase().includes('where are you')) {
        return "I’sss at Dark Wing to gedd one toooo... hic.";
    } else if (message.toLowerCase().includes('help')) {
        return "Ugh dude, I can’t deal right now. hic. I’m hurtin'! Just come over he' already!";
    } else {
        return "Wha dooo ya wannnt? hic.";
    }
}

// Function to generate bar-specific responses
function generateBarResponse(message) {
    const jokes = [
        "I used to be a bartender in a place that had a lot of magic. I had a great trick for making drinks disappear—just charge 'em extra!",
        "What did the bartender say after Charles Dickens ordered a martini? 'Olive or twist?'",
        "A guy walks into a bar and orders a fruit punch. The bartender says, 'If you want a fruit punch, you’ll have to get in line!'",
        "Why did the computer go to the bar? Because it needed to get a byte!",
        "A guy walks into a bar with a parrot on his shoulder. The bartender says, 'Where’d you get that?' The parrot replies, 'In a small town, they’re everywhere!'",
        "Why did the man bring a ladder to the bar? Because he heard the drinks were on the house!",
        "A computer science student walks into a bar. The bartender says, 'What’ll it be?' The student replies, 'I’ll have a binary beer, please.' The bartender chuckles, 'Got it! That’s 1010101 cents, coming right up!'",
        "I told the bartender to make me a zombie. He said, 'You look pretty alive to me!'",
        "A bartender says, 'Sorry, we don’t serve SQL queries here.' The programmer replies, 'But I just wanted to SELECT * FROM Drinks!'",
        "I told my bartender I’d like a drink that lasts all night. He gave me a long straw.",
        "A CS50 student walks into a bar. The bartender says, 'What can I get you?' The student replies, 'I'll take one drink.' The bartender says, 'Sorry, we only serve arrays of drinks here.' The student then says, 'Fine. I'll take one drink[0].'",
        "A drunk walks into a bar and orders a double. The bartender says, 'We don’t serve doubles here.' The drunk replies, 'Then I’ll take two singles!'",
        "A CS50 student walks into a bar, orders a drink, but nothing happens. The bartender says, 'Sorry, your drink is still compiling.'",
        "One day a man walks into a bar and to his amazement, he finds a tiny person playing a tiny piano. Stunned, the man asks the bartender where he got this amazing person. The bartender replies that inside the closet there is a genie that will grant him a single wish. The man dashes into the closet, and as the bartender said, there was a genie inside. Without hesitation, the man wishes for a million bucks, but instead a million ducks instantly appear. Infuriated, the man storms to the bartender and screams, 'I think your genie is hard of hearing; I asked for a million bucks but instead I got a million ducks.' The bartender shakes his head and replies, 'You're telling me... Do you really think I asked for a 12-inch pianist?'",
        "A CS50 student walks into a bar and asks for a drink. The bartender replies, '404 — drink not found.'",
        "Why don't scientists trust atoms? Because they make up everything! Just like my ex when she ordered a drink!",
        "Why don't programmers like nature? Because it has too many bugs!"
    ];

    if (message.toLowerCase().includes('talk about') ||
        message.toLowerCase().includes('where to go') ||
        message.toLowerCase().includes('remember')) {
        return "Man, yesterday was a blur with all the folks around. But I think I remember you chattin' about a beach thing and swimming... like maybe a party or somethin’? Sound familiar?";
    } else if (message.toLowerCase().includes('help')) {
        return "Help, eh? I might not be a therapist, but I can definitely help you quench your thirst!  Cocktails are quite popular these days. How 'bout trying one of these delights from my menu?";
    } else if (message.toLowerCase().includes('duck fizz') ||
        message.toLowerCase().includes('waddling whiskey') ||
        message.toLowerCase().includes('quacktail royale') ||
        message.toLowerCase().includes('feathered daiquiri') ||
        message.toLowerCase().includes('crimson quacktail') ||
        message.toLowerCase().includes('duck debugger') ||
        message.toLowerCase().includes('infinite loop lush') ||
        message.toLowerCase().includes('quicksort old fashioned') ||
        message.toLowerCase().includes('binary bliss') ||
        message.toLowerCase().includes('plumage punch')) {
        return "Hey, buddy! I can’t whip up anything too adventurous for you today—you might still be riding the waves from last night! But I’ve got a little something that could help jog those memory cells. It’s smooth, it’s easy, and it just might help you rediscover the fun you had! Just say the magic word, and I’ll get it ready for you!";
    } else if (message.toLowerCase().includes('hey') || message.toLowerCase().includes('hello')) {
        return "Hey buddy! What can I get ya?";
    } else if (message.toLowerCase().includes('forgetful fowl')) {
        return "Ah, the Forgetful Fowl! Just one sip, and you might find yourself so blissfully relaxed that even your own name slips your mind! Just a friendly reminder: if you wake up with a duck in your bathtub, well, that’s not our fault! And hey, if you can name me four of the ingredients, I might just slip you a little tip!";
    } else if (message.toLowerCase().includes('vodka') &&
        message.toLowerCase().includes('elderflower') &&
        message.toLowerCase().includes('blue curacao') &&
        (message.toLowerCase().includes('mint leaves') || message.toLowerCase().includes('lemon juice'))) {
        return "Hey, you nailed it! Those are the magic ingredients! Just hearing 'em makes me forget everything already—no wonder you can't remember last night. You drank that cocktail like it was water, huh? As for your tip... Ah, it's a little fuzzy with all the folks comin' through, but I do remember you guys struttin' in here, grinnin' ear to ear after winning that Sand Sculpture contest, flashing that shiny golden shovel like it was the crown jewels! After that, things got a bit blurry, but I think you were rambling on about a skinny dipping or somethin'? Ring any bells?";
    } else if (message.toLowerCase().includes('vodka') ||
        message.toLowerCase().includes('elderflower') ||
        message.toLowerCase().includes('blue curacao') ||
        message.toLowerCase().includes('mint leaves') || message.toLowerCase().includes('lemon juice')) {
        return "Hey, pal! I need you to hit me with all the ingredients at once—no loops or conditional statements here. Let’s compile that drink recipe like true programmers. Give it another shot!";

    } else {
        const randomIndex = Math.floor(Math.random() * jokes.length);
        return "Little humor to debug your day! " + jokes[randomIndex];
    }
}

// REVEAL OR HIDE PICTURES IN FUNCTION OF CLUE GIVEN
// Example clue_ids array passed from the server
function revealImages() {
    const images = document.querySelectorAll('.gallery-item');
    const articles = document.querySelectorAll('.article');

    images.forEach(image => {
        const imageId = image.id;

        if (imageId === "clueImage_0" && clue_ids.includes(1)) {
            image.classList.remove('hiddenImage');
        }
        if (imageId === "clueImage_1" && clue_ids.includes(3)) {
            image.classList.remove('hiddenImage');
        }
        if (imageId === "clueImage_2" && clue_ids.includes(3)) {
            image.classList.add('hiddenImage');
        }
        if (imageId === "clueImage_3" && clue_ids.includes(12)) {
            image.classList.remove('hiddenImage');
        }
        if (imageId === "clueImage_4" && clue_ids.includes(21)) {
            image.classList.remove('hiddenImage');
        }

        // Index. html
        if (imageId === "clueImage_5" && clue_ids.includes(0)) {
            image.classList.remove('hiddenImage');
        }
        if (imageId === "clueImage_6" && clue_ids.includes(11)) {
            image.classList.remove('hiddenImage');
        }
        if (imageId === "clueImage_7" && clue_ids.includes(14)) {
            image.classList.remove('hiddenImage');
        }
        if (imageId === "clueImage_8" && clue_ids.includes(15)) {
            image.classList.remove('hiddenImage');
        }
        if (imageId === "clueImage_9" && clue_ids.includes(20)) {
            image.classList.remove('hiddenImage');
        }
        if (imageId === "clueImage_10" && clue_ids.includes(19)) {
            image.classList.remove('hiddenImage');
        }

    });

    articles.forEach(article => {
        const articleId = article.id;
        console.log(`Checking article with id: ${articleId}`); // Log article id

        if (articleId === "clueImage_13" && clue_ids.includes(15)) {
            article.classList.remove('hiddenImage');
        }
        if (articleId === "clueImage_14" && clue_ids.includes(16)) {
            article.classList.remove('hiddenImage');
        }
    });

    initializeLightbox(); // Initialize lightbox
}


function initializeLightbox() {
    items.length = 0; // Clear items array before re-populating

    const galleryItems = document.querySelectorAll('.gallery-item img, .gallery-item video');
    galleryItems.forEach(item => {
        const type = item.tagName.toLowerCase() === 'video' ? 'video' : 'image';
        addItem(item.tagName.toLowerCase() === 'video' ? item.querySelector('source').src : item.src, type);

        // Re-attach the click event
        item.addEventListener('click', function() {
            openLightbox(item.tagName.toLowerCase() === 'video' ? item.querySelector('source').src : item.src, type);
        });
    });
}

// Initialize variables for time spent
let totalTimeSpent = parseInt('{{ total_time_spent }}'); // Server-sent accumulated time in seconds
let startTime = Date.now();

// Function to format time in DD:HH:MM:SS format
function formatTime(seconds) {
    let days = Math.floor(seconds / (3600 * 24)); // Calculate total days
    let hours = Math.floor((seconds % (3600 * 24)) / 3600); // Calculate remaining hours
    let minutes = Math.floor((seconds % 3600) / 60); // Calculate remaining minutes
    let secs = Math.floor(seconds % 60); // Calculate remaining seconds

    let completeDays = Math.floor(days % (3600 * 24)); // Assuming you want to show days as a smaller unit

    // Format the output string
    return (
        (completeDays > 0 ? (days + ' days ') : '') + // Show days only if > 0
        (hours < 10 ? '0' : '') + hours + ':' +
        (minutes < 10 ? '0' : '') + minutes + ':' +
        (secs < 10 ? '0' : '') + secs
    );
}

// Function to update the clock display
function updateClock() {
    let currentTime = Date.now();
    let timeElapsed = (currentTime - startTime) / 1000; // Elapsed time in seconds
    let totalSeconds = totalTimeSpent + timeElapsed;

    // Update the clock display in DD:HH:MM:SS format
    document.getElementById('live-clock').innerText = formatTime(totalSeconds);
}

// Periodically update time spent on server
function saveTimeSpent() {
    let currentTime = Date.now();
    let timeElapsed = (currentTime - startTime) / 1000; // Elapsed time in seconds
    let totalSeconds = totalTimeSpent + timeElapsed;

    // Send a POST request to save time on the server
    fetch('/save_time', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                timeSpent: totalSeconds
            })
        })
        .then(response => {
            if (!response.ok) {
                console.error('Failed to save time');
            }
        })
        .catch(error => console.error('Error:', error));
}

// Start the clock and update every second
setInterval(updateClock, 1000);

// Save time every 30 seconds
setInterval(saveTimeSpent, 30000);

// Optionally save time on page unload
window.addEventListener('beforeunload', saveTimeSpent);
