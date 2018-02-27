
def how_long_is_this_string(thing):
    return 'there are ' + str(len(thing)) + ' characters.'

class StringMeasurer():
    def __init__(self):
        self.number_of_strings_measured = 0

    def measure_this_string(self, string):
        self.number_of_strings_measured = self.number_of_strings_measured+1
        return 'there are ' + str(len(string)) + ' characters.'
