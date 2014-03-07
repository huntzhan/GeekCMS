# lextab.py. This file automatically created by PLY (version 3.4). Don't edit!
_tabversion   = '3.4'
_lextokens    = {'IDENTIFIER': 1, 'LEFT_OP': 1, 'RIGHT_OP': 1, 'DEGREE': 1, 'NEWLINE': 1}
_lexreflags   = 256
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_NEWLINE>\\n+)|(?P<t_IDENTIFIER>([^\\d\\W]\\w*\\.)?[^\\d\\W]\\w*)|(?P<t_DEGREE>[^0\\D]\\d*|0+)|(?P<t_ignore_COMMENT>\\#.*)|(?P<t_LEFT_OP><<)|(?P<t_RIGHT_OP>>>)', [None, ('t_NEWLINE', 'NEWLINE'), (None, 'IDENTIFIER'), None, (None, 'DEGREE'), (None, None), (None, 'LEFT_OP'), (None, 'RIGHT_OP')])]}
_lexstateignore = {'INITIAL': ' \t'}
_lexstateerrorf = {'INITIAL': 't_error'}
