import asyncio

from toio import *

async def motor_1():
    async with ToioCoreCube() as cube:
        # go
        await cube.api.motor.motor_control(10, -10)
        await asyncio.sleep(2)
        # stop
        await cube.api.motor.motor_control(0, 0)

        await cube.disconnect()
    return 0

if __name__ == "__main__":
    asyncio.run(motor_1())