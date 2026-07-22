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
        switch(data.gesture) {
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