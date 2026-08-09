import cv2
import mediapipe as mp
import time
import serial

py_serial = serial.Serial(
    port='COM4', # Window    
    baudrate=9600, # 보드 레이트 (통신 속도)
)
      

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode = False,
    max_num_hands = 2,
    min_detection_confidence = 0.7,
    min_tracking_confidence = 0.7
)

WIDTH = 480
HEIGHT = 640

ptime = 0

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    ctime = time.time()
    fps = 1 / (ctime - ptime)
    ptime = ctime

    cv2.putText(frame, f'FPS: {int(fps)}', (10,30), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0),3)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results= hands.process(rgb)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            finger_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
            thumb_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x

            finger_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
            thumb_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y

            label = handedness.classification[0].label  # 'Left' 또는 'Right'
            score = handedness.classification[0].score  # 신뢰도

            x = int(hand_landmarks.landmark[0].x * frame.shape[1])
            y = int(hand_landmarks.landmark[0].y * frame.shape[0])

            cv2.putText(frame, f'{label} ({score:.2f})', (x, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            
            finger_point = (int(finger_x * HEIGHT),int(finger_y * WIDTH))
            thumb_point = (int(thumb_x * HEIGHT),int(thumb_y * WIDTH))

            cv2.circle(frame, finger_point, 8, (0,255,0), -1, cv2.LINE_AA)
            cv2.circle(frame, thumb_point, 8, (0,255,0), -1, cv2.LINE_AA)

            cv2.line(frame, finger_point, thumb_point, (255,255,0), 6, cv2.LINE_AA)

            print(finger_point, thumb_point)
            command = abs(int(finger_x * HEIGHT) - int(thumb_x * HEIGHT))
            x_pos = abs(finger_x - thumb_x) * HEIGHT / 2 + (thumb_x * HEIGHT) if finger_x > thumb_x else abs(finger_x - thumb_x) * HEIGHT / 2 + (finger_x * HEIGHT)
            y_pos = abs(finger_y - thumb_y) * WIDTH / 2 + (thumb_y * WIDTH) if finger_y > thumb_y else abs(finger_y - thumb_y) * WIDTH / 2 + (finger_y * WIDTH)

            cv2.putText(frame, f'X_length: {command}',  (int(x_pos)+10, int(y_pos)-10) , cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                     
            value = str(int(command))
            py_serial.write(f"{value}\n".encode()) # 문자열 끝을 알려주는 \n을 붙여야 아두이노쪽 Serial.parseInt()에서 병목현상이 없어짐 -> 추가 입력이나 타임아웃을 기다림.

            print(value)
            print(value.encode())
        
    cv2.imshow("MediaPipe Hands", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()