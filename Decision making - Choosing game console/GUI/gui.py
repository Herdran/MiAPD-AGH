import pathlib

from kivy.config import Config
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.list import MDList, OneLineListItem
import os

Config.set('input', 'mouse', 'mouse,disable_multitouch')

file_path = str(pathlib.Path(__file__).parent.resolve())


class WelcomeScreen(Screen):
    pass


class MainScreen(Screen):
    pass


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        scroll = ScrollView(size_hint=(.78, 1), pos_hint={"x": 0.11})
        list_view = MDList()
        scroll.add_widget(list_view)

        for i in range(20):
            item = OneLineListItem(text="item" + str(i))
            item.bind(on_press=self.on_press_func)
            list_view.add_widget(item)

        self.add_widget(scroll)

    def on_press_func(self, instance):
        print(instance.text)
        instance.text = "something different"


class WindowManager(ScreenManager):
    images_path = os.path.join(file_path, "Images")
    screen_mode_change_image_link = StringProperty(os.path.join(images_path, "fullscreen_maximize.png"))
    settings_icon_link = StringProperty(os.path.join(images_path, "settings.png"))
    return_icon_link = StringProperty(os.path.join(images_path, "return.png"))
    skip_icon_link = StringProperty(os.path.join(images_path, "next.png"))
    last_screen = "welcome_screen"

    def screen_mode_change(self):
        if Window.fullscreen:
            Window.fullscreen = False
            self.screen_mode_change_image_link = os.path.join(self.images_path, "fullscreen_maximize.png")
        else:
            Window.fullscreen = "auto"
            self.screen_mode_change_image_link = os.path.join(self.images_path, "fullscreen_minimalize.png")


class Gui(MDApp):
    def build(self):
        Window.minimum_width = 640
        Window.minimum_height = 360
        self.icon = file_path + "Images//logo_maybe.png"
        self.title = "Decision making - Choosing game console"
        return Builder.load_file(os.path.join(file_path, "gui.kv"))

# if __name__ == "__main__":
#     Gui().run()
