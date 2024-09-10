import cv2
import matplotlib.pyplot as plt
import numpy as np
import os

square_size = 1.9     # 正方形の1辺のサイズ[cm]
pattern_size = (7, 7)  # 交差ポイントの数

reference_img = 40 # 参照画像の枚数

pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 ) #チェスボード（X,Y,Z）座標の指定 (Z=0)
pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)
pattern_points *= square_size
objpoints = []
imgpoints = []

# ここを変更: USBカメラを指定
capture = cv2.VideoCapture(1)  # 1はUSBカメラを示す。複数のUSBカメラがある場合は2,3...と増やす

while len(objpoints) < reference_img:
    # 画像の取得
    ret, img = capture.read()
    if not ret:
        print("Failed to grab frame")
        break
    
    height = img.shape[0]
    width = img.shape[1]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # チェスボードのコーナーを検出
    ret, corner = cv2.findChessboardCorners(gray, pattern_size)
    # コーナーがあれば
    if ret == True:
        print("detected corner!")
        print(f"{len(objpoints)+1}/{reference_img}")
        term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
        cv2.cornerSubPix(gray, corner, (5,5), (-1,-1), term)
        imgpoints.append(corner.reshape(-1, 2))
        objpoints.append(pattern_points)

    cv2.imshow('image', img)
    # 毎回判定するから 400 ms 待つ．遅延するのはココ
    if cv2.waitKey(400) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()

print("calculating camera parameter...")
# 内部パラメータを計算
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# 計算結果を保存
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    np.save(os.path.join(current_dir, "mtx.npy"), mtx)
    np.save(os.path.join(current_dir, "dist.npy"), dist.ravel())
    print(f"Files saved successfully in {current_dir}")
except Exception as e:
    print(f"Error saving files: {e}")

# 計算結果を表示
print("RMS = ", ret)
print("mtx = \n", mtx)
print("dist = ", dist.ravel())

# ファイルが正しく保存されたか確認
if os.path.exists(os.path.join(current_dir, "mtx.npy")) and os.path.exists(os.path.join(current_dir, "dist.npy")):
    print("Files were successfully saved.")
else:
    print("Files were not saved. Please check your permissions and file paths.")