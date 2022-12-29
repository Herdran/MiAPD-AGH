import itertools
import os
import pathlib

from kivy.config import Config
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp

Config.set("input", "mouse", "mouse,disable_multitouch")

file_path = str(pathlib.Path(__file__).parent.resolve())

ahp = None

criteria = ["Price", "Graphics", "Performance"]

alternatives = ["PS4", "PS5", "XBOX ONE", "XBOX SERIES X", "XBOX SERIES S", "NINTENDO SWITCH", "STEAM DECK"]

images_path = os.path.join(file_path, "Images")

alternatives_images_links = {alternative: alternative.replace(" ", "_") + ".png" for alternative in alternatives}

alternatives_combinations = list(itertools.combinations(alternatives, 2))


class WelcomeScreen(Screen):
    pass


class MainScreen(Screen):
    curr_val = 0
    curr_criterion_index = 0
    curr_alternatives_index = -1

    criteria_count = len(criteria)
    alternatives_combinations_count = len(alternatives_combinations)

    curr_criterion = StringProperty(criteria[curr_criterion_index])
    left_text = StringProperty(alternatives_combinations[curr_alternatives_index][0])
    right_text = StringProperty(alternatives_combinations[curr_alternatives_index][1])
    left_image_link = StringProperty(
        os.path.join(images_path, alternatives_images_links[alternatives_combinations[curr_alternatives_index][0]]))
    right_image_link = StringProperty(
        os.path.join(images_path, alternatives_images_links[alternatives_combinations[curr_alternatives_index][1]]))

    def set_curr_val(self, val):
        self.curr_val = val

    def confirm_answer(self):
        print(self.curr_val)
        self.change_question()

    def skip_question(self):
        print("Skipping question? idk how would that work")
        self.change_question()

    def change_question(self):
        if self.curr_alternatives_index >= self.alternatives_combinations_count - 1:
            if self.curr_criterion_index >= self.criteria_count - 1:
                self.curr_criterion_index = 0
                self.curr_alternatives_index = 0
                print("All questions answered, displaying results")
                self.manager.current = "results_screen"
            else:
                self.curr_criterion_index += 1
                self.curr_alternatives_index = 0
        else:
            self.curr_alternatives_index += 1

        self.curr_criterion = criteria[self.curr_criterion_index]
        self.left_text = alternatives_combinations[self.curr_alternatives_index][0]
        self.right_text = alternatives_combinations[self.curr_alternatives_index][1]
        self.left_image_link = os.path.join(images_path, alternatives_images_links[self.left_text])
        self.right_image_link = os.path.join(images_path, alternatives_images_links[self.right_text])

    # def reset_checkbox(self):
    #     for child in reversed(self.ids.grid.children):
    #         # print(child)
    #         if isinstance(child, MDCheckbox):
    #             child.active = False
    #             print("test")


class SettingsScreen(Screen):
    pass


class ResultsScreen(Screen):
    pass


class WindowManager(ScreenManager):
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
