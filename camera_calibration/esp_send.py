import requests
import time

# ESP32のIPアドレスとポート
ESP32_IP = "192.168.20.1"
ESP32_PORT = 80

# エンドポイントのURL
RIGHT_URL = f"http://{ESP32_IP}:{ESP32_PORT}/PostElevatorTorque"
LEFT_URL = f"http://{ESP32_IP}:{ESP32_PORT}/PostLadderTorque"

def send_command(url, value):
    try:
        response = requests.post(url, data={"Torque": str(value)})
        if response.status_code == 200:
            print(f"Command sent successfully: {url.split('/')[-1]} = {value}")
        else:
            print(f"Failed to send command. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending command: {e}")

def main():
    while True:
        # Rightを1に、Leftを0に設定
        send_command(RIGHT_URL, 1)
        send_command(LEFT_URL, 0)
        time.sleep(0.85)

        # Rightを0に、Leftを1に設定
        send_command(RIGHT_URL, 0)
        send_command(LEFT_URL, 1)
        time.sleep(0.85)

if __name__ == "__main__":
    main()