import json

from bottle import route, run, request


@route('/:name')
def index(name='World'):
    return '<b>Hello %s!</b>' % name


@route('/text', method='POST')
def post_text():
    data = request.json
    raw_text = data["text"]

    # toponyms should have a python dictionary or a json object already
    toponyms = extract_toponyms(raw_text)
    json_toponyms = json.dumps(toponyms)
    return json_toponyms


def extract_toponyms(raw_text):
    result = None
    # import modules and extract the toponyms here

    return result


run(host='localhost', port=8880)
