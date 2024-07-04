import cv2
import numpy as np

def detect_markers(frame):
    # グレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # ArUcoディクショナリを4x4に変更
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
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
            
            # 角度を0 <= 角度 < 360の範囲に調整
            angle = (angle + 360) % 360
            
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

def list_cameras():
    """利用可能なカメラをリストアップする"""
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr

def select_camera():
    """ユーザーにカメラを選択させる"""
    available_cameras = list_cameras()
    if not available_cameras:
        print("利用可能なカメラが見つかりません。")
        return None
    
    print("利用可能なカメラ:")
    for i, cam in enumerate(available_cameras):
        print(f"{i}: カメラ {cam}")
    
    while True:
        choice = input("使用するカメラの番号を入力してください: ")
        try:
            index = int(choice)
            if 0 <= index < len(available_cameras):
                return available_cameras[index]
            else:
                print("無効な選択です。もう一度お試しください。")
        except ValueError:
            print("数字を入力してください。")

def initialize_camera():
    camera_index = select_camera()
    if camera_index is None:
        print("カメラが選択されませんでした。")
        return None
    return cv2.VideoCapture(camera_index)

def run_ar_detection():
    camera_index = select_camera()
    if camera_index is None:
        print("カメラが選択されませんでした。プログラムを終了します。")
        return

    cap = cv2.VideoCapture(camera_index)

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