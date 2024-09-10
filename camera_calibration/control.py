import asyncio
import keyboard
from toio import *
Speed = 50

async def control_toio():
    async with ToioCoreCube() as cube:
        print("矢印キーでtoioを操作します。Escキーで終了します。")
        while True:
            if keyboard.is_pressed('up'):
                await cube.api.motor.motor_control(Speed, Speed)
            elif keyboard.is_pressed('down'):
                await cube.api.motor.motor_control(-Speed, -Speed)
            elif keyboard.is_pressed('left'):
                await cube.api.motor.motor_control(-Speed, Speed)
            elif keyboard.is_pressed('right'):
                await cube.api.motor.motor_control(Speed, -Speed)
            else:
                await cube.api.motor.motor_control(0, 0)
            
            if keyboard.is_pressed('esc'):
                break
            
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(control_toio())