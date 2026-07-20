import cv2
import mediapipe as mp

# --- MediaPipe setup (boilerplate — provided, since the API is hard to guess) ---
mp_hands = mp.solutions.hands          # the Hands solution
mp_draw = mp.solutions.drawing_utils   # helper to draw landmarks on a frame

# The Hands object does the actual detection. These settings are fine to start.
hands = mp_hands.Hands(
    max_num_hands=1,               # track one hand for now
    min_detection_confidence=0.7,
)

def main():
    """Takes the video capture and makes it so that the video has hand tracking"""
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # MediaPipe expects RGB, but OpenCV gives BGR — so we convert.
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Run detection on this frame. `results` holds any hands MediaPipe found.
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
