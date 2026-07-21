import cv2
import mediapipe as mp
from pathlib import Path

# --- MediaPipe setup (same boilerplate as week3) ---
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# The shared file, built relative to THIS file so both programs agree on it.
STATE_FILE = Path(__file__).parent / "gesture_state.txt"


def write_gesture(gesture):
    """Changes the STATE_FILE to what ever gesture is being displayed"""
    with open(STATE_FILE, "w") as f:
        f.write(gesture)


def read_gesture():
    """This Read the text in the STATE_FILE"""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return f.read()
    else:
        return "UNKNOWN"


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


def run():
    """Camera loop: detect the gesture each frame, write it ONLY when it changes."""
    cap = cv2.VideoCapture(0)
    last_gesture = None          # remember the previous gesture (state across frames)
    prev_x = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                wrist_x = hand.landmark[0].x
                gesture = detect_gesture(hand)                  
                if prev_x is not None:
                    dx = wrist_x - prev_x
                    if dx > 0.1:
                        write_gesture("Swipe Right")
                    elif dx < -0.1:
                        write_gesture("Swipe Left")
                prev_x = wrist_x

                if gesture != last_gesture:
                    write_gesture(gesture)
                    last_gesture = gesture

        cv2.imshow("Gestures", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()


 
                