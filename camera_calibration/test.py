import asyncio
import keyboard
from toio import *
import math

def notification_handler(payload: bytearray):
    id_info = IdInformation.is_my_data(payload)
    print(f"Notification received: {str(id_info)}")

def calculate_forward_position(x, y, angle, distance):
    angle_rad = math.radians(angle)
    dx = distance * math.cos(angle_rad)
    dy = distance * math.sin(angle_rad)
    new_x = x + dx
    new_y = y + dy
    return int(new_x), int(new_y)

async def move_toio(cube, x, y, angle):
    print(f"Moving toio to position: ({x}, {y}, {angle}°)")
    try:
        await cube.api.motor.motor_control_target(
            timeout=5,
            movement_type=MovementType.Linear,
            speed=Speed(
                max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration
            ),
            target=TargetPosition(
                cube_location=CubeLocation(point=Point(x=x, y=y), angle=angle),
                rotation_option=RotationOption.AbsoluteOptimal,
            ),
        )
        print("Movement command sent successfully")
    except Exception as e:
        print(f"Error moving toio: {e}")

async def control_toio():
    async with ToioCoreCube() as cube:
        await cube.api.motor.register_notification_handler(notification_handler)
        print("矢印キーでtoioを操作します。Escキーで終了します。")
        
        current_x, current_y = 200, 200  # 初期位置
        current_angle = 0  # 初期角度
        
        while True:
            if keyboard.is_pressed('up'):
                new_x, new_y = calculate_forward_position(current_x, current_y, current_angle, 30)
                await move_toio(cube, new_x, new_y, current_angle)
                current_x, current_y = new_x, new_y
                await asyncio.sleep(0.5)
                
                if not keyboard.is_pressed('up'):
                    back_x, back_y = calculate_forward_position(current_x, current_y, current_angle, -30)
                    await move_toio(cube, back_x, back_y, current_angle)
                    current_x, current_y = back_x, back_y
            
            elif keyboard.is_pressed('down'):
                back_x, back_y = calculate_forward_position(current_x, current_y, current_angle, -100)
                await move_toio(cube, back_x, back_y, current_angle)
                current_x, current_y = back_x, back_y
            
            elif keyboard.is_pressed('left'):
                turn_angle = (current_angle - 90) % 360
                await move_toio(cube, current_x, current_y, turn_angle)
                current_angle = turn_angle
                
                while keyboard.is_pressed('left'):
                    new_x, new_y = calculate_forward_position(current_x, current_y, current_angle, 30)
                    await move_toio(cube, new_x, new_y, current_angle)
                    current_x, current_y = new_x, new_y
                    await asyncio.sleep(0.5)
                
                back_x, back_y = calculate_forward_position(current_x, current_y, current_angle, -30)
                await move_toio(cube, back_x, back_y, current_angle)
                current_x, current_y = back_x, back_y
                
                turn_back_angle = (current_angle + 90) % 360
                await move_toio(cube, current_x, current_y, turn_back_angle)
                current_angle = turn_back_angle
            
            elif keyboard.is_pressed('right'):
                turn_angle = (current_angle + 90) % 360
                await move_toio(cube, current_x, current_y, turn_angle)
                current_angle = turn_angle
                
                while keyboard.is_pressed('right'):
                    new_x, new_y = calculate_forward_position(current_x, current_y, current_angle, 30)
                    await move_toio(cube, new_x, new_y, current_angle)
                    current_x, current_y = new_x, new_y
                    await asyncio.sleep(0.5)
                
                back_x, back_y = calculate_forward_position(current_x, current_y, current_angle, -30)
                await move_toio(cube, back_x, back_y, current_angle)
                current_x, current_y = back_x, back_y
                
                turn_back_angle = (current_angle - 90) % 360
                await move_toio(cube, current_x, current_y, turn_back_angle)
                current_angle = turn_back_angle
            
            if keyboard.is_pressed('esc'):
                break
            
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(control_toio())