import asyncio
from toio import *

async def display_toio_position(cube):
    def id_notification_handler(payload: bytearray):
        id_info = IdInformation.is_my_data(payload)
        if isinstance(id_info, PositionId):
            print(f"Cube position: x={id_info.center.point.x}, y={id_info.center.point.y}, angle={id_info.center.angle}")

    await cube.api.id_information.register_notification_handler(id_notification_handler)
    
    await cube.api.id_information.unregister_notification_handler(id_notification_handler)

async def main():
    async with ToioCoreCube() as cube:
        print("Connected to cube")
        await display_toio_position(cube)
        print("Disconnected from cube")

# メイン関数を実行
asyncio.run(main())