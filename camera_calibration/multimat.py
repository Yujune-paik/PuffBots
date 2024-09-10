import asyncio
import math
from toio import *

# グローバル変数として mat_info を定義
mat_info = ((98, 142), (402, 142), (402, 358), (98, 358))

class MultiMatHandler:
    def __init__(self, cube):
        self.cube = cube
        self.mat_tl, self.mat_tr, self.mat_br, self.mat_bl = mat_info
        self.mat_width = self.mat_tr[0] - self.mat_tl[0]
        self.mat_height = self.mat_bl[1] - self.mat_tl[1]
        self.mat_x = 0
        self.mat_y = 0
        self.last_x = (self.mat_tl[0] + self.mat_tr[0]) // 2
        self.last_y = (self.mat_tl[1] + self.mat_bl[1]) // 2
        self.x = 0
        self.y = 0
        self.angle = 0
        self.notification_handler = None

    def update_position(self, raw_x, raw_y, angle):
        if self.last_x > self.mat_tr[0] - 20 and raw_x < self.mat_tl[0] + 20:
            self.mat_x += 1
        elif raw_x > self.mat_tr[0] - 20 and self.last_x < self.mat_tl[0] + 20:
            self.mat_x -= 1
        
        if self.last_y > self.mat_bl[1] - 20 and raw_y < self.mat_tl[1] + 20:
            self.mat_y += 1
        elif raw_y > self.mat_bl[1] - 20 and self.last_y < self.mat_tl[1] + 20:
            self.mat_y -= 1

        self.mat_x = max(0, self.mat_x)
        self.mat_y = max(0, self.mat_y)

        self.last_x = raw_x
        self.last_y = raw_y

        self.x = raw_x + self.mat_x * self.mat_width
        self.y = raw_y + self.mat_y * self.mat_height
        self.angle = angle

        return self.x, self.y, self.angle

    def get_current_position(self):
        return self.x, self.y, self.angle

    def get_current_mat(self):
        return self.mat_x, self.mat_y

    async def register_notification_handler(self):
        def id_notification_handler(payload: bytearray):
            id_info = IdInformation.is_my_data(payload)
            if isinstance(id_info, PositionId):
                raw_x = id_info.center.point.x
                raw_y = id_info.center.point.y
                angle = id_info.center.angle

                self.update_position(raw_x, raw_y, angle)

        self.notification_handler = id_notification_handler
        await self.cube.api.id_information.register_notification_handler(self.notification_handler)

    async def unregister_notification_handler(self):
        if self.notification_handler:
            await self.cube.api.id_information.unregister_notification_handler(self.notification_handler)
            self.notification_handler = None

    async def stop(self):
        await self.cube.api.motor.motor_control(0, 0, 0)

    async def move(self, speed, duration):
        await self.cube.api.motor.motor_control(speed, speed, duration)

    async def rotate(self, speed, duration, clockwise=True):
        if clockwise:
            await self.cube.api.motor.motor_control(speed, -speed, duration)
        else:
            await self.cube.api.motor.motor_control(-speed, speed, duration)

    async def rotate_to_angle(self, target_angle, target_tolerance=5):
        while True:
            current_x, current_y, current_angle = self.get_current_position()
            angle_diff = (target_angle - current_angle + 360) % 360

            print(f"Current angle: {current_angle}, Target angle: {target_angle}, Difference: {angle_diff}")

            if angle_diff < target_tolerance or angle_diff > 360 - target_tolerance:  # Close enough to target angle
                await self.stop()
                print("Reached target angle")
                break
            elif angle_diff <= 180:
                await self.rotate(60, 50, clockwise=True)  # 時計回り
            else:
                await self.rotate(-60, 50, clockwise=False)  # 反時計回り
            
            await asyncio.sleep(0.1)  # 短い待機時間を入れて、連続的な命令送信を防ぐ

    async def move_to_position(self, target_x, target_y, target_tolerance=5):
        while True:
            current_x, current_y, current_angle = self.get_current_position()
            x_diff = target_x - current_x
            y_diff = target_y - current_y
            distance = math.sqrt(x_diff ** 2 + y_diff ** 2)

            print(f"Current position: ({current_x}, {current_y}), Target position: ({target_x}, {target_y}), Distance: {distance}")

            if distance < target_tolerance:
                await self.stop()
                print("Reached target position")
                break
            else:
                angle = math.degrees(math.atan2(y_diff, x_diff))
                await self.rotate_to_angle(angle, 10)
                await self.move(60, 50)

async def display_toio_position(cube):
    mat_handler = MultiMatHandler(cube)
    await mat_handler.register_notification_handler()

    try:
        print("Press Ctrl+C to quit")
        while True:
            x, y, angle = mat_handler.get_current_position()
            mat_x, mat_y = mat_handler.get_current_mat()
            print(f"Virtual position: x={x}, y={y}, angle={angle}")
            print(f"Current mat: ({mat_x}, {mat_y})")
            print("--------------------")
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        await mat_handler.unregister_notification_handler()

async def main():
    async with ToioCoreCube() as cube:
        print("Connected to cube")
        mat_handler = MultiMatHandler(cube)
        await mat_handler.register_notification_handler()
        print("Starting movement")
        await mat_handler.move_to_position(250, 250)
        print("Movement completed")
        await mat_handler.unregister_notification_handler()
        print("Disconnected from cube")

if __name__ == "__main__":
    asyncio.run(main())