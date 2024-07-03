# 他のディレクトリから関数をインポートするために sys.path を変更
import sys
import os

# example_simple ディレクトリへのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '../example_simple'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../ar_marker'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# 関数をインポート
import toio_information

# toio_information内のリストを取得
toio_list = toio_information.get_toio_list()
print(toio_information.get_toio_name(0))