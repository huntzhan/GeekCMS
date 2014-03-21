import os
from ply import yacc
from .simple_lex import tokens
from .utils import PluginRel
from .utils import PluginExpr
from .utils import ErrorCollector


def p_start(p):
    '''start : NEWLINE lines end
             | lines end'''
    if len(p) == 4:
        lines = p[2]
        end = p[3]
    elif len(p) == 3:
        lines = p[1]
        end = p[2]
    # check end is avaliable or not
    if end:
        lines.append(end)
    p[0] = lines


def p_end(p):
    '''end : plugin_expr
           | empty'''
    p[0] = p[1]


def p_lines_expend(p):
    '''lines : lines line_atom
             | empty'''
    if len(p) == 2:
        p[0] = []
    elif len(p) == 3:
        # init a list if lines is None
        plugin_set = p[1]
        single_plugin = p[2]
        plugin_set.append(single_plugin)
        p[0] = plugin_set


def p_line_atom(p):
    'line_atom : plugin_expr NEWLINE'
    p[0] = p[1]


def p_plugin_expr_binary(p):
    'plugin_expr : plugin_name relation plugin_name'
    p[0] = PluginExpr(
        left_operand=p[1],
        relation=p[2],
        right_operand=p[3],
    )


def p_plugin_expr_left(p):
    'plugin_expr : plugin_name relation'
    p[0] = PluginExpr(
        left_operand=p[1],
        relation=p[2],
    )


def p_plugin_expr_right(p):
    'plugin_expr : relation plugin_name'
    p[0] = PluginExpr(
        relation=p[1],
        right_operand=p[2],
    )


def p_plugin_expr_none(p):
    'plugin_expr : plugin_name'
    p[0] = PluginExpr(
        left_operand=p[1],
    )


def p_relation(p):
    '''relation : left_rel
                | right_rel'''
    p[0] = p[1]


def p_left_rel(p):
    '''left_rel : LEFT_OP
                | LEFT_OP DEGREE'''
    if len(p) == 2:
        rel = PluginRel(True, 0)
    elif len(p) == 3:
        rel = PluginRel(True, int(p[2]))
    p[0] = rel


def p_right_rel(p):
    '''right_rel : RIGHT_OP
                 | DEGREE RIGHT_OP'''
    if len(p) == 2:
        rel = PluginRel(False, 0)
    elif len(p) == 3:
        rel = PluginRel(False, int(p[1]))
    p[0] = rel


def p_plugin_name(p):
    'plugin_name : IDENTIFIER'
    p[0] = p[1]


def p_empty(p):
    'empty :'
    # in order not to fix up with plugin_expr
    p[0] = None


def p_error(p):
    # print("Syntax Error: '{}' in line {}".format(p.value, p.lineno))
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
    # print('Discard: ', ''.join(discard))
    ErrorCollector.add_yacc_message(
        (p.value, p.lineno, ''.join(discard)),
    )
    yacc.restart()


parser = yacc.yacc(
    debug=0,
    optimize=1,
    outputdir=os.path.dirname(__file__),
)
