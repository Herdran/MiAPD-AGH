import os
import itertools
from typing import Callable

from AHP.ahp import AHP_builder

class SugestatorToModel:
    def __init__(self, alternatives_path: os.path, criteria_path: os.path):
        self.load_alternatives(alternatives_path)
        self.load_criteria(criteria_path)
        self.build_model()
        self.comparisions = {c:{a:{b:None for b in self.alternatives} for a in self.alternatives} for c in self.get_criteria_to_choose()}
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

    def load_comparisions_value_into_model(self):
        alternatives_combinations = list(itertools.combinations(self.alternatives, 2))


        for criterion in self.get_criteria_to_choose():
            self.model = self.model.build_alternatives_comparison(criterion)
            for first_alt, second_alt in alternatives_combinations:
                val = self.comparisions[criterion][first_alt][second_alt]

                print(f"{criterion}:{first_alt}:{second_alt} -> {val}")

                if val >= 0:
                    self.model = self.model.compare(first_alt, second_alt, val)
                else:
                    self.model = self.model.compare(second_alt, first_alt, -val)



    def get_criteria_to_choose(self) -> list[str]:
        result = []
        
        for criterion in self.criteria:
            if criterion not in self.sub_criteria:
                result.append(criterion)
            else:
                for sub_criterion in self.sub_criteria[criterion]:
                    result.append(sub_criterion)
        return result

    def add_partial_comparision(self, first_alter: str, second_alter: str, criterion: str, value: int):
        self.comparisions[criterion][first_alter][second_alter] = self.mapping_function(value)
        self.comparisions[criterion][second_alter][first_alter] = self.mapping_function(-value)

if __name__ == '__main__':
    sugestator = SugestatorToModel('Data/alternatives.txt', 'Data/criteria.txt')
    print(sugestator.alternatives)
    print(sugestator.criteria)
    print(sugestator.sub_criteria)
    print(sugestator.model)