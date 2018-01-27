
# Utility methods
def tf_val(number):
    """ Convert 0 to False and 1 (or any other value) to True """
    return number != 0


def num_val(bool_val):
    """ Convert True to 1 and False to 0 """
    return 1 if bool_val else 0
