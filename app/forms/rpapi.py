import re

from flask import render_template
from wtforms import Form, StringField, SubmitField, validators, RadioField, ValidationError

# TODO: finish this list
varnish_domains = ['www.bethel.edu']


#######################################################
#                   Custom Validators                 #
#######################################################

def valid_purge_uri():

    def _uri(form, field):
        # This regex should match anything from www.google.com to https://cdn1.bethel.edu/resize/
        uri_pattern = re.compile(r'^(https?://)?([A-Za-z0-9-]+\.[A-Za-z0-9-]+\.[A-Za-z0-9-]+)(/.*)?$')

        # First, assert that the value submitted is syntactically a URI
        result = uri_pattern.search(field.data)
        if result is None:
            raise ValidationError('The path submitted is not a valid URI')

        # Second, assert that the domain is one of the domains behind Varnish
        domain = result.group(2)
        if domain not in varnish_domains:
            raise ValidationError('%s isn\'t behind Varnish' % domain)

        # Finally, assert that the URL is at least '/'
        url = result.group(3)
        if url is None:
            raise ValidationError('The URL at the end of the path needs to have at least a "/" at the beginning')

    return _uri


def valid_ban_syntax():

    def _parse(form, field):
        field_data = field.data

        # Because someone will inevitably try to use an OR instead of just ANDs, I'm adding this block of code
        # before the syntax check.
        or_pattern = re.compile(r'\|\|')
        result = or_pattern.search(field_data)
        if result:
            raise ValidationError('Varnish Bans only support doing logical ANDs, not ORs. '
                                  'You\'ll have to submit multiple Bans to achieve an OR.')

        _recursive_syntax_check(field_data.strip())

    def _recursive_syntax_check(expression):
        and_pattern_result = re.compile(r'(.*?)&&(.*)').search(expression)

        if and_pattern_result is not None:
            # If expression contains '&&', then it's a compound expression
            left_comparison = and_pattern_result.group(1).strip()
            right_expression = and_pattern_result.group(2).strip()

            if right_expression == '':
                raise ValidationError('Ban expressions can\'t end with an &&')

            _recursive_syntax_check(left_comparison)
            _recursive_syntax_check(right_expression)
        else:
            # If '&&' isn't in the expression, then it has been reduced down to a single comparison
            comparison = re.compile(r'(.*?)\s+(.*?)\s+(.*)').search(expression)

            if comparison is None:
                raise ValidationError('Too few arguments in "%s". Make sure that they\'re all '
                                      'separated by at least one space' % expression)

            field = comparison.group(1)
            field_check = re.compile(r'((req|obj)\.(http\.[A-Za-z0-9-]+)|req\.url|obj\.status)').search(field)
            if field_check is None:
                raise ValidationError('"%s" is not a valid Field for a Ban expression' % field)

            operator = comparison.group(2)
            valid_operators = ['==', '!=', '~', '!~']  # r'(!?~|[!=]=)'
            if operator not in valid_operators:
                raise ValidationError('"%s" is not a valid Operator for a Ban expression. The only operators '
                                      'allowed are %s' % (operator, str(valid_operators)))

            arg = comparison.group(3)
            arg_has_whitespace = re.compile(r'\s+').search(arg)
            if arg_has_whitespace is not None:
                raise ValidationError('"%s" contains whitespace, which is not allowed for a Ban\'s argument' % arg)

            arg_has_quotes = re.compile(r'[\'"]').search(arg)
            if arg_has_quotes is not None:
                raise ValidationError('"%s" contains either an apostrophe or quotation mark, which are not allowed '
                                      'for a Ban\'s argument' % arg)

    return _parse


#######################################################
#                     Custom Forms                    #
#######################################################

# These forms were adapted from Classifieds

class RenderableForm(Form):
    def render_to_html(self):
        return render_template('forms/generic_form.html', fields=self._fields.items())

    def get(self, key):
        return self._fields.get(key).data


class PurgeRefreshForm(RenderableForm):
    uri = StringField('Path:', [validators.DataRequired(), valid_purge_uri()])
    api_action = RadioField('Action:', [validators.DataRequired()],
                            choices=[('purge', 'Purge'), ('refresh', 'Refresh')])
    submit = SubmitField('Go')


class SimpleBanForm(RenderableForm):
    # Because Bans are regex-compatible, it's not practical to do any type of data validation.
    # As long as there's a value submitted, we can pass it on to the Refresh/Purge API.
    host = StringField('Domain:', [validators.DataRequired()])
    url = StringField('URL:', [validators.DataRequired()])
    submit = SubmitField('Ban')


class AdvancedBanForm(RenderableForm):
    expression = StringField('Custom Ban expression:', [validators.DataRequired(), valid_ban_syntax()])
    submit = SubmitField('Ban')
