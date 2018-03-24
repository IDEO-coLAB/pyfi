# examples of how the imports we're testing work in python for sanity checking
# since there's name colision, uncomment one at a time to test.

# import MODULE

# import test_module
# print test_module.how_long_is_this_string('testthisstring')


# from MODULE import OBJECT

# from test_module import how_long_is_this_string, StringMeasurer
# print how_long_is_this_string('testhisstring')
# sm = StringMeasurer()
# print sm.measure_this_string('testthisstring')


# from PACKAGE.MODULE import OBJECT

from test_package.test_package_module import give_me_five
print(give_me_five())


# from PACKAGE import MODULE

# from test_package import test_package_module
# print test_package_module.give_me_five()


# from PACKAGE import OBJECT

# only works if we have
# from test_package_module import *
# in test_package/__init__.py
# from test_package import give_me_five
# print give_me_five()
