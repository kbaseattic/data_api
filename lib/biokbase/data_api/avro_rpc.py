"""
Put all the boilerplate and convenience code for Avro RPC
servers in one module.

Usage:
   from biokbase.data_api import avro_rpc
   avro_rpc.run_service(<ServiceClass>)

"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/20/15'

# Imports

# Stdlib
import logging
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
# Third-party
import avro.ipc as ipc
# Local
from biokbase.data_api.util import get_logger, log_start, log_end, log_event

# Logging

_log = get_logger('data_api.avro_rpc')

# Constants

AVRO_DEFAULT_PORT = 9090

# Classes and functions

class AvroRPCServer(HTTPServer):
    def __init__(self, server_addr, service_class):
        handler_class = AvroRPCHandler
        HTTPServer.__init__(self, server_addr, handler_class)
        self.responder = service_class()

class AvroRPCHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        t0 = log_start(_log, 'do_POST')
        call_request_reader = ipc.FramedReader(self.rfile)
        call_request = call_request_reader.read_framed_message()
        resp_body = self.server.responder.respond(call_request)
        self.send_response(200)
        self.send_header('Content-Type', 'avro/binary')
        self.end_headers()
        resp_writer = ipc.FramedWriter(self.wfile)
        resp_writer.write_framed_message(resp_body)
        log_end(_log, t0, 'do_POST')

def run_service(service_class, host='localhost', port=AVRO_DEFAULT_PORT):
    server_addr = (host, port)
    server = AvroRPCServer(server_addr, service_class)
    server.allow_reuse_address = True
    t0 = log_start(_log, 'avro.server.run')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log_event(_log, 'avro.server.run.interrupted', level=logging.WARN)
        pass
    log_end(_log, t0, 'avro.server.run')
