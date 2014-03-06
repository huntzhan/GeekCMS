import re
import ply.lex as lex

tokens = (
    'PLUGIN_ID',
    'LEFT_REL',
    'RIGHT_REL',
    'DEGREE',
    'NEWLINE',
)

plugin_name = r'[^\d\W]\w*'
full_name = r'({0}\.)?{0}'.format(plugin_name)
t_PLUGIN_ID = full_name

t_LEFT_REL = r'<<'
t_RIGHT_REL = r'>>'
t_DEGREE = r'[^0\D]\d*|0+'


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t


t_ignore = ' \t'


def t_error(t):
    raise Exception('Illegal: {}'.format(t.value[0]))

lexer = lex.lex(reflags=re.ASCII)
