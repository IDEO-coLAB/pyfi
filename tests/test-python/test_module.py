
def how_long_is_this_string(thing):
    return len(thing)

class StringMeasurer():
    def __init__(self):
        self.number_of_strings_measured = 0

    def measure_this_string(self, string):
        self.number_of_strings_measured = self.number_of_strings_measured+1
        return len(string)
