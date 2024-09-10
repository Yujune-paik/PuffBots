import asyncio
from toio import ToioCoreCube, IdInformation, Speed, SpeedChangeType, MovementType, TargetPosition, CubeLocation, Point, RotationOption

# マット1（初期マット）の左上と右下の座標
MAT1_TOP_LEFT = (98, 142)
MAT1_BOTTOM_RIGHT = (402, 358)

# マットのサイズ
MAT_WIDTH = MAT1_BOTTOM_RIGHT[0] - MAT1_TOP_LEFT[0]
MAT_HEIGHT = MAT1_BOTTOM_RIGHT[1] - MAT1_TOP_LEFT[1]

def multimat_to_absolute(multimat_x, multimat_y):
    mat_x = (multimat_x - MAT1_TOP_LEFT[0]) // MAT_WIDTH
    mat_y = (multimat_y - MAT1_TOP_LEFT[1]) // MAT_HEIGHT
    
    absolute_x = multimat_x - mat_x * MAT_WIDTH
    absolute_y = multimat_y - mat_y * MAT_HEIGHT
    
    return absolute_x, absolute_y

async def get_current_position(cube):
    pos = await cube.api.id_information.read()
    if pos and hasattr(pos, 'center'):
        return pos.center.point.x, pos.center.point.y
    return None

async def move_to_multimat_position(cube, target_x, target_y):
    absolute_x, absolute_y = multimat_to_absolute(target_x, target_y)
    print(f"Moving to multimat position ({target_x}, {target_y}), absolute position ({absolute_x}, {absolute_y})")
    
    try:
        await cube.api.motor.motor_control_target(
            timeout=10,
            movement_type=MovementType.Linear,
            speed=Speed(
                max=50, speed_change_type=SpeedChangeType.AccelerationAndDeceleration),
            target=TargetPosition(
                cube_location=CubeLocation(point=Point(x=absolute_x, y=absolute_y), angle=0),
                rotation_option=RotationOption.AbsoluteOptimal,
            ),
        )
        await asyncio.sleep(5)  # 移動完了を待つ
        
        # 現在の位置を取得して表示
        current_pos = await get_current_position(cube)
        if current_pos:
            print(f"Current position after movement: {current_pos}")
        else:
            print("Failed to get current position")
    except asyncio.CancelledError:
        print("Movement cancelled")
    except Exception as e:
        print(f"Error during movement: {e}")

async def main():
    async with ToioCoreCube() as cube:
        # マルチマット座標での移動テスト
        positions = [(250, 250), (554, 250), (554, 466), (250, 466)]
        for i, (x, y) in enumerate(positions, 1):
            print(f"Moving to mat {i} center")
            await move_to_multimat_position(cube, x, y)
            await asyncio.sleep(2)  # 各移動後に少し待機

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"An error occurred: {e}")