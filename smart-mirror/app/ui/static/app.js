// Smart Mirror — front-end behavior (JavaScript runs in the BROWSER).
//
// Step 1: switch between views. For now we test with the arrow keys.
// Later, gestures (via the Flask endpoint) will call showView() instead.

// The list of view element ids, in order. To add a screen later, add its id here.
const views = ["view-home", "view-calendar"];

// Which view is currently showing (an index into `views`). Starts at 0 = home.
let current = 0;

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

// --- TEMPORARY test controls: arrow keys switch views ---
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
