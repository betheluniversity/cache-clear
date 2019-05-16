# Globals
import hashlib
import re
import subprocess

from app import app


def clear_image_cache(image_path):
    # /academics/faculty/images/lundberg-kelsey.jpg"
    # Make sure image path starts with a slash
    if not image_path.startswith('/'):
        image_path = '/%s' % image_path

    resp = []

    def path_on_filesystem(path):
        path = re.sub(":", "%3A", path)
        digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
        return "%s/%s/%s" % (
            app.config['THUMBOR_STORAGE_LOCATION'].rstrip('/'),
            digest[:2],
            digest[2:]
        )

    for prefix in ['http://www.bethel.edu', 'https://www.bethel.edu',
                   'http://staging.bethel.edu', 'https://staging.bethel.edu']:
        path = prefix + image_path
        resp.append(path)
        encrypted_path = path_on_filesystem(path)
        resp.append(encrypted_path)

        # remove the file at the path
        subprocess.call(['rm', encrypted_path])

    cmd = 'find %s -wholename "*/smart/*%s"' % (app.config['THUMBOR_RESULT_STORAGE_LOCATION'], image_path)
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    results = sp.communicate()[0].split()

    matches = ""

    for result_path in results:
        sp2 = subprocess.Popen('rm ' + result_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # response = subprocess.call(['rm', result_path])
        response = sp2.communicate()
        if response == ('', ''):
            matches += "Deleted resize at \"%s\"\n" % result_path
        else:
            matches += "ERROR: Couldn't delete resize at \"%s\": \"%s\"\n" % (result_path, response[0])

    matches += "\n"

    # this iterates through resp two items at a time
    for x, y in zip(*[iter(resp)] * 2):
        matches += "Deleted original of \"%s\" at \n\"%s\"\n" % (str(x), str(y))

    return matches
