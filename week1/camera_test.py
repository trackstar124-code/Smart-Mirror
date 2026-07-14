import cv2
"""Week 1 deliverable: open your webcam and show the live feed in a window.

Goal: run `python camera_test.py`, see yourself in a window, and press a key
(commonly 'q') to close it cleanly. Throwaway learning script.

Fill in the TODOs yourself. Pointers are given, not answers.
"""

# TODO: import the computer-vision library you installed.
#       (Look up: "opencv python import cv2")


def open_camera():
    """This Function open camera"""
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: could not open camera")
        return None
    return cap


def show_feed(capture):
    """This function shows the feed for the camera"""
    while True:
        ret, frame = capture.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow('Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


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
    cap = open_camera()
    if cap is None:
        return
    print("Camera opened successfully")
    try:
        show_feed(cap)
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
