import os,sys,json

# --------------- get the directory where this code is executed -----------

def get_base_dir():
    if getattr(sys, 'frozen', False):           # Running as a PyInstaller EXE
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))   # Running as a normal .py script
    
def get_config():
    with open(os.path.join(get_base_dir(),"password.json" ), 'r') as file:
         js = json.load(file)
         return js
    
def get_map_path():
    return os.path.join(get_base_dir(),"mymap.png")