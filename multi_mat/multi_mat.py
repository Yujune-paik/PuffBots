# multi_mat_position.py

import sys
import os
import asyncio
from toio import *
from toio.simple import SimpleCube
import keyboard
import cv2
import numpy as np
import time
import math

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '../example_simple'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../ar_marker'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

class MultiMatPosition:
    def __init__(self):
        self.mat = [0, 0]
        self.last_grid = [0, 0]

    def multi_mat_pos(self, cube: SimpleCube, update_interval: float = 0.1):
        last_time = time.time()

        while True:
            current_time = time.time()
            if current_time - last_time >= update_interval:
                x = cube.get_x()
                y = cube.get_y()
                grid_x = cube.get_grid_x()
                grid_y = cube.get_grid_y()
                # print("grid_x: ", grid_x, "grid_y: ", grid_y)

                # grid_x の変化を確認
                if self.last_grid[0] >= 3 and grid_x <= 0:
                    self.mat[0] += 1
                elif self.last_grid[0] <= -3 and grid_x >= 0:
                    self.mat[0] -= 1

                # grid_y の変化を確認
                if self.last_grid[1] <= -2 and grid_y >= 0:
                    self.mat[1] += 1
                elif self.last_grid[1] >= 2 and grid_y <= 0:
                    self.mat[1] -= 1

                # グローバル座標の計算
                global_x = x + 152 + self.mat[0] * 304
                global_y = y*(-1) + 108 + self.mat[1] * 216

                # print("global_x: ", global_x, "global_y: ", global_y)
                # print("last_grid_x: ", self.last_grid[0], "last_grid_y: ", self.last_grid[1])

                # last_grid の更新
                self.last_grid[0] = grid_x
                self.last_grid[1] = grid_y

                return global_x, global_y
    
    def get_mat(self):
        return self.mat
    
    def get_last_grid(self):
        return self.last_grid
    
    def angle_between_vectors(self, v1, v2):
        # ベクトルの内積
        dot_product = np.dot(v1, v2)
        # ベクトルのノルム（大きさ）
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        # コサインの値
        cos_theta = dot_product / (norm_v1 * norm_v2)
        # アークコサインで角度（ラジアン）を計算
        theta = np.arccos(cos_theta)
        # ラジアンを度に変換
        theta_deg = np.degrees(theta)
        return theta_deg

    def direction_vector_from_angle(self, angle_deg):
        # 角度（度）をラジアンに変換
        angle_rad = np.radians(angle_deg)
        # 単位ベクトルの計算
        return np.array([np.cos(angle_rad), np.sin(angle_rad)])

    def vector_from_points(self, p1, p2):
        # 二点からベクトルを計算
        return np.array([p2[0] - p1[0], p2[1] - p1[1]])
    
    # multi_mat座標系でいきたい座標(x,y)を入力する
    def toio_move_to(self, cube: SimpleCube, x: int, y: int, speed: int = 50):
        # 角度から方向ベクトルを計算
        angle_deg = cube.get_orientation()
        print("angle_deg: ", angle_deg)
        direction_vector = mmp.direction_vector_from_angle(angle_deg)

        # 二点の座標からベクトルを計算
        point2 = [x - 152, y * (-1) + 108]
        point1 = [cube.get_x(), cube.get_y()]
        vector_from_pts = mmp.vector_from_points(point1, point2)

        # ベクトル間の角度を計算
        angle_between = mmp.angle_between_vectors(direction_vector, vector_from_pts)
        angle_between += 90

        # 0<=angle_between<=90になるように調整
        if angle_between > 90:
            angle_between = angle_between - 180
        elif angle_between < -90:
            angle_between = angle_between + 180

        print("angle_between: ", angle_between)
        cube.set_orientation(30, angle_between)
        # target_mat = x // 304, y // 216
        # print("target_mat_x: ", target_mat[0], "target_mat_y: ", target_mat[1])
        # cube.set_orientation(speed=speed, x=pos[0], y=pos[1])
        

        # matの場所が一致し、stop_x, stop_yの場所が近くなったら（誤差±3）になったら移動を終了
        # while True:
        #     pos = self.multi_mat_pos(cube):

if __name__ == "__main__":
    mmp = MultiMatPosition()
    with SimpleCube() as cube:
        # while True:
            global_position = mmp.multi_mat_pos(cube)
            mmp.toio_move_to(cube, 456, 108)


        

# if __name__ == "__main__":
#     mmp = MultiMatPosition()
#     with SimpleCube() as cube:
#         while True:
#             global_position = mmp.multi_mat_pos(cube)
#             print(global_position)
#             print("mat_x: ", mmp.mat[0], "mat_y: ", mmp.mat[1])

#             # 0.5秒ごとにtoioの座標を出力
#             time.sleep(0.5)
            
#             # qを押すと終了
#             if keyboard.is_pressed('q'):
#                 break

# toio_move_to()の使用例
# if __name__ == "__main__":
#     mmp = MultiMatPosition()
#     with SimpleCube() as cube:
#         asyncio.run(mmp.toio_move_to(cube, 456, 108))
        # while True:
        #     pos = mmp.multi_mat_pos(cube)
        #     mmp.toio_move_to(cube, 456, 108)
            
        #     if keyboard.is_pressed('q'):
        #         break
        # mmp.toio_move_to(cube, 456, 324)

        # mmp.toio_move_to(cube, 152, 108)
        # mmp.toio_move_to(cube, 456, 108)
        # mmp.toio_move_to(cube, 456, 324)
        # mmp.toio_move_to(cube, 152, 324)
        # mmp.toio_move_to(cube, 152, 108)

# if __name__ == "__main__":
#     mmp = MultiMatPosition()
    
#     with SimpleCube() as cube:
#         while True:
#             pos = mmp.multi_mat_pos(cube)
#             if keyboard.is_pressed('enter'):
#                 print("mat_x: ", mmp.mat[0], "mat_y: ", mmp.mat[1])
#                 print("grid_x: ", pos[0], "grid_y: ", pos[1])



            