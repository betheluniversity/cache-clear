# Imports from Python global packages

# Imports from packages installed from requirements.txt
from flask import render_template, request
from flask_classy import FlaskView, route
from werkzeug.datastructures import ImmutableMultiDict

# Imports from elsewhere in this project
from app.controllers.thumbor import clear_image_cache


class ThumborView(FlaskView):

    def index(self):
        return render_template('thumbor.html')

    @route('/submit', methods=['POST'])
    def submit(self):
        form = request.form
        if isinstance(form, ImmutableMultiDict):
            form_data = form.to_dict()
        else:
            form_data = {}

        cleared_path = form_data['path']
        matches = clear_image_cache(cleared_path)

        return render_template('thumbor_success.html', **locals())
