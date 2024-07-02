# 他のディレクトリから関数をインポートするために sys.path を変更
import sys
import os

# example_simple ディレクトリへのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '../example_simple'))

# 関数をインポート
from goto_a_gird import test

# test() 関数を呼び出す
test()