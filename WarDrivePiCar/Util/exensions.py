

# Will make sure the given number 'number' wont be bigger than max-number and not smaller than minimum number
def clamp(number, minimum_number, max_number):
    return max(min(max_number, number), minimum_number)
