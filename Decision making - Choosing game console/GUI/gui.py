import pathlib

from kivy.config import Config
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivymd.app import MDApp
from kivymd.uix.list import MDList, OneLineListItem, OneLineAvatarListItem
import os

from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.slider import MDSlider

Config.set("input", "mouse", "mouse,disable_multitouch")

file_path = str(pathlib.Path(__file__).parent.resolve())

ahp = None


# from ..AHP.ahp_thread_placeholder import complicated_stuff


# def on_checkbox_active(self, checkbox, value):
#     if value:
#         print('The checkbox', checkbox, 'is active')
#     else:
#         print('The checkbox', checkbox, 'is inactive')

class WelcomeScreen(Screen):
    pass


class MainScreen(Screen):
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.curr_val = 0
    # activeee = False

    def set_curr_val(self, val):
        # print(self.curr_val)
        # complicated_stuff(self.curr_val)
        ahp.set_curr_val(val)

    def get_curr_val(self):
        ahp.get_curr_val()

    def reset_checkbox(self):
        # self.activeee = False

        for child in reversed(self.ids.grid.children):
            # print(child)
            if isinstance(child, MDCheckbox):
                child.active = False
                print("test")


class SettingsScreen(Screen):
    pass
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

    # def slider_ring_change_blocker(self, instance, value):
    #     if instance.value == instance.min:
    #         instance._is_off = False
    #     # instance.text = "something different"
    # def on_checkbox_active(self, checkbox, value):
    #     if value:
    #         print('The checkbox', checkbox, 'is active')
    #     else:
    #         print('The checkbox', checkbox, 'is inactive')


class WindowManager(ScreenManager):
    images_path = os.path.join(file_path, "Images")
    screen_mode_change_image_link = StringProperty(os.path.join(images_path, "fullscreen_maximize.png"))
    settings_icon_link = StringProperty(os.path.join(images_path, "settings.png"))
    return_icon_link = StringProperty(os.path.join(images_path, "return.png"))
    skip_icon_link = StringProperty(os.path.join(images_path, "next.png"))
    button_rectangle_image_link = StringProperty(os.path.join(images_path, "button_rectangle_round_corners_background.png"))
    left_image_link = StringProperty(os.path.join(images_path, "left_image_placeholder.png"))
    right_image_link = StringProperty(os.path.join(images_path, "right_image_placeholder.png"))
    last_screen = "welcome_screen"


    def screen_mode_change(self):
        if Window.fullscreen:
            Window.fullscreen = False
            self.screen_mode_change_image_link = os.path.join(self.images_path, "fullscreen_maximize.png")
        else:
            Window.fullscreen = "auto"
            self.screen_mode_change_image_link = os.path.join(self.images_path, "fullscreen_minimalize.png")


class Gui(MDApp):
    # def on_checkbox_active(self, checkbox, value):
    #     if value:
    #         print('The checkbox', checkbox, 'is active')
    #     else:
    #         print('The checkbox', checkbox, 'is inactive')

    def build(self):
        Window.minimum_width = 640
        Window.minimum_height = 360
        self.icon = file_path + "Images//logo_maybe.png"
        self.title = "Decision making - Choosing game console"
        return Builder.load_file(os.path.join(file_path, "gui.kv"))

# if __name__ == "__main__":
#     Gui().run()
