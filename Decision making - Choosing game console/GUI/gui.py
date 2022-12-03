import pathlib

from kivy.config import Config
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.list import MDList, OneLineListItem

Config.set('input', 'mouse', 'mouse,disable_multitouch')

file_path = str(pathlib.Path(__file__).parent.resolve()) + "\\"


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
    screen_mode_change_image_link = StringProperty(file_path + "Images/fullscreen_maximize.png")
    settings_icon_link = StringProperty(file_path + "Images/settings.png")
    return_icon_link = StringProperty(file_path + "Images/return.png")
    skip_icon_link = StringProperty(file_path + "Images/next.png")
    last_screen = "welcome_screen"

    def screen_mode_change(self):
        if Window.fullscreen:
            Window.fullscreen = False
            self.screen_mode_change_image_link = file_path + "Images/fullscreen_maximize.png"
        else:
            Window.fullscreen = "auto"
            self.screen_mode_change_image_link = file_path + "Images/fullscreen_minimalize.png"


class Gui(MDApp):
    def build(self):
        Window.minimum_width = 640
        Window.minimum_height = 360
        self.icon = file_path + "Images/logo_maybe.png"
        self.title = "Decision making - Choosing game console"
        return Builder.load_file(file_path + "gui.kv")

# if __name__ == "__main__":
#     Gui().run()
