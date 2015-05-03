import socket
import sys


def client(msg, log_buffer=sys.stderr):
    server_address = ('localhost', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print >>log_buffer, 'connecting to {0} port {1}'.format(*server_address)
    sock.connect(server_address)
    try:
        print >>log_buffer, 'sending "{0}"'.format(msg)
        sock.sendall(msg)
        msg_size = len(msg)
        msg_received = 0
        while msg_size > msg_received:
            chunk = sock.recv(16)
            msg_received += len(chunk)
            print >>log_buffer, 'received "{0}"'.format(chunk)
    finally:
        # TODO: after you break out of the loop receiving echoed chunks from
        #       the server you will want to close your client socket.
        print >>log_buffer, 'closing socket'
        sock.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usg = '\nusage: python echo_client.py "this is my message"\n'
        print >>sys.stderr, usg
        sys.exit(1)

    msg = sys.argv[1]
    client(msg)
