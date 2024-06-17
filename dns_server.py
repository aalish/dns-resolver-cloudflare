from dnslib.server import DNSServer, BaseResolver, DNSLogger
from dnslib import RR, QTYPE, A
import uuid

# Simulated DNS records storage
dns_records = {}

class DynamicResolver(BaseResolver):
    def resolve(self, request, handler):
        reply = request.reply()
        qname = str(request.q.qname).rstrip('.')
        qtype = QTYPE[request.q.qtype]

        if qtype == 'A' and qname in [record['name'] for record in dns_records.values()]:
            for record in dns_records.values():
                if record['name'] == qname:
                    reply.add_answer(RR(qname, QTYPE.A, rdata=A(record['content'])))
                    break

        return reply

def start_dns_server():
    resolver = DynamicResolver()
    logger = DNSLogger()
    server = DNSServer(resolver, port=53, address="127.0.0.1", logger=logger)
    server.start_thread()

if __name__ == '__main__':
    start_dns_server()
    while True:
        pass
