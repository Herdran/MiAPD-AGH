from AHP.ahp import AHP_builder

class SugestatorToModel:
    def __init__(self, alternatives_path, criteria_path):
        self.load_alternatives(alternatives_path)
        self.load_criteria(criteria_path)
        self.model = self.build_model()
        

    def load_alternatives(self, path):
        self.alternatives = []
        with open(path, 'r') as f:
            for line in f:
                self.alternatives.append(line.strip())

    def load_criteria(self, path):
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
            self.model.add_alternative(alternative)
        for criterion in self.criteria:
            self.model.add_criterion(criterion)
        for criterion, sub_criteria in self.sub_criteria.items():
            for sub_criterion in sub_criteria:
                self.model.add_sub_criterion(criterion, sub_criterion)


if __name__ == '__main__':
    sugestator = SugestatorToModel('Data/alternatives.txt', 'Data/criteria.txt')
    print(sugestator.alternatives)
    print(sugestator.criteria)
    print(sugestator.sub_criteria)