from dnslib.server import DNSServer, BaseResolver, DNSLogger
from dnslib import RR, QTYPE, A, DNSRecord
import socket
import uuid

# Simulated DNS records storage
dns_records = {}

class DynamicResolver(BaseResolver):
    def __init__(self, forwarders):
        self.forwarders = forwarders

    def resolve(self, request, handler):
        reply = request.reply()
        qname = str(request.q.qname).rstrip('.')
        qtype = QTYPE[request.q.qtype]

        found = False
        if qtype == 'A':
            for record in dns_records.values():
                if record['name'] == qname:
                    reply.add_answer(RR(qname, QTYPE.A, rdata=A(record['content'])))
                    found = True
                    break

        if not found:
            # Forward the request to the forwarder
            for forwarder in self.forwarders:
                try:
                    response = self.forward_query(request, forwarder)
                    if response:
                        reply.add_answer(*response.rr)
                        break
                except Exception as e:
                    print(f"Failed to forward query to {forwarder}: {e}")

        return reply

    def forward_query(self, request, forwarder):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        try:
            sock.sendto(request.pack(), (forwarder, 53))
            data, _ = sock.recvfrom(4096)
            return DNSRecord.parse(data)
        except Exception as e:
            print(f"Error forwarding query: {e}")
        finally:
            sock.close()

def start_dns_server():
    forwarders = ['1.1.1.1', '8.8.8.8']
    resolver = DynamicResolver(forwarders)
    logger = DNSLogger()
    server = DNSServer(resolver, port=53, address="0.0.0.0", logger=logger)
    server.start_thread()

if __name__ == '__main__':
    start_dns_server()
    while True:
        pass
