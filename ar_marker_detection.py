import cv2
import numpy as np

def detect_markers(frame):
    # グレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # ArUcoディクショナリを定義
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    
    # ArUcoDetectorを作成
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    
    # マーカーを検出
    corners, ids, rejected = detector.detectMarkers(gray)
    
    detected_markers = []
    
    if len(corners) > 0:
        ids = ids.flatten()
        # 検出されたマーカーごとに処理
        for i, corner in enumerate(corners):
            # マーカーの角の座標を取得
            c = corner.reshape((4, 2))
            
            # マーカーの中心座標を計算
            center = np.mean(c, axis=0).astype(int)
            x, y = center
            
            # マーカーの向きを計算（簡易的な方法）
            direction = c[1] - c[0]
            angle = np.arctan2(direction[1], direction[0]) * 180 / np.pi
            
            # 結果を描画
            cv2.polylines(frame, [c.astype(int)], True, (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {ids[i]}", (x, y - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, f"X: {x}, Y: {y}", (x, y + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, f"Angle: {angle:.2f}", (x, y + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            detected_markers.append({
                'id': ids[i],
                'position': (x, y),
                'angle': angle
            })
    
    return frame, detected_markers

def run_ar_detection():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # マーカー検出と描画
        frame, markers = detect_markers(frame)
        
        # 検出されたマーカーの情報を表示
        for marker in markers:
            print(f"Marker ID: {marker['id']}")
            print(f"Position: X={marker['position'][0]}, Y={marker['position'][1]}")
            print(f"Angle: {marker['angle']:.2f} degrees")
            print("---")
        
        # 結果を表示
        cv2.imshow('AR Marker Detection', frame)
        
        # 'q'キーまたはESCキーで終了
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 27 is the ASCII code for the ESC key
            break

    print("プログラムを終了します。")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_ar_detection()