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

# 十字キーでtoioを操作する関数
def control_toio():
    print("** ACTIVATE")
    with SimpleCube() as cube:
        print("** CONNECTED")
        print("CUBE NAME:", cube.get_cube_name())

        while True:
            pos = cube.get_current_position()
            x = cube.get_x()
            y = cube.get_y()
            orientation = cube.get_orientation()

            grid = cube.get_grid()
            grid_x = cube.get_grid_x()
            grid_y = cube.get_grid_y()

            battery_level = cube.get_battery_level()

            button_state = cube.is_button_pressed()

            # print(
            #     "POSITION:",
            #     pos,
            #     x,
            #     y,
            #     orientation,
            #     "GRID:",
            #     grid,
            #     grid_x,
            #     grid_y,
            #     "BATTERY",
            #     battery_level,
            #     "BUTTON",
            #     button_state,
            # )

            #　キーボードの矢印キー（上）が押されたら前進
            if keyboard.read_key() == "up":
                cube.move(30, 1)
            # キーボードの矢印キー（下）が押されたら後退
            if keyboard.read_key() == "down":
                cube.move(-30, 1)
            # キーボードの矢印キー（右）が押されたら右回転
            if keyboard.read_key() == "right":
                cube.spin(30, 1)
            # キーボードの矢印キー（左）が押されたら左回転
            if keyboard.read_key() == "left":
                cube.spin(-30, 1)
            
            # キーボードのqが入力されたら終了
            if keyboard.read_key() == "q":
                break


if __name__ == "__main__":
    control_toio()