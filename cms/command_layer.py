"""
{1}
{0}

{2}

{3}
"""

import os
import re

class CommandProcessor:

    def doc_elements(self):
        """
        should always return triple-tuple, (usage, option, explanation)
        fullfilling the rules of docopt,
        """
        pass

    def check(self, args):
        """
        See if the processor can handler args or not.
        """
        pass

    def run(self):
        """
        Handle the command.
        """
        pass


def process_docopt_doc(settings):
    program_name = 'GeekCMS'
    usages = []
    options = []
    explanations = []

    for command_processor in settings.command_processors:
        usage, option, explanation = command_processor.doc_elements()

        indent4 = ' ' * 4
        indent2 = ' ' * 2
        indent1 = ' ' * 1
        assert usage
        usages.append(indent4 + program_name + indent1 + usage)
        if option:
            options.append(indent4 + option)
        if explanation:
            explanations.append(indent4 + usage.lstrip(program_name)\
                                + indent2 + explanation)

    usage_text = ''
    option_text = ''
    explanation_text = ''
    if usages:
        usage_text = 'Usage:{0}{1}'.format(
            os.linesep,
            os.linesep.join(usages)
        )
    if options:
        option_text = 'Options:{0}{1}'.format(
            os.linesep,
            os.linesep.join(options)
        )
    if explanations:
        explanation_text = 'Explanation:{0}{1}'.format(
            os.linesep,
            os.linesep.join(explanations)
        )

    doc = __doc__.format(
        indent4 + program_name,
        usage_text,
        option_text,
        explanation_text,
    )

    return re.sub(os.linesep + r'{2,999}', os.linesep * 2, doc)


def process_args(settings, args):
    for command_processor in settings.command_processors:
        if command_processor.check(args):
            # I'm feeling good.
            command_processor.run()
            return False
    return True

