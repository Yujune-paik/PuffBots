from toio import ToioCoreCube
from move import ToioController
import asyncio

async def your_function():
    async with ToioCoreCube() as cube:
        controller = ToioController(cube)
        
        # 90度回転
        await controller.rotate_to_angle(90)
        
        # (200, 200)の位置に移動
        await controller.move_to_position(200, 200)

asyncio.run(your_function())