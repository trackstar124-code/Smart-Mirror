import cv2

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
    """Function to cleanup after the camera runs and destorys window"""
    capture.release()
    cv2.destroyAllWindows()


def main():
    """Open the camera, show the feed, then clean up."""
    cap = open_camera()
    if cap is None:
        return
    print("Camera opened successfully")
    try:
        show_feed(cap)
    finally:
        cleanup(cap)


if __name__ == "__main__":
    main()
