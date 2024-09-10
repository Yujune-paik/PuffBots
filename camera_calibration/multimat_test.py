import asyncio
from toio import *
from multimat import MultiMatHandler

async def test_multimat_handler(cube):
    mat_handler = MultiMatHandler(cube)
    await mat_handler.register_notification_handler()

    try:
        # # テスト1: 現在位置の表示
        # print("Test 1: Display current position")
        # for _ in range(5):
        #     x, y, angle = mat_handler.get_current_position()
        #     mat_x, mat_y = mat_handler.get_current_mat()
        #     print(f"Position: x={x}, y={y}, angle={angle}")
        #     print(f"Current mat: ({mat_x}, {mat_y})")
        #     await asyncio.sleep(1)

        # # テスト2: 特定の位置への移動
        # print("\nTest 2: Move to specific position")
        # target_x, target_y = 250, 250
        # print(f"Moving to position: ({target_x}, {target_y})")
        # await mat_handler.move_to_position(target_x, target_y)

        # # テスト3: 特定の角度への回転
        # print("\nTest 3: Rotate to specific angle")
        # target_angle = 90
        # print(f"Rotating to angle: {target_angle}")
        # await mat_handler.rotate_to_angle(target_angle)

        # テスト4: 連続した動き
        print("\nTest 4: Sequence of movements")
        center = (250, 250)
        movements = [
            center,
            (center[0] + mat_handler.mat_width, center[1]),
            (center[0] + mat_handler.mat_width, center[1] + mat_handler.mat_height),
            (center[0], center[1] + mat_handler.mat_height),
            center
        ]
        for i, (x, y) in enumerate(movements, 1):
            print(f"Movement {i}: Moving to ({x}, {y})")
            await mat_handler.move_to_position(x, y)
            await asyncio.sleep(1)

        # # テスト5: 回転のテスト
        # print("\nTest 5: Rotation test")
        # for angle in [0, 90, 180, 270, 0]:
        #     print(f"Rotating to {angle} degrees")
        #     await mat_handler.rotate_to_angle(angle)
        #     await asyncio.sleep(1)

    finally:
        await mat_handler.unregister_notification_handler()

async def main():
    async with ToioCoreCube() as cube:
        print("Connected to cube")
        await test_multimat_handler(cube)
        print("Test completed")

if __name__ == "__main__":
    asyncio.run(main())