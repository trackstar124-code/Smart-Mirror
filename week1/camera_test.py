"""Week 1 deliverable: open your webcam and show the live feed in a window.

Goal: run `python camera_test.py`, see yourself in a window, and press a key
(commonly 'q') to close it cleanly. Throwaway learning script.

Fill in the TODOs yourself. Pointers are given, not answers.
"""

# TODO: import the computer-vision library you installed.
#       (Look up: "opencv python import cv2")


def open_camera():
    """Create and return a handle to the webcam.

    OpenCV represents the camera as a "VideoCapture" object. Index 0 is
    usually your built-in webcam.

    Look up:
      - "cv2.VideoCapture"
      - how to check whether the camera actually opened (.isOpened())

    Returns:
        the VideoCapture object.
    """
    # TODO: create the capture object and return it.
    raise NotImplementedError


def show_feed(capture):
    """Continuously read frames and display them until the user quits.

    The pattern is a loop:
      1. read one frame from the camera
      2. show it in a window
      3. check if the user pressed the quit key; if so, break

    Look up:
      - "cv2 read frame loop" (.read() returns two things — what are they?)
      - "cv2.imshow"
      - "cv2.waitKey" (why is it needed, and how to detect a keypress)

    Args:
        capture: the VideoCapture object from open_camera().
    """
    # TODO: write the capture loop described above.
    raise NotImplementedError


def cleanup(capture):
    """Release the camera and close any OpenCV windows.

    Forgetting this can leave your webcam "locked" until you restart.

    Look up:
      - ".release()" and "cv2.destroyAllWindows()"

    Args:
        capture: the VideoCapture object to release.
    """
    # TODO: release the camera and destroy the windows.
    raise NotImplementedError


def main():
    """Open the camera, show the feed, then clean up."""
    # TODO: call the functions above in order.
    #       Tip: wrap show_feed in try/finally so cleanup always runs.
    raise NotImplementedError


if __name__ == "__main__":
    main()
