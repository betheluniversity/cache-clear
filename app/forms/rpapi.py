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

    def _ban_syntax(form, field):
        # The regex for Ban expression syntax is a bit of a monster, and gets explained in
        # https://github.com/betheluniversity/cache-clear/issues/2
        syntax_pattern = re.compile(r'((req|obj)\.(url|status|http\.[A-Za-z0-9-]+)\s?(!?~|[!=]=)\s?([^ \n]+)(\s?&&\s?(?=(req|obj)\.(url|status|http\.[A-Za-z0-9-]+)\s?(!?~|[!=]=)\s?([^ \n]+)))?)+')

        # If the value submitted matches that regex, then it is very likely to be syntactically valid as a Ban.
        result = syntax_pattern.search(field.data)
        if result is None:
            raise ValidationError('That Ban expression wouldn\'t be valid')

    return _ban_syntax


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
