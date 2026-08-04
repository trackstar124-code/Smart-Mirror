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

            // --- Swipe EVENTS: handle these FIRST, and outside the cooldown. ---
            // The server already popped the event, so if we bail out early here
            // the swipe is lost forever. The SwipeTracker's own cooldown in
            // gestures.py is what prevents repeats, so we don't need one here.
            if (data.event === "Swipe Right" || data.event === "Swipe Left") {
                const step = data.event === "Swipe Right" ? 1 : -1;
                // + views.length keeps the result positive when step is -1,
                // so index -1 wraps to the last view instead of breaking.
                showView((current + step + views.length) % views.length);
                // Stamp the pose cooldown too: your hand is very likely still
                // open right after a swipe, and without this the pose branch
                // below would fire on the next poll and undo the swipe.
                lastCall = now;
                return;
            }

            // --- POSE: continuously true, so the cooldown belongs here ---
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


// --- Weather live refresh (every 10 minutes) ---
function pollWeather() {
    fetch("/api/weather")
        .then(response => response.json())
        .then(data => {
            const current  = data.current;
            const forecast = data.forecast;

            // Update current weather
            if (current) {
                const iconEl = document.getElementById("weather-icon");
                const tempEl = document.getElementById("weather-temp");
                const cityEl = document.getElementById("weather-city");
                if (iconEl) iconEl.src = `https://openweathermap.org/img/wn/${current.icon}@2x.png`;
                if (tempEl) tempEl.textContent = `${Math.round(current.temp)}°F`;
                if (cityEl) cityEl.textContent = current.city;
            }

            // Re-render forecast strip
            const forecastEl = document.getElementById("weather-forecast");
            if (forecastEl && forecast && forecast.length > 0) {
                forecastEl.innerHTML = forecast.map(day => `
                    <div class="forecast-day">
                        <div class="forecast-label">${day.day}</div>
                        <img class="forecast-icon"
                             src="https://openweathermap.org/img/wn/${day.icon}@2x.png"
                             alt="${day.day} weather">
                        <div class="forecast-temps">
                            <span class="forecast-high">${day.temp_high}°</span>
                            <span class="forecast-low">${day.temp_low}°</span>
                        </div>
                    </div>
                `).join("");
            }
        })
        .catch(err => console.error("Weather poll failed:", err));
}

// Refresh weather immediately, then every 10 minutes
pollWeather();
setInterval(pollWeather, 10 * 60 * 1000);