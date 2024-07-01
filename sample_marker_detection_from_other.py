import cv2
from ar_marker_detection import detect_markers, initialize_camera

def main():
    # カメラの初期化
    cap = initialize_camera()
    if cap is None:
        return

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
        cv2.imshow('AR Marker Detection Sample', frame)
        
        # 'q'キーまたはESCキーで終了
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 27 is the ASCII code for the ESC key
            break

    print("プログラムを終了します。")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()