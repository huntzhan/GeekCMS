import os
import re
import ply.lex as lex

tokens = (
    'IDENTIFIER',
    'LEFT_OP',
    'RIGHT_OP',
    'DEGREE',
    'NEWLINE',
)

plugin_name = r'[^\d\W]\w*'
full_name = r'({0}\.)?{0}'.format(plugin_name)
t_IDENTIFIER = full_name

t_LEFT_OP = r'<<'
t_RIGHT_OP = r'>>'
t_DEGREE = r'[^0\D]\d*|0+'


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t


t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'


def t_error(t):
    print("Illegal Character: '{}' in line {}".format(t.value[0], t.lineno))
    t.lexer.skip(1)

lexer = lex.lex(
    # debug=0,
    optimize=1,
    reflags=re.ASCII,
    outputdir=os.path.dirname(__file__),
)
