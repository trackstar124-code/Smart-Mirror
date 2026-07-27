// The list of view element ids, in order. To add a screen later, add its id here.
const views = ["view-home", "view-calendar"];
const COOLDOWN_MS = 3000; // 3 seconds

// Which view is currently showing (an index into `views`). Starts at 0 = home.
let current = 0;
let lastCall = 0;

// Show one view and hide the rest.
//   index = which view to show (0, 1, ...)
function showView(index) {
    // 1. Remove "active" from every view (hides them all).
    views.forEach(function (id) {
        document.getElementById(id).classList.remove("active");
    });
    // 2. Add "active" to just the one we want (shows it).
    document.getElementById(views[index]).classList.add("active");
    // 3. Remember which one is now showing.
    current = index;
}

// TEMPORARY test controls: arrow keys switch views
// This proves the switching works before we wire in gestures.
document.addEventListener("keydown", function (event) {
    if (event.key === "ArrowRight") {
        // go to the next view, wrapping back to 0 after the last one
        showView((current + 1) % views.length);
    } else if (event.key === "ArrowLeft") {
        // go to the previous view, wrapping to the last one before 0
        showView((current - 1 + views.length) % views.length);
    }
});

// --- Gesture polling (STEP 3) — YOU fill this in ---
// Ask the Flask endpoint what gesture is happening, then switch views to match.
function pollGesture() {
    fetch("/api/gesture")
        .then(response => response.json())
        .then(data => {
            const now = Date.now();
            if (now - lastCall < COOLDOWN_MS) return;
            switch (data.gesture) {
                case "OK":
                    showView(0);
                    lastCall = now;
                    break;
                case "FIST":
                    showView(1);
                    lastCall = now;
                    break;
            }
        })
        .catch(err => console.error("Gesture poll failed:", err));
}
setInterval(pollGesture, 300);

//make it so the clock updates in the Html
function updateClock() {
    const time = new Date().toLocaleTimeString();
    document.getElementById("time-display").innerText = time;
}
updateClock();
setInterval(updateClock, 1000);



// --- NYT News Logic (Backend Polling & Rotation) ---
let newsArticles = [];
let currentNewsIndex = 0;
let newsRotationInterval = null;

function displayCurrentNews() {
    const newsContent = document.getElementById('nyt-news-content');
    if (!newsContent || newsArticles.length === 0) return;

    const article = newsArticles[currentNewsIndex];
    newsContent.innerHTML = '';

    const div = document.createElement('div');
    div.className = 'headline';

    const link = document.createElement('a');
    link.href = article.url;
    link.target = '_blank';
    link.textContent = article.title;

    div.appendChild(link);
    newsContent.appendChild(div);

    // Increment index to show the next article on the next tick
    currentNewsIndex = (currentNewsIndex + 1) % newsArticles.length;
}

function pollNews() {
    fetch("/api/news")
        .then(response => response.json())
        .then(data => {
            const articles = data.articles;
            if (!articles || articles.length === 0) {
                return; // Keep existing content if fetch fails or is empty
            }

            // Update our global list and reset index
            newsArticles = articles;
            currentNewsIndex = 0;

            // Display the first one immediately
            displayCurrentNews();

            // Clear any existing rotation and start a new one (every 30 seconds)
            if (newsRotationInterval) clearInterval(newsRotationInterval);
            newsRotationInterval = setInterval(displayCurrentNews, 30 * 1000);
        })
        .catch(err => console.error("News poll failed:", err));
}

// Fetch news immediately, then every 30 minutes
pollNews();
setInterval(pollNews, 30 * 60 * 1000);