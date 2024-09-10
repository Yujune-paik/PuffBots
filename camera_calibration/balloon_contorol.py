import asyncio
import keyboard
from toio import ToioCoreCube
from rotate_cube_relative import rotate_cube_relative

async def move_forward(cube):
    await cube.api.motor.motor_control(50, 50)  # 両モーターを同じ速度で前進

async def stop_movement(cube):
    await cube.api.motor.motor_control(0, 0)  # 両モーターを停止

async def control_cube(cube):
    """
    'l'キーが押されている間、キューブを左に90度回転させてから前進させる。
    'r'キーが押されている間、キューブを右に90度回転させてから前進させる。
    キーが離されたら停止し、元の向きに戻る。
    """
    print("Press and hold 'l' to turn left and move forward")
    print("Press and hold 'r' to turn right and move forward")
    print("Release the key to stop and turn back")
    print("Press 'q' to quit")

    moving = False
    current_direction = None

    while True:
        event = keyboard.read_event(suppress=True)
        
        if event.event_type == keyboard.KEY_DOWN:
            if event.name in ['l', 'r'] and not moving:
                current_direction = event.name
                turn_angle = -90 if current_direction == 'l' else 90
                print(f"Turning {'left' if current_direction == 'l' else 'right'} 90 degrees")
                await rotate_cube_relative(cube, turn_angle)
                moving = True
                print("Moving forward")
                await move_forward(cube)
            elif event.name == 'q':
                print("Quitting...")
                return

        elif event.event_type == keyboard.KEY_UP:
            if event.name in ['l', 'r'] and moving and event.name == current_direction:
                print("Stopping")
                await stop_movement(cube)
                turn_back_angle = 90 if current_direction == 'l' else -90
                print("Turning back 90 degrees")
                await rotate_cube_relative(cube, turn_back_angle)
                moving = False
                current_direction = None

async def main():
    async with ToioCoreCube() as cube:
        print("Connected to cube")
        await control_cube(cube)
        print("Disconnected from cube")

if __name__ == "__main__":
    asyncio.run(main())