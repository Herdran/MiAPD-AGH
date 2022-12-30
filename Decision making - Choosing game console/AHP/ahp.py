from __future__ import annotations
from functools import reduce
from typing import Callable
import math
import unittest

MAX_COMPARISON_VALUE = 9
Comparison_Matrix_type = dict[str, dict[str, float]]

class Comparison_builder:

    UNINITIALIZED_MATRIX_VALUE = -1.0

    def __init__(self, add_to_model: Callable[[Comparison_Matrix_type], AHP_model|AHP_complete_model], matrix_labels: list[str]):
        self.add_to_model = add_to_model

        get_initial_value = lambda inner, outer: 1.0 if inner == outer else self.UNINITIALIZED_MATRIX_VALUE
        self.matrix = {outer:{inner: get_initial_value(inner, outer) for inner in matrix_labels} for outer in matrix_labels}
        
    def compare(self, first: str, second: str, value: int) -> Comparison_builder|AHP_model|AHP_complete_model:
        assert(value > 0)
        assert(value <= MAX_COMPARISON_VALUE)
        assert(first != second)
        assert(first in self.matrix)
        assert(second in self.matrix)

        self.matrix[first][second] = value
        self.matrix[second][first] = 1 / value

        if self.__is_finished():
            return self.add_to_model(self.matrix) 
        return self

    def __is_finished(self) -> bool:
        return all(all(value != self.UNINITIALIZED_MATRIX_VALUE for value in inner.values()) for inner in self.matrix.values())

class Criteria_comparison_builder(Comparison_builder):
    def __init__(self, model: AHP_model):
        super().__init__(lambda matrix: model.add_criterion_comparison_matrix(matrix), model.criteria)

class Sub_criteria_comparison_builder(Comparison_builder):
    def __init__(self, model: AHP_model, criterion: str):
        super().__init__(lambda matrix: model.add_sub_criterion_comparison_matrix(criterion, matrix), model.sub_criteria[criterion])

class Alternative_comparison_builder(Comparison_builder):
    def __init__(self, model: AHP_model, criterion: str):
        super().__init__(lambda matrix: model.add_alternatives_comparison_matrix(criterion, matrix), model.alternatives)

class AHP_complete_model:
    def __init__(self, model: AHP_model):
        self.model = model

    def GMM(self, matrix: Comparison_Matrix_type) -> dict[str, float]:
        gm_rows = {key:math.prod(values.values()) ** (1 / len(values)) for key, values in matrix.items()}
        gm_rows_sum = sum(gm_rows.values())
        return {key: value / gm_rows_sum for key, value in gm_rows.items()}

    def koczkoaj(self, criterion: str):
        alts = self.model.alternatives
        T = []
        for i in range(len(alts)):
            for j in range(i+1, len(alts)):
                for k in range(j+1, len(alts)):
                    T.append((i, j, k))
        
        def c(i, j):
            return self.model.alternatives_comparison_matrixes[criterion][alts[i]][alts[j]]

        K = {}
        for (i, j, k) in T:
            K.update({(i, j, k):min(abs(1-((c(i, k)*c(k, j)/c(i, j)))), abs(1-((c(i, j)*c(i, k)/c(k, j)))))})

        return max(K.values())


    def calculate(self):
        get_criteria_or_sub_criteria = lambda criterion: self.model.sub_criteria[criterion] if criterion in self.model.sub_criteria else [criterion]
        final_criterion_list = reduce(lambda acc, criterion: acc + get_criteria_or_sub_criteria(criterion), self.model.criteria, [])
        alternatives_priorities = {criterion:self.GMM(self.model.alternatives_comparison_matrixes[criterion]) for criterion in final_criterion_list}
        
        get_parent_criterion = lambda criterion: next((parent_criterion for parent_criterion in self.model.sub_criteria if criterion in self.model.sub_criteria[parent_criterion]), "")

        criteria_priorities = self.GMM(self.model.criterion_comparison_matrix)
        sub_criteria_priorities = {criterion:self.GMM(self.model.sub_criterion_comparison_matrixes[criterion]) for criterion in self.model.sub_criteria}

        get_sub_criterion_priority = lambda sub_criterion: sub_criteria_priorities[get_parent_criterion(sub_criterion)][sub_criterion] * criteria_priorities[get_parent_criterion(sub_criterion)]
        get_criterion_priority = lambda criterion: criteria_priorities[criterion] if criterion in criteria_priorities else get_sub_criterion_priority(criterion)

        calculate_alternative_priority = lambda alternative: (
            sum([alternatives_priorities[criterion][alternative] * get_criterion_priority(criterion) for criterion in final_criterion_list])
        )

        return {alternative:calculate_alternative_priority(alternative) for alternative in self.model.alternatives}

