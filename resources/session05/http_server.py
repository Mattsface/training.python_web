import socket
import sys
import os
import mimetypes


def response_ok(content, mime_type):
    """returns a basic HTTP response"""
    resp = []
    resp.append("HTTP/1.1 200 OK")
    resp.append("Content-Type: {}".format(mime_type))
    resp.append("")
    resp.append(content)
    return "\r\n".join(resp)


def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 405 Method Not Allowed")
    resp.append("")
    return "\r\n".join(resp)


def resolve_uri(uri):
    """
    Function that handles looking resources on disk using the URI.
    return content and type
    """
    webroot = "webroot"
    path = os.path.join(webroot + uri)
    if os.path.isdir(path):
        ls = "\n".join(os.listdir(path))
        return ls, 'text/plain'
    elif os.path.isfile(path):
        mime_type, encoding = mimetypes.guess_type(path)
        with open(path, 'rb') as f:
            page = f.read()
        return page, mime_type
    else:
        raise ValueError("Could not find resource")


def response_not_found():
    """
    returns a 404 response if the resource does not exist.
    """
    resp = []
    resp.append("HTTP/1.1 404 Not Found")
    resp.append("Content-Type: text/plain")
    resp.append("")
    resp.append("404 Not Found")
    return "\r\n".join(resp)


def parse_request(request):
    first_line = request.split(""
                               "\r\n", 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    print >>sys.stderr, 'request is okay'
    return uri


def server():
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print >>sys.stderr, "making a server on %s:%s" % address
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print >>sys.stderr, 'waiting for a connection'
            conn, addr = sock.accept() # blocking
            try:
                print >>sys.stderr, 'connection - %s:%s' % addr
                request = ""
                while True:
                    data = conn.recv(1024)
                    request += data
                    if len(data) < 1024 or not data:
                        break

                try:
                    uri = parse_request(request)
                    content, mime_type = resolve_uri(uri)
                except NotImplementedError:
                    response = response_method_not_allowed()
                except ValueError:
                    response = response_not_found()
                else:
                    response = response_ok(content, mime_type)


                print >>sys.stderr, 'sending response'
                conn.sendall(response)
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
