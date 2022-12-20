import threading

from GUI import gui
# from AHP.ahp_thread_placeholder import complicated_stuff
from AHP import ahp_thread_placeholder

if __name__ == "__main__":
    # ahp_thread = threading.Thread(target=ahp_thread_placeholder, args=())
    # ahp_thread.start()
    gui.ahp = ahp_thread_placeholder.ahp()
    gui.Gui().run()