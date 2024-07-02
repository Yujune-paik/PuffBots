import asyncio
from toio import *
from toio_information import toio_list

# 番号からIDを取得する関数
def get_toio_id_by_number(toio_number):
    for toio in toio_list:
        if toio["number"] == toio_number:
            return toio["name"]
    return None

# 番号でToioを接続し命令を出す関数
async def scan_and_connect(toio_number):
    toio_id = get_toio_id_by_number(toio_number)
    if not toio_id:
        print(f"No Toio with number {toio_number} found.")
        return

    dev_list = await BLEScanner.scan_with_id(cube_id={toio_id})
    if not dev_list:
        print(f"No Toio with ID {toio_id} found.")
        return

    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()
    print(f"Connected to Toio with number {toio_number} and ID {toio_id}")

    await asyncio.sleep(3)

    await cube.disconnect()
    print(f"Disconnected from Toio with number {toio_number} and ID {toio_id}")
    return 0


# キューブをその場で2秒間回転させるために使用する関数
async def motor_1():
    async with ToioCoreCube() as cube:
        # go
        await cube.api.motor.motor_control(10, -10)
        await asyncio.sleep(2)
        # stop
        await cube.api.motor.motor_control(0, 0)

    return 0

# キューブをマット上の指定された位置に移動するために使用する関数
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

# キューブを複数のマット上の指定された位置に移動するために使用する関数
async def motor_3():
    async with ToioCoreCube() as cube:
        targets = [
            TargetPosition(
                cube_location=CubeLocation(point=Point(x=250, y=250), angle=0), rotation_option=RotationOption.AbsoluteOptimal
            ),
            TargetPosition(
                cube_location=CubeLocation(point=Point(x=120, y=170), angle=0), rotation_option=RotationOption.AbsoluteOptimal
            ),
        ]
        await cube.api.motor.motor_control_multiple_targets(
            timeout=5,
            movement_type=MovementType.Linear,
            speed=Speed(
                max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration),
            mode=WriteMode.Overwrite,
            target_list=targets,
        )
        await asyncio.sleep(5)

if __name__ == "__main__":
    # asyncio.run(motor_1())
    # asyncio.run(motor_2())
    asyncio.run(motor_3())
    # asyncio.run(scan_and_connect(2))