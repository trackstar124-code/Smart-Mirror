"""Smart Mirror web app (Week 2).

Serves a fullscreen dashboard (time, date, weather) to the browser.

How to run:
    python smart-mirror/app/main.py
Then open http://localhost:8000 in your browser.

Fill in the TODOs yourself. Pointers are given, not answers.
"""
from flask import Flask, render_template

# Create the Flask application.
#   __name__            -> tells Flask where this app lives (standard boilerplate)
#   template_folder     -> where your HTML files live (relative to THIS file)
#   static_folder       -> where CSS / JS / images live
app = Flask(
    __name__,
    template_folder="ui/templates",
    static_folder="ui/static",
)


@app.route("/")
def index():
    return "Hello, Mirror"
    """Serve the main dashboard page.

    A "route" means: when a browser visits "/" (the home URL), Flask runs this
    function and sends back whatever you return.

    Build this in two steps:
      1. FIRST TEST: return a simple string like "Hello, Mirror!" and confirm it
         shows up at http://localhost:5000. This proves Flask is working.
      2. THEN upgrade to serving your HTML file:
             return render_template("index.html")
         (render_template looks in your template_folder for the file.)

    Returns:
        str: the text or HTML to display in the browser.
    """
    # TODO: step 1 -> return a simple "Hello" string to confirm Flask runs.
    #       step 2 -> switch to render_template("index.html").


if __name__ == "__main__":
    # debug=True auto-reloads the server whenever you save a change,
    # and shows helpful error pages in the browser while you're learning.
    app.run(host="0.0.0.0", port=8000, debug=True)
