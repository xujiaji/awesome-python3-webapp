# def application(environ, start_response):
#     start_response('200 OK', [('Content-Type', 'text/html')])
#     print(environ)
#     body = '<h1>Hello, %s!</h1>' % (environ['PATH_INFO'][1:] or 'web')
#     return [body.encode('utf-8')]
#
#
# from wsgiref.simple_server import make_server
#
# httpd = make_server('', 8000, application)
# print('Serving Http on port 8000..')
# httpd.serve_forever()


import send_email

send_email.send_comment_email('demofamilies@gmail.com', '一条留言', "/blog/0015279355359080a648f9223784255ba6199a8892e44c0000")