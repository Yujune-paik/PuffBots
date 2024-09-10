import cv2
import numpy as np
import os

# ArUcoマーカー辞書の定義（4x4マーカー、50個）
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

# マーカーのサイズを定義（ピクセル単位）
marker_size = 200

# 保存先フォルダの作成
save_folder = "ar_marker_4x4"
os.makedirs(save_folder, exist_ok=True)

# 0から49までのマーカーを生成して保存
for marker_id in range(50):
    # マーカーの生成
    marker_image = np.zeros((marker_size, marker_size), dtype=np.uint8)
    marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size, marker_image, 1)
    
    # ファイル名の生成
    filename = f"aruco_4x4_marker_{marker_id:02d}.png"
    
    # マーカーの保存（フォルダ内に）
    save_path = os.path.join(save_folder, filename)
    cv2.imwrite(save_path, marker_image)
    
    print(f"Saved marker {marker_id} as {save_path}")

print("All markers have been generated and saved in the 'ar_marker_4x4' folder.")