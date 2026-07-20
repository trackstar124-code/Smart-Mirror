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
def distance(a, b):
    """Distance formula"""
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5

def detect_gesture(hand):
    """Checks for a fist and open palm and prints OPEN PALM when there is an open palm and FIST when there is a fist Now 
    returns OK when the OK sign is made"""
    pinch = distance(hand.landmark[4], hand.landmark[8]) < 0.05
    middle_up = hand.landmark[12].y < hand.landmark[10].y
    ring_up   = hand.landmark[16].y < hand.landmark[14].y
    pinky_up  = hand.landmark[20].y < hand.landmark[18].y
    fingers_up = 0
    if hand.landmark[8].y < hand.landmark[6].y:
        fingers_up += 1
    if hand.landmark[12].y < hand.landmark[10].y:
        fingers_up += 1
    if hand.landmark[16].y < hand.landmark[14].y:
        fingers_up += 1
    if hand.landmark[20].y < hand.landmark[18].y:
        fingers_up += 1
    """Below is the OK hand gesture detection"""
    if pinch and middle_up and ring_up and pinky_up:
        return "OK"

    if fingers_up == 4:
        return "OPEN_PALM"
    elif fingers_up == 0:
        return "FIST"
    else:
        return "UNKNOWN"

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
                gesture = detect_gesture(hand)   # figure out palm / fist
                print(gesture)                   # Week 3 deliverable: print it live

        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
