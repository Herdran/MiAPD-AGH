import itertools
import os
import pathlib

from kivy.config import Config
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from sugestator_to_model import SugestatorToModel

Config.set("input", "mouse", "mouse,disable_multitouch")

file_path = str(pathlib.Path(__file__).parent.resolve())

sugestator_to_model = SugestatorToModel(os.path.join("Data", "alternatives.txt"), os.path.join("Data", "criteria.txt"))

ahp = sugestator_to_model.model
alternatives = sugestator_to_model.alternatives
criteria = sugestator_to_model.get_criteria_to_choose()

images_path = os.path.join(file_path, "Images")

alternatives_images_links = {alternative: alternative.replace(" ", "_") + ".png" for alternative in alternatives}

alternatives_combinations = list(itertools.combinations(alternatives, 2))

criteria_and_subcriteria_combinations = sugestator_to_model.get_criteria_and_subcriteria_combinations()


def mapping_function(val: int):
    match val:
        case -2:
            return -9
        case -1:
            return -4
        case 0:
            return 1
        case 1:
            return 4
        case 2:
            return -9


sugestator_to_model.set_mapping_function(mapping_function)


class WelcomeScreen(Screen):
    pass


class MainScreen(Screen):
    curr_val = 0
    curr_criterion_index = 0
    curr_alternatives_index = 0

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
        sugestator_to_model.add_partial_comparision(self.left_text, self.right_text, self.curr_criterion, self.curr_val)
        self.change_question()

    def change_question(self):
        if self.curr_alternatives_index >= self.alternatives_combinations_count - 1:
            if self.curr_criterion_index >= self.criteria_count - 1:
                self.curr_criterion_index = 0
                self.curr_alternatives_index = 0
                self.manager.current = "criteria_screen"
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


class SettingsScreen(Screen):
    pass


class CriteriaScreen(Screen):
    curr_val = 0
    curr_criterion_index = 0

    criteria_combinations_count = len(criteria_and_subcriteria_combinations)

    left_text = StringProperty(criteria_and_subcriteria_combinations[curr_criterion_index][0])
    right_text = StringProperty(criteria_and_subcriteria_combinations[curr_criterion_index][1])

    def set_curr_val(self, val):
        self.curr_val = val

    def confirm_answer(self):
        sugestator_to_model.add_partial_cryteria_comparision(self.left_text, self.right_text, self.curr_val)
        self.change_question()

    def change_question(self):
        if self.curr_criterion_index >= self.criteria_combinations_count - 1:
            self.curr_criterion_index = 0

            # ne gdzie to dac to na koncu wrzuca wszystkie dane do modelu
            complete_model = sugestator_to_model.load_comparisions_value_into_model()
            # i tu dostajesz kompletny model
            # masz metody calculate -> zwraca ranking
            # i koczkoaj od danego kryterium

            self.manager.get_screen('results_screen').generate_result_view(complete_model)
            self.manager.current = "results_screen"

            # print(complete_model.calculate())
            # print("============")
            # print(complete_model.koczkoaj("Price"))
            # print(complete_model.koczkoaj("Exclusives"))
            # print(complete_model.koczkoaj("Subscription model"))

        else:
            self.curr_criterion_index += 1

        self.left_text = criteria_and_subcriteria_combinations[self.curr_criterion_index][0]
        self.right_text = criteria_and_subcriteria_combinations[self.curr_criterion_index][1]


class ResultsScreen(Screen):
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #
    #     layout = GridLayout(cols=2, pos_hint={"x": 0.15, "y": 0.2}, size_hint=(.7, .7))
    #     self.layout_left = GridLayout(cols=1, spacing=5, size_hint_y=None)
    #     self.layout_right = GridLayout(cols=1, spacing=5, size_hint_y=None)
    #     self.layout_left.bind(minimum_height=self.layout_left.setter('height'))
    #     self.layout_right.bind(minimum_height=self.layout_right.setter('height'))
    #
    #
    #     scroll_left = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
    #     scroll_left.add_widget(self.layout_left)
    #     scroll_right = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
    #     scroll_right.add_widget(self.layout_right)
    #     layout.add_widget(scroll_left)
    #     layout.add_widget(scroll_right)
    #     self.add_widget(layout)

    def generate_result_view(self, complete_model):
        results = complete_model.calculate()
        results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))

        for key in results:
            lbl = Label(text=key + "  ---  " + str(results[key]), size_hint_y=None, color=(0, 0, 0, 1))
            self.ids.left_scroll_view.add_widget(lbl)

        sorted_koczkoaj = {criterion: complete_model.koczkoaj(criterion) for criterion in criteria}
        sorted_koczkoaj = dict(sorted(sorted_koczkoaj.items(), key=lambda item: item[1], reverse=True))

        for key in sorted_koczkoaj:
            lbl2 = Label(text=key + "  ---  " + str(sorted_koczkoaj[key]), size_hint_y=None, color=(0, 0, 0, 1))
            self.ids.right_scroll_view.add_widget(lbl2)


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
