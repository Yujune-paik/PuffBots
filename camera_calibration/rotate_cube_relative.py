import asyncio
from toio import *

async def rotate_cube_relative(cube, relative_angle):
    current_position = None
    start_angle = None

    def id_notification_handler(payload: bytearray):
        nonlocal current_position, start_angle
        id_info = IdInformation.is_my_data(payload)
        if isinstance(id_info, PositionId):
            current_position = id_info.center
            if start_angle is None:
                start_angle = current_position.angle
            # print(f"Current position: x={current_position.point.x}, y={current_position.point.y}, angle={current_position.angle}")

    await cube.api.id_information.register_notification_handler(id_notification_handler)

    # 現在の位置を取得するまで待機
    while current_position is None or start_angle is None:
        await asyncio.sleep(0.1)

    # 目標角度を計算（0-359の範囲内に収める）
    target_angle = (start_angle + relative_angle) % 360

    print(f"Starting angle: {start_angle}")
    print(f"Target angle: {target_angle}")

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
        relative_angle = 180  # 90度回転させる
        await rotate_cube_relative(cube, relative_angle)
        print("Rotation completed")
        
        await asyncio.sleep(2)  # 2秒待機
        
        # relative_angle = -45  # -45度（反時計回りに45度）回転させる
        # await rotate_cube_relative(cube, relative_angle)
        # print("Second rotation completed")
        
        # print("Disconnected from cube")

# メイン関数を実行
if __name__ == "__main__":
    asyncio.run(main())