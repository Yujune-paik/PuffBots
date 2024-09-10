import asyncio
from toio import *

async def rotate_cube_to_angle(cube, target_angle):
    current_position = None

    def id_notification_handler(payload: bytearray):
        nonlocal current_position
        id_info = IdInformation.is_my_data(payload)
        if isinstance(id_info, PositionId):
            current_position = id_info.center
            print(f"Current position: x={current_position.point.x}, y={current_position.point.y}, angle={current_position.angle}")

    await cube.api.id_information.register_notification_handler(id_notification_handler)

    # 現在の位置を取得するまで待機
    while current_position is None:
        await asyncio.sleep(0.1)

    # 目標角度まで回転
    await cube.api.motor.motor_control_target(
        timeout=5,
        movement_type=MovementType.Linear,
        speed=Speed(max=30, speed_change_type=SpeedChangeType.Constant),
        target=TargetPosition(
            cube_location=CubeLocation(point=current_position.point, angle=target_angle),
            rotation_option=RotationOption.AbsoluteOptimal,
        ),
    )

    # 回転が完了するまで少し待機
    await asyncio.sleep(2)

    # 最終位置を表示
    print(f"Final position: x={current_position.point.x}, y={current_position.point.y}, angle={current_position.angle}")

    await cube.api.id_information.unregister_notification_handler(id_notification_handler)

async def main():
    async with ToioCoreCube() as cube:
        print("Connected to cube")
        target_angle = 270  # 目標角度を90度に設定
        await rotate_cube_to_angle(cube, target_angle%360)
        print("Rotation completed")
        print("Disconnected from cube")

# メイン関数を実行
asyncio.run(main())