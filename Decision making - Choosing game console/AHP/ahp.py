from __future__ import annotations
from functools import reduce
from typing import Callable
import math
import unittest

MAX_COMPARISION_VALUE = 9
Comparision_Matrix_type = dict[str, dict[str, float]]

class Comparision_builder:

    UNINITRIALIZED_MATRIX_VALUE = -1.0

    def __init__(self, add_to_model: Callable[[Comparision_Matrix_type], AHP_model|AHP_complete_model], matrix_labels: list[str]):
        self.add_to_model = add_to_model

        get_initial_value = lambda inner, outer: 1.0 if inner == outer else self.UNINITRIALIZED_MATRIX_VALUE
        self.matrix = {outer:{inner: get_initial_value(inner, outer) for inner in matrix_labels} for outer in matrix_labels}
        
    def compare(self, first: str, second: str, value: int) -> Comparision_builder|AHP_model|AHP_complete_model:
        assert(value > 0)
        assert(value <= MAX_COMPARISION_VALUE)
        assert(first != second)
        assert(first in self.matrix.keys())
        assert(second in self.matrix.keys())

        self.matrix[first][second] = value
        self.matrix[second][first] = 1 / value

        if self.__is_finished():
            return self.add_to_model(self.matrix) 
        return self

    def __is_finished(self) -> bool:
        return all(all(value != self.UNINITRIALIZED_MATRIX_VALUE for value in inner.values()) for inner in self.matrix.values())

class Cryteria_comparision_builder(Comparision_builder):
    def __init__(self, model: AHP_model):
        super().__init__(lambda matrix: model.add_cryteria_comparision_matrix(matrix), model.criteria)

class Alternative_comparision_builder(Comparision_builder):
    def __init__(self, model: AHP_model, criterion: str):
        super().__init__(lambda matrix: model.add_alternatives_comparision_matrix(criterion, matrix), model.alternatives)

class AHP_complete_model:
    def __init__(self, model: AHP_model):
        self.model = model

    def GMM(self, matrix: Comparision_Matrix_type) -> dict[str, float]:
        gm_rows = {key:math.prod(values.values()) ** (1 / len(values)) for key, values in matrix.items()}
        gm_rows_sum = sum(gm_rows.values())
        return {key: value / gm_rows_sum for key, value in gm_rows.items()}

    def calculate(self):
        alternatives_proririties = {cryterion:self.GMM(self.model.alternatives_comparision_matrixes[cryterion]) for cryterion in self.model.criteria}
        cryteria_proririties = self.GMM(self.model.cryterion_comparision_matrix)
        
        calculate_alternative_priority = lambda alternative: (
            sum([alternatives_proririties[cryterion][alternative] * cryteria_proririties[cryterion] for cryterion in self.model.criteria])
        )

        return {alternative:calculate_alternative_priority(alternative) for alternative in self.model.alternatives}

class AHP_model:
    def __init__(self, criteria: list[str], alternatives: list[str]):
        self.criteria = criteria
        self.alternatives = alternatives
        self.alternatives_comparision_matrixes = {}
        self.cryterion_comparision_matrix = {}

    def build_alternatives_comparision(self, criterion: str) -> Alternative_comparision_builder:
        return Alternative_comparision_builder(self, criterion)

    def build_cryteria_comparision(self) -> Cryteria_comparision_builder:
        return Cryteria_comparision_builder(self)

    def add_alternatives_comparision_matrix(self, criterion: str, matrix: Comparision_Matrix_type) -> AHP_model|AHP_complete_model:
        self.alternatives_comparision_matrixes.update({criterion:matrix})
        return self.__return_model()

    def add_cryteria_comparision_matrix(self, matrix: Comparision_Matrix_type) -> AHP_model|AHP_complete_model:
        self.cryterion_comparision_matrix = matrix
        return self.__return_model()
        
    def __return_model(self) -> AHP_model|AHP_complete_model:
        if(self.__is_finished()): return AHP_complete_model(self)
        return self

    def __is_finished(self) -> bool:
        return ( 
            len(self.cryterion_comparision_matrix) != 0 and 
            len(self.alternatives_comparision_matrixes) == len(self.criteria)
        )
            

    
class AHP_builder:
    def __init__(self):
        self.criteria = []
        self.alternatives = []

    def add_alternative(self, name: str) -> AHP_builder:
        self.alternatives.append(name)
        return self

    def add_criteria(self, name: str) -> AHP_builder:
        self.criteria.append(name)
        return self

    def build(self) -> AHP_model:
        assert(len(self.criteria) > 0)
        assert(len(self.alternatives) > 0)

        return AHP_model(self.criteria, self.alternatives)


class TestAHP(unittest.TestCase):

    def test_basic_example(self):
        ahp_result = (
            AHP_builder()
            .add_alternative("A")
            .add_alternative("B")
            .add_criteria("X")
            .add_criteria("Y")
            .build()
            .build_alternatives_comparision("X")
            .compare("A", "B", 9)
            .build_alternatives_comparision("Y")
            .compare("A", "B", 1)
            .build_cryteria_comparision()
            .compare("X", "Y", 9)
            .calculate()
        )

        print(ahp_result)

    def test_wikipedia_leader(self):
        # https://en.wikipedia.org/wiki/Analytic_hierarchy_process_–_leader_example
        ahp_result = (
            AHP_builder()
            .add_alternative("Tom")
            .add_alternative("Dick")
            .add_alternative("Harry")
            .add_criteria("Experience")
            .add_criteria("Education")
            .add_criteria("Charisma")
            .add_criteria("Age")
            .build()
            .build_alternatives_comparision("Experience")
            .compare("Dick", "Tom", 4)
            .compare("Tom", "Harry", 4)
            .compare("Dick", "Harry", 9)
            .build_alternatives_comparision("Education")
            .compare("Tom", "Dick", 3)
            .compare("Harry", "Tom", 5)
            .compare("Harry", "Dick", 7)
            .build_alternatives_comparision("Charisma")
            .compare("Tom", "Dick", 5)
            .compare("Tom", "Harry", 9)
            .compare("Dick", "Harry", 4)
            .build_alternatives_comparision("Age")
            .compare("Dick", "Tom", 3)
            .compare("Tom", "Harry", 5)
            .compare("Dick", "Harry", 9)
            .build_cryteria_comparision()
            .compare("Experience", "Education", 4)
            .compare("Experience", "Charisma", 3)
            .compare("Experience", "Age", 7)
            .compare("Education", "Age", 3)
            .compare("Charisma", "Education", 3)
            .compare("Charisma", "Age", 5)
            .calculate()
        )


        ranking = [k for k, _ in sorted(ahp_result.items(), key=lambda item: item[1], reverse=True)]
        self.assertEqual(ranking, ["Dick", "Tom", "Harry"])

if __name__ == '__main__':
    unittest.main()

