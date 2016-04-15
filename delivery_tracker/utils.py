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


def generate_table_for_popup(header, data):
    table = '<table class="popup_table">'
    if header:
        table += '<tr class="popup_table_row">'
        for head_col_name in header:
            table += '<th>%s</th>' % (head_col_name,)
        table += '</tr>'
    for row in data:
        table += '<tr class="popup_table_row">'
        for col in row:
            table += '<td>%s</td>' % (col,)
        table += '</tr>'

    table += '</table>'
    return table
