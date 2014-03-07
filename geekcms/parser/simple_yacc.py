import os
import ply.yacc as yacc
from .simple_lex import tokens


def p_start_newline(p):
    'start : NEWLINE lines'
    pass


def p_start_nonewline(p):
    'start : lines'
    pass


def p_lines_expend(p):
    'lines : lines line_atom'
    pass


def p_lines_line_atom(p):
    'lines :'
    pass


def p_line_atom(p):
    'line_atom : plugin_expr NEWLINE'
    pass


def p_plugin_expr_binary(p):
    'plugin_expr : plugin_name relation plugin_name'
    pass


def p_plugin_expr_left(p):
    'plugin_expr : plugin_name relation'
    pass


def p_plugin_expr_right(p):
    'plugin_expr : relation plugin_name'
    pass


def p_plugin_expr_none(p):
    'plugin_expr : plugin_name'
    pass


def p_relation_left(p):
    'relation : left_rel'
    pass


def p_relation_right(p):
    'relation : right_rel'
    pass


def p_left_rel_nodegree(p):
    'left_rel : LEFT_OP'
    pass


def p_left_rel_degree(p):
    'left_rel : LEFT_OP DEGREE'
    pass


def p_right_rel_nodegree(p):
    'right_rel : RIGHT_OP'
    pass


def p_right_rel_degree(p):
    'right_rel : DEGREE RIGHT_OP'
    pass


def p_plugin_name(p):
    'plugin_name : IDENTIFIER'
    pass


def p_error(p):
    print("Syntax Error: '{}' in line {}".format(p.value, p.lineno))
    discard = [p.value]
    while True:
        token = yacc.token()
        if token and token.type != 'NEWLINE':
            discard.append(token.value)
            continue
        else:
            val = '[NEWLINE]' if token else '[EOL]'
            discard.append(val)
            break
    print('Discard: ', ''.join(discard))
    yacc.restart()


parser = yacc.yacc(
    # debug=0,
    optimize=1,
    outputdir=os.path.dirname(__file__),
)
