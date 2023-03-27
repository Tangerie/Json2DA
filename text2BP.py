from pprint import pprint
import json
import importlib
import WidgetUtil
importlib.reload(WidgetUtil)
import Clipboard
importlib.reload(Clipboard)

def create_widget(json_str):
    data = json.loads(json_str)
    w = WidgetUtil.CreateRootWidget(data)
    Clipboard.put(w)
    return w


# Test script
if __name__ == "__main__":
    TEST_FILE = "ui" #"__jso" # "VectorOverrideRow"
    with open(fr"F:\HL\PhoenixUProj\Content\Python\.private\{TEST_FILE}.json", "r") as fp:
        w = create_widget(fp.read())
    with open(r"F:\HL\PhoenixUProj\Content\Python\.private\output.txt", "w+") as fp:
        fp.write(w)