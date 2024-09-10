import keyboard
import requests
import time

ESP32_IP = "192.168.100.3"  # ESP32のIPアドレスを入力してください

def send_command_to_esp32(state):
    url = f"http://{ESP32_IP}/led"
    try:
        response = requests.get(url, params={"state": state})
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

print("Press 'q' to turn the LED on, and any other key to turn it off. Press 'esc' to exit.")

while True:
    if keyboard.is_pressed('q'):
        send_command_to_esp32("on")
        time.sleep(0.2)  # キーの連続入力を防ぐための小さな遅延
    elif keyboard.is_pressed('esc'):
        print("Exiting...")
        break
    else:
        send_command_to_esp32("off")
    
    time.sleep(0.1)  # CPUの負荷を減らすための小さな遅延