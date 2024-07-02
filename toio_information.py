# toioのnumberとnameのリスト
toio_list = [
    {"number": 0, "name": "B6e"},
    {"number": 1, "name": "36r"},
    {"number": 2, "name": "r64"},
    {"number": 3, "name": "p6M"},
]

# toioのnumberとnameのリストを返す
def get_toio_list():
    return toio_list

# toioのnameからnumberを取得
def get_toio_number(name):
    for toio in toio_list:
        if toio["name"] == name:
            return toio["number"]
    return None

# toioのnumberからnameを取得
def get_toio_name(number):
    for toio in toio_list:
        if toio["number"] == number:
            return toio["name"]
    return None