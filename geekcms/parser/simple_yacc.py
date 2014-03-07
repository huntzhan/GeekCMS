import ply.yacc as yacc


def p_lines_newline(p):
    'lines : NEWLINE lines line_atom'
    pass


def p_lines_expend(p):
    'lines : lines line_atom'
    pass


def p_lines_line_atom(p):
    'lines : line_atom'
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
