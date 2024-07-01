import asyncio

from toio import *

async def scan_and_connect():
    cube = ToioCoreCube()
    await cube.scan()
    await cube.connect()

    await asyncio.sleep(3)

    await cube.disconnect()
    return 0

# 通知ハンドラ
def notification_handler(payload: bytearray):
    id_info = IdInformation.is_my_data(payload)
    print(str(id_info))



async def motor_2():
    async with ToioCoreCube() as cube:
        await cube.api.motor.register_notification_handler(notification_handler)
        await cube.api.motor.motor_control_target(
            timeout=5,
            movement_type=MovementType.Linear,
            speed=Speed(
                max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration),
            target=TargetPosition(
                cube_location=CubeLocation(point=Point(x=200, y=200), angle=0),
                rotation_option=RotationOption.AbsoluteOptimal,
            ),
        )

        await asyncio.sleep(4)

if __name__ == "__main__":
    asyncio.run(motor_2())
    # asyncio.run(scan_and_connect())