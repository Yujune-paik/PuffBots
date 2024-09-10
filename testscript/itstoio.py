import signal
from toio.simple import SimpleCube
# 他のディレクトリから関数をインポートするために sys.path を変更
import sys
import os

# example_simple ディレクトリへのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '../example_simple'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../ar_marker'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
import toio_information

LOOP = True


def ctrl_c_handler(_signum, _frame):
    global LOOP
    print("Ctrl-C")
    LOOP = False


signal.signal(signal.SIGINT, ctrl_c_handler)

# 指定した toio に接続して、その toioに命令を出す
def test():
    targets = ((30, 30), (30, -30), (-30, -30), (-30, 30), (30, 30))

    with SimpleCube(toio_information.get_toio_name(2)) as cube:
        print("name:", cube.get_cube_name())
        while LOOP:
            pos = cube.get_current_position()
            orientation = cube.get_orientation()
            print("POSITION:", pos, orientation)
            cube.sleep(0.5)

    with SimpleCube(toio_information.get_toio_name(3)) as cube:
        print("name:", cube.get_cube_name())
        while LOOP:
            print("** CONNECTED")
        for target in targets:
            target_pos_x, target_pos_y = target
            print(f"move to ({target_pos_x}, {target_pos_y})")
            success = cube.move_to(speed=70, x=target_pos_x, y=target_pos_y)
            print(f"arrival: {success}")
            if not success:
                print("Position ID missed")
                break
            cube.sleep(0.5)
    print("** DISCONNECTED")
    print("** END")


if __name__ == "__main__":
    sys.exit(test())