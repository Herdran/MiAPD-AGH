from GUI import gui
from AHP import ahp

if __name__ == "__main__":
    gui.ahp = ahp
    gui.Gui().run()