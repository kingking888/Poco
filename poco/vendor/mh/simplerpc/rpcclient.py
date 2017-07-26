# encoding=utf-8
from simplerpc import RpcBaseClient, Connection
from protocol import SimpleProtocolFilter
from simplesocket import SafeSocket
from asyncsocket import Client, init_loop


class SafeSocketConn(Connection):
    """docstring for SafeSocketConn"""
    def __init__(self, address):
        super(SafeSocketConn, self).__init__()
        self.s = SafeSocket(address=address)
        self.prot = SimpleProtocolFilter()

    def connect(self):
        self.s.connect()

    def send(self, msg):
        msg_bytes = self.prot.pack(msg)
        self.s.send(msg_bytes)

    def recv(self):
        msg_bytes = self.s.recv_nonblocking()
        return self.prot.input(msg_bytes)


class AsyncConn(Connection):
    """docstring for AsyncConn"""
    def __init__(self, address):
        super(AsyncConn, self).__init__()
        self.s = Client(address)
        self.prot = SimpleProtocolFilter()

    def connect(self):
        init_loop()

    def send(self, msg):
        msg_bytes = self.prot.pack(msg)
        self.s.say(msg_bytes)

    def recv(self):
        msg_bytes = self.s.read_message()
        return self.prot.input(msg_bytes)


class RpcClient(RpcBaseClient):
    """docstring for RpcClient"""
    def __init__(self, conn):
        super(RpcClient, self).__init__()
        self.conn = conn
        self.conn.connect()

    def call(self, func, *args, **kwargs):
        msg, cb = self.format_request(func, *args, **kwargs)
        self.conn.send(msg)
        return cb

    def update(self):
        data = self.conn.recv()
        if not data:
            return
        for msg in data:
            message_type, result = self.handle_message(msg)
            if message_type == self.REQUEST:
                self.conn.send(result)


if __name__ == '__main__':
    from pprint import pprint
    # conn = SafeSocketConn(("localhost", 5001))
    conn = AsyncConn(("localhost", 5001))
    c = RpcClient(conn)
    # simply call rpc
    c.call("foobar", foo="aaa", bar="bbb")
    # call rpc and wait for rpc result
    cb = c.call("foobar", foo="aaa", bar="bbb")
    r = cb.wait()
    # call rpc and register callback
    c.call("foobar", foo="aaa", bar="bbb").callback(pprint)
    # call rpc and register callback, then wait for callback result
    cb = c.call("foobar", foo="aaa", bar="bbb")
    cb.callback(pprint)
    cb.wait()
    # c.run()
    # run python console
    c.console_run({"c": c})