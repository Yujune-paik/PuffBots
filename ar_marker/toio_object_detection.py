import sys
import os
# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '../example_simple'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../ar_marker'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import asyncio
from toio import *
from toio.simple import SimpleCube
import toio_information
import ar_marker_detection
import keyboard
import cv2
import numpy as np


async def get_ar_corners():
    corner_positions_ar = []

    camera_index = ar_marker_detection.select_camera()
    if camera_index is None:
        print("カメラが選択されませんでした。プログラムを終了します。")
        return

    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
    cv2.namedWindow('AR Marker Detection', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('AR Marker Detection', 1600, 1200)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("フレームの読み取りに失敗しました。")
            break

        if frame is None:
            print("フレームが None です。")
            continue
        
        # マーカー検出と描画
        frame, markers = ar_marker_detection.detect_markers(frame)

        # フレーム表示
        cv2.imshow('AR Marker Detection', frame)

        if keyboard.is_pressed('enter') and len(corner_positions_ar) < 4:
            # マーカーの中心位置を取得
            if markers:
                position = markers[0]['position']
                # 一般的な座標の形に変換して保存
                corner_positions_ar.append((int(position[0]), int(position[1])))  # 実際の位置
                print(f"Position {len(corner_positions_ar)} saved.")
                
                # 画面を一瞬白くする
                white_frame = 255 * np.ones_like(frame)
                cv2.imshow('AR Marker Detection', white_frame)
                cv2.waitKey(100)  # 100ミリ秒間白い画面を表示

                while keyboard.is_pressed('enter'):
                    await asyncio.sleep(0.1)  # エンターキーが放されるのを待つ

        if len(corner_positions_ar) == 4:
            print("4つの位置が保存されました。")
            break
            
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    print("プログラムを終了します。")
    cap.release()
    cv2.destroyAllWindows()
    
    print(corner_positions_ar)

# toioの4つ角を取得する関数
async def get_toio_corners():
    corner_positions = []
    with SimpleCube() as cube:
        while True:
            if keyboard.is_pressed('enter') and len(corner_positions) < 4:
                position = cube.get_current_position()
                corner_positions.append(position)
                print(f"Position {len(corner_positions)} saved.")
                
                while keyboard.is_pressed('enter'):
                    await asyncio.sleep(0.1)  # エンターキーが放されるのを待つ

            if len(corner_positions) == 4:
                print("4つの位置が保存されました。")
                break

    print("プログラムを終了します。")
    print(corner_positions)

if __name__ == "__main__":
    asyncio.run(get_ar_corners())
