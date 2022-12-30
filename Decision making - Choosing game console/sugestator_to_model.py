import os
import itertools
from typing import Callable

from AHP.ahp import AHP_builder, AHP_complete_model

class SugestatorToModel:
    def __init__(self, alternatives_path: os.path, criteria_path: os.path):
        self.load_alternatives(alternatives_path)
        self.load_criteria(criteria_path)
        self.build_model()
        self.comparisions = {c:{a:{b:None for b in self.alternatives} for a in self.alternatives} for c in self.get_criteria_to_choose()}
        self.criteria_comparisions = {a:{b:None for b in self.criteria} for a in self.criteria}
        self.sub_criteria_comparisions = {crit:{a:{b:None for b in self.sub_criteria[crit]} for a in self.sub_criteria[crit]} for crit in self.sub_criteria.keys()}
        self.mapping_function = lambda x: x


    def load_alternatives(self, path: os.path):
        self.alternatives = []
        with open(path, 'r') as f:
            for line in f:
                self.alternatives.append(line.strip())

    def load_criteria(self, path: os.path):
        self.criteria = []
        self.sub_criteria = {}
        with open(path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                if line.startswith(' '):
                    if self.criteria[-1] not in self.sub_criteria:
                        self.sub_criteria[self.criteria[-1]] = []
                    self.sub_criteria[self.criteria[-1]].append(line.strip())
                else:
                    self.criteria.append(line.strip())

    def build_model(self):
        self.model = AHP_builder()
        for alternative in self.alternatives:
            self.model = self.model.add_alternative(alternative)
        for criterion in self.criteria:
            self.model = self.model.add_criterion(criterion)
        for criterion, sub_criteria in self.sub_criteria.items():
            for sub_criterion in sub_criteria:
                self.model = self.model.add_sub_criterion(criterion, sub_criterion)
        self.model = self.model.build()

    def set_mapping_function(self, mapping_function: Callable[[int], int]):
        self.mapping_function = mapping_function

    def load_comparisions_value_into_model(self) -> AHP_complete_model:
        combinations = lambda x: list(itertools.combinations(x, 2))

        def add_comparision_to_model(first, second, value):
            self.model = self.model.compare(first, second, value) if value >= 0 else self.model.compare(second, first, -value)

        for criterion in self.get_criteria_to_choose():
            self.model = self.model.build_alternatives_comparison(criterion)
            for first_alt, second_alt in combinations(self.alternatives):
                add_comparision_to_model(first_alt, second_alt, self.comparisions[criterion][first_alt][second_alt])

        self.model = self.model.build_criteria_comparison()
        for first_crit, second_crit in combinations(self.criteria):
            add_comparision_to_model(first_crit, second_crit, self.criteria_comparisions[first_crit][second_crit])

        for criterion in self.sub_criteria.keys():
            self.model = self.model.build_sub_criteria_comparison(criterion)
            for first_crit, second_crit in combinations(self.sub_criteria[criterion]):
                add_comparision_to_model(first_crit, second_crit, self.sub_criteria_comparisions[criterion][first_crit][second_crit])

        return self.model

    def get_criteria_to_choose(self) -> list[str]:
        result = []

        for criterion in self.criteria:
            if criterion not in self.sub_criteria:
                result.append(criterion)
            else:
                for sub_criterion in self.sub_criteria[criterion]:
                    result.append(sub_criterion)
        return result

    def get_criteria_and_subcriteria_combinations(self) -> list[(str, str)]:
        result = list(itertools.combinations(self.criteria, 2))

        for criterion in self.criteria:
            if criterion in self.sub_criteria:
                tmp = []
                for sub_criterion in self.sub_criteria[criterion]:
                    tmp.append(sub_criterion)
                result += list(itertools.combinations(tmp, 2))
        return result

    def has_sub_criteria(self, criterion: str) -> bool:
        return criterion in self.sub_criteria

    def get_sub_critera(self, criterion: str) -> list[str]:
        return self.sub_criteria[criterion]

    def add_partial_comparision(self, first_alter: str, second_alter: str, criterion: str, value: int):
        self.comparisions[criterion][first_alter][second_alter] = self.mapping_function(value)
        self.comparisions[criterion][second_alter][first_alter] = self.mapping_function(-value)

    def add_partial_cryteria_comparision(self, first_cryterion: str, second_cryterion: str, value: int):
        if self.is_main_criterion(first_cryterion) and self.is_main_criterion(second_cryterion):
            self.criteria_comparisions[first_cryterion][second_cryterion] = self.mapping_function(value)
            self.criteria_comparisions[second_cryterion][first_cryterion] = self.mapping_function(-value)
        else:
            main_cryterion = self.get_main_criterion(first_cryterion)
            self.sub_criteria_comparisions[main_cryterion][first_cryterion][second_cryterion] = self.mapping_function(value)
            self.sub_criteria_comparisions[main_cryterion][second_cryterion][first_cryterion] = self.mapping_function(-value)

    def is_main_criterion(self, criterion: str) -> bool:
        return criterion in self.criteria

    def get_main_criterion(self, criterion: str) -> str:
        for main_criterion in  self.sub_criteria.keys():
            if criterion in self.sub_criteria[main_criterion]:
                return main_criterion

    def add_partial_sub_cryteria_comparision(self, first_cryterion: str, second_cryterion: str, main_cryterion: str, value: int):
        self.sub_criteria_comparisions[main_cryterion][first_cryterion][second_cryterion] = self.mapping_function(value)
        self.sub_criteria_comparisions[main_cryterion][second_cryterion][first_cryterion] = self.mapping_function(-value)

if __name__ == '__main__':
    sugestator = SugestatorToModel('Data/alternatives.txt', 'Data/criteria.txt')
    print(sugestator.alternatives)
    print(sugestator.criteria)
    print(sugestator.sub_criteria)
    print(sugestator.model)