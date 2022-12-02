from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang.builder import Builder
from kivy.config import Config
# Config.set('graphics', 'resizable', '0')


from kivy.core.window import Window


class WelcomeScreen(Screen):
    pass


class MainScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class WindowManager(ScreenManager):
    screen_mode_change_image_link = StringProperty("Images/fullscreen_maximize.png")
    last_screen = "welcome_screen"

    def screen_mode_change(self):
        if Window.fullscreen:
            Window.fullscreen = False
            # self.screen_mode_change_image_link = "Images/fullscreen_maximize.png"
            self.screen_mode_change_image_link = "Images/fullscreen_maximize.png"
            # self.ids.screen_mode_button.background_normal = "Images/fullscreen_maximize.png"
            # self.ids.screen_mode_button.background_down = "Images/fullscreen_maximize.png"
        else:
            Window.fullscreen = "auto"
            # self.screen_mode_change_image_link = "Images/fullscreen_minimalize.png"
            self.screen_mode_change_image_link = "Images/fullscreen_minimalize.png"
            # self.ids.screen_mode_button.background_normal = "Images/fullscreen_minimalize.png"
            # self.ids.screen_mode_button.background_down = "Images/fullscreen_minimalize.png"


class Gui(App):
    # Config.set('graphics', 'resizable', '0')
    # Config.set("graphics", "fullscreen", "auto")
    # Config.set('graphics', 'width', '1280')
    # Config.set('graphics', 'height', '720')
    # Window.borderless = True

    def build(self):
        Window.minimum_width = 640
        Window.minimum_height = 360
        self.icon = 'Images/logo_maybe.png'
        self.title = "Decision making - Choosing game console"
        return Builder.load_file('gui.kv')


if __name__ == "__main__":
    Gui().run()