class AHP_model:
    def __init__(self, criteria: list[str], sub_criteria: dict[str, list[str]],  alternatives: list[str]):
        self.criteria = criteria
        self.sub_criteria = sub_criteria
        self.alternatives = alternatives
        self.criterion_count = (len(criteria) - len(sub_criteria)) + sum(map(lambda sub_criteria_list: len(sub_criteria_list), sub_criteria.values()))
        self.alternatives_comparison_matrixes = {}
        self.criterion_comparison_matrix = {}
        self.sub_criterion_comparison_matrixes = {}

    def build_alternatives_comparison(self, criterion: str) -> Alternative_comparison_builder:
        assert(self.__can_build_alternatives_comparison_of(criterion))
        return Alternative_comparison_builder(self, criterion)

    def build_criteria_comparison(self) -> Criteria_comparison_builder:
        return Criteria_comparison_builder(self)

    def build_sub_criteria_comparison(self, criterion: str) -> Sub_criteria_comparison_builder:
        assert(criterion in self.sub_criteria)
        return Sub_criteria_comparison_builder(self, criterion)

    def add_alternatives_comparison_matrix(self, criterion: str, matrix: Comparison_Matrix_type) -> AHP_model|AHP_complete_model:
        self.alternatives_comparison_matrixes.update({criterion:matrix})
        return self.__return_model()

    def add_criterion_comparison_matrix(self, matrix: Comparison_Matrix_type) -> AHP_model|AHP_complete_model:
        self.criterion_comparison_matrix = matrix
        return self.__return_model()

    def add_sub_criterion_comparison_matrix(self, criterion: str, matrix: Comparison_Matrix_type) -> AHP_model|AHP_complete_model:
        self.sub_criterion_comparison_matrixes.update({criterion:matrix})
        return self.__return_model()
        
    def __can_build_alternatives_comparison_of(self, criterion: str) -> bool:
        return (criterion in self.criteria and criterion not in self.sub_criteria) or self.__is_sub_criterion(criterion)
    
    def __is_sub_criterion(self, criterion: str) -> bool:
        return any(map(lambda sub_criteria_list: criterion in sub_criteria_list, self.sub_criteria.values()))

    def __return_model(self) -> AHP_model|AHP_complete_model:
        if(self.__is_finished()): return AHP_complete_model(self)
        return self

    def __is_finished(self) -> bool:
        return ( 
            len(self.criterion_comparison_matrix) != 0 and 
            len(self.alternatives_comparison_matrixes) == self.criterion_count and
            len(self.sub_criterion_comparison_matrixes) == len(self.sub_criteria)
        )
            

    
