from html import escape
from urllib.parse import parse_qs

html = """
<html>
  <body>
    <h1>Hello, world!</h1>
    <form method="post" action="">
        <p>
           Age: <input type="text" name="age" value="%(age)s">
        </p>
        <p>
            <input type="submit" value="Submit">
        </p>
    </form>

    <h3>GET parameters from request:</h3>
    %(get_params)s

    <h3>POST parameters from request:</h3>
    %(post_params)s
  </body>
</html>
"""

def hello_world(environ, start_response):
    get_dict = parse_qs(environ['QUERY_STRING'])
    if get_dict:
        get_params = ('<p>' +
                      '<p></p>'.join(key + '=' + ' & '.join(value for value in get_dict[key])
                                     for key in get_dict.keys()) +
                      '</p>')
    else:
        get_params = ''
    
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = environ['wsgi.input'].read(request_body_size)
    post_dict = parse_qs(request_body)
    post_params = ('<p>' +
                   '<p></p>'.join(key.decode() + '=' + ' & '.join(value.decode() for value in post_dict[key])
                                  for key in post_dict.keys()) +
                   '</p>')

    age = post_dict.get(b'age', [b''])[0].decode()

    response_body = html % {
        'age': age,
        'get_params': get_params,
        'post_params': post_params,
    }

    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(response_body)))
    ]
    start_response(status, response_headers)

    return [response_body.encode()]
