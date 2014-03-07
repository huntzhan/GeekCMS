

class PluginRel:

    def __init__(self, is_left_rel, degree):
        self.is_left_rel = is_left_rel
        self.degree = degree

    def __repr__(self):
        return 'PluginRel({}, {})'.format(self.is_left_rel, self.degree)


class PluginExpr:

    HEAD = 'HEAD'
    TAIL = 'TAIL'

    def __init__(self, *,
                 left_operand=None, right_operand=None, relation=None):
        # HEAD and TAIL are set for None value.
        self.left_operand = left_operand or self.HEAD
        self.right_operand = right_operand or self.TAIL
        # if rel is None, which means the expression's order is not defined.
        self.relation = relation

    def __repr__(self):
        text = '<PluginExpr left: {}, right: {}, is_left_rel: {}>'.format(
            self.left_operand,
            self.right_operand,
            self.relation,
        )
        return text


class ErrorCollector:
    pass
