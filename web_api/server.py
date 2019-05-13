from bottle import route, run, request


@route('/:name')
def index(name='World'):
    return '<b>Hello %s!</b>' % name


@route('/feedback', method='POST')
def feedback():
    data = request.json
    print(data)


run(host='localhost', port=8880)
