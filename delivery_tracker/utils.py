from random import SystemRandom
import string


def generate_password(length=8):
    choices = string.ascii_lowercase + string.ascii_uppercase + string.digits
    choices = choices.replace('o', '')
    choices = choices.replace('O', '')
    choices = choices.replace('0', '')
    choices = choices.replace('l', '')
    choices = choices.replace('I', '')
    choices = choices.replace('1', '')
    return ''.join(SystemRandom().choice(choices) for _ in range(length))