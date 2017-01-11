

# Will make sure the given number 'number' wont be bigger than max-number and not smaller than minimum number
def clamp(number, minimum_number, max_number):
    return max(min(max_number, number), minimum_number)


# Will find a given string string between two other strings
# For example find_between("123abc456", "123, "456") will return "abc"
def find_between(input_string, first_string, last_string):
    try:
        start = input_string.index(first_string) + len(first_string)
        end = input_string.index(last_string, start)
        return input_string[start:end]
    except ValueError:
        return ""
