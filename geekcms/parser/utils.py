

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


class _ContainerError:

    def __init__(self, name):
        self._name = name

    def __get__(self, instance, cls):
        container_name = cls._get_message_container(self._name)
        container = getattr(cls, container_name)
        return bool(container)


class ErrorCollector:

    lex_error = _ContainerError('lex')
    yacc_error = _ContainerError('yacc')

    theme_lex_error = {}
    theme_yacc_error = {}
    _lex_message_container = []
    _yacc_message_container = []

    @classmethod
    def _get_message_container(cls, name):
        attr = '_{}_message_container'.format(name)
        return attr

    @classmethod
    def _get_theme_error_mapping(cls, name):
        attr = 'theme_{}_error'.format(name)
        return attr

    @classmethod
    def _clean_up(cls, name):
        attr = cls._get_message_container(name)
        setattr(cls, attr, list())

    @classmethod
    def _add_message(cls, name, message):
        attr = cls._get_message_container(name)
        getattr(cls, attr).append(message)

    @classmethod
    def add_lex_message(cls, message):
        cls._add_message('lex', message)

    @classmethod
    def add_yacc_message(cls, message):
        cls._add_message('yacc', message)

    @classmethod
    def _archive(cls, name, theme):
        # resolve name.
        mapping_name = cls._get_theme_error_mapping(name)
        container_name = cls._get_message_container(name)
        # get obj.
        mapping = getattr(cls, mapping_name)
        container = getattr(cls, container_name)
        # archive and clean up.
        mapping[theme] = container
        cls._clean_up(name)

    @classmethod
    def archive_yacc_messages(cls, theme):
        cls._archive('yacc', theme)

    @classmethod
    def archive_lex_messages(cls, theme):
        cls._archive('lex', theme)