class AHP_builder:
    def __init__(self):
        self.criteria = []
        self.alternatives = []
        self.sub_criteria = {}

    def add_alternative(self, name: str) -> AHP_builder:
        self.alternatives.append(name)
        return self

    def add_criterion(self, name: str) -> AHP_builder:
        self.criteria.append(name)
        return self

    def add_sub_criterion(self, criterion, name: str) -> AHP_builder:
        assert(criterion in self.criteria)

        if criterion not in self.sub_criteria:
            self.sub_criteria.update({criterion:[name]})
        else:
            self.sub_criteria[criterion].append(name)
        return self

    def build(self) -> AHP_model:
        assert(len(self.criteria) > 0)
        assert(len(self.alternatives) > 0)

        return AHP_model(self.criteria, self.sub_criteria, self.alternatives)


class TestAHP(unittest.TestCase):

    def test_basic_example(self):
        ahp_result = (
            AHP_builder()
            .add_alternative("A")
            .add_alternative("B")
            .add_criterion("X")
            .add_criterion("Y")
            .build()
            .build_alternatives_comparison("X")
            .compare("A", "B", 9)
            .build_alternatives_comparison("Y")
            .compare("A", "B", 1)
            .build_criteria_comparison()
            .compare("X", "Y", 9)
            .calculate()
        )

        self.assertGreater(ahp_result["A"], ahp_result["B"])

    def test_wikipedia_leader(self):
        # https://en.wikipedia.org/wiki/Analytic_hierarchy_process_–_leader_example
        ahp_result = (
            AHP_builder()
            .add_alternative("Tom")
            .add_alternative("Dick")
            .add_alternative("Harry")
            .add_criterion("Experience")
            .add_criterion("Education")
            .add_criterion("Charisma")
            .add_criterion("Age")
            .build()
            .build_alternatives_comparison("Experience")
            .compare("Dick", "Tom", 4)
            .compare("Tom", "Harry", 4)
            .compare("Dick", "Harry", 9)
            .build_alternatives_comparison("Education")
            .compare("Tom", "Dick", 3)
            .compare("Harry", "Tom", 5)
            .compare("Harry", "Dick", 7)
            .build_alternatives_comparison("Charisma")
            .compare("Tom", "Dick", 5)
            .compare("Tom", "Harry", 9)
            .compare("Dick", "Harry", 4)
            .build_alternatives_comparison("Age")
            .compare("Dick", "Tom", 3)
            .compare("Tom", "Harry", 5)
            .compare("Dick", "Harry", 9)
            .build_criteria_comparison()
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

    def test_sub_criteria(self):
        ahp_result = (
            AHP_builder()
            .add_alternative("A")
            .add_alternative("B")
            .add_criterion("X")
            .add_criterion("Y")
            .add_sub_criterion("X", "X1")
            .add_sub_criterion("X", "X2")
            .build()
            .build_alternatives_comparison("Y")
            .compare("A", "B", 1)
            .build_alternatives_comparison("X1")
            .compare("A", "B", 2)
            .build_alternatives_comparison("X2")
            .compare("B", "A", 3)
            .build_criteria_comparison()
            .compare("X", "Y", 1)
            .build_sub_criteria_comparison("X")
            .compare("X1", "X2", 2)
            .calculate()
        )

        self.assertGreater(ahp_result["A"], ahp_result["B"])

    def test_koczkodaj(self):
        alts = ["a", "b", "c", "d", "e"]
        cryt = ["1"]
        mat_list = [
            [1, 69/74, 10/31, 7/22, 19/7],
            [74/69, 1, 27/43, 2/3, 34/13],
            [31/10, 43/27, 1, 47/38, 73/7],
            [22/7, 3/2, 38/47, 1, 7],
            [7/19, 13/34, 7/73, 1/7, 1],
        ]
        mat_dict = {
            alts[a]:{alts[b]:mat_list[a][b] for b in range(len(alts))} for a in range(len(alts))
        }
        model = AHP_model(cryt, {}, alts)
        model.alternatives_comparison_matrixes = {"1":mat_dict}
        complete = AHP_complete_model(model)

        self.assertAlmostEqual(complete.koczkoaj("1"), 0.60059, 5)

            


if __name__ == '__main__':
    unittest.main()

