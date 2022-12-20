arr = []


def complicated_stuff(val):
    arr.append(val)
    print(arr)


class ahp:
    def __init__(self, **kwargs):
        self.curr_val = 0
        # super().__init__(**kwargs)

    def set_curr_val(self, val):
        self.curr_val = val

    def get_curr_val(self):
        print(self.curr_val)
