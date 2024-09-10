# 他のスクリプトからの使用例

from multi_mat import MultiMatPosition
from toio.simple import SimpleCube
import time
import keyboard

mmp = MultiMatPosition()

with SimpleCube() as cube:
    while True:
        global_position = mmp.multi_mat_pos(cube)
        print(global_position)
        print("mat_x: ", mmp.mat[0], "mat_y: ", mmp.mat[1])

        # 0.5秒ごとにtoioの座標を出力
        time.sleep(0.5)
        
        # qを押すと終了
        if keyboard.is_pressed('q'):
            break
