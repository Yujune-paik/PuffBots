import asyncio
import math
from toio import *

async def get_current_position(cube):
    position_info = await cube.api.id_information.read()
    if isinstance(position_info, PositionId):
        return position_info.center
    return None

async def stop(cube):
    await cube.api.motor.motor_control(0, 0, 0)

async def move(cube, speed, duration):
    await cube.api.motor.motor_control(speed, speed, duration)

async def rotate(cube, speed, duration, clockwise=True):
    if clockwise:
        await cube.api.motor.motor_control(speed, -speed, duration)
    else:
        await cube.api.motor.motor_control(-speed, speed, duration)

async def rotate_to_angle(cube, target_angle, target_tolerance=5):
    while True:
        current_position = await get_current_position(cube)
        if current_position is None:
            await asyncio.sleep(0.1)
            continue

        current_angle = current_position.angle
        angle_diff = (target_angle - current_angle + 360) % 360

        print(f"Current angle: {current_angle}, Target angle: {target_angle}, Difference: {angle_diff}")

        if angle_diff < target_tolerance or angle_diff > 360 - target_tolerance:  # Close enough to target angle
            await cube.api.motor.motor_control(0, 0, 0)
            print("Reached target angle")
            break
        elif angle_diff <= 180:
            await cube.api.motor.motor_control(30, -30, 50)  # 時計回り
        else:
            await cube.api.motor.motor_control(-30, 30, 50)  # 反時計回り
        
        await asyncio.sleep(0.1)  # 短い待機時間を入れて、連続的な命令送信を防ぐ

async def move_to_position(cube, target_x, target_y, target_tolerance=5):
    while True:
        pos_current = await get_current_position(cube)
        if pos_current is None:
            await asyncio.sleep(0.1)
            continue

        x_diff = target_x - pos_current.point.x
        y_diff = target_y - pos_current.point.y
        distance = math.sqrt(x_diff ** 2 + y_diff ** 2)

        print(f"Current position: ({pos_current.point.x}, {pos_current.point.y}), Target position: ({target_x}, {target_y}), Distance: {distance}")

        if distance < target_tolerance:
            await stop(cube)
            print("Reached target position")
            break
        else:
            angle = math.degrees(math.atan2(y_diff, x_diff))
            await rotate_to_angle(cube, angle, 10)
            await move(cube, 30, 50)

async def main():
    async with ToioCoreCube() as cube:
        print("Starting movement")
        await move_to_position(cube, 250, 250)
        print("Movement completed")

asyncio.run(main())