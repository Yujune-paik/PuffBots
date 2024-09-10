import asyncio
from toio import ToioCoreCube

# グローバル変数の定義
matX = 0
matY = 0
lastX = 0
lastY = 0
x = 0
y = 0

async def update_position(cube):
    global matX, matY, lastX, lastY, x, y

    pos = await cube.api.id_information.read()
    rawX = pos.center.point.x
    rawY = pos.center.point.y

    if lastX > 352 and rawX < 148:
        matX += 1
    elif rawX > 352 and lastX < 148:
        matX -= 1
    if lastY > 308 and rawY < 192:
        matY += 1
    elif rawY > 308 and lastY < 192:
        matY -= 1

    matX = max(0, matX)
    matY = max(0, matY)
    lastX = rawX
    lastY = rawY

    x = rawX + matX * 304
    y = rawY + matY * 216
    print(f"Position: ({x}, {y})")

async def input_listener():
    while True:
        user_input = await asyncio.get_event_loop().run_in_executor(None, input)
        if user_input.lower() == 'q':
            return True
        await asyncio.sleep(0.1)

async def multi_mat():
    async with ToioCoreCube() as cube:
        print("Connected to toio. Press 'q' and Enter to quit.")
        input_task = asyncio.create_task(input_listener())
        try:
            while not input_task.done():
                await update_position(cube)
                await asyncio.sleep(0.1)  # 100msごとに更新
        except asyncio.CancelledError:
            pass
        finally:
            input_task.cancel()
    print("Quitting...")

if __name__ == "__main__":
    asyncio.run(multi_mat())