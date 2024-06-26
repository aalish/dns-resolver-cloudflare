from flask import Flask, request, jsonify
import dns_server
import threading
import uuid
from datetime import datetime
import json

app = Flask(__name__)

# Start the DNS server in a separate thread
dns_thread = threading.Thread(target=dns_server.start_dns_server)
dns_thread.daemon = True
dns_thread.start()

# File to store DNS records
DNS_RECORDS_FILE = 'dns_records.json'

def load_dns_records():
    try:
        with open(DNS_RECORDS_FILE, 'r') as file:
            dns_server.dns_records = json.load(file)
    except FileNotFoundError:
        dns_server.dns_records = {}

def save_dns_records():
    with open(DNS_RECORDS_FILE, 'w') as file:
        json.dump(dns_server.dns_records, file)

load_dns_records()

@app.route('/client/v4/zones/zoneid/dns_records', methods=['GET'])
def list_dns_records():
    return jsonify(list(dns_server.dns_records.values()))

@app.route('/client/v4/zones/zoneid/dns_records', methods=['POST'])
def create_dns_record():
    data = request.json
    record_id = uuid.uuid4().hex
    created_on = datetime.utcnow().isoformat() + "Z"
    record = {
        "id": record_id,
        "zone_id": "your_zone_id",
        "zone_name": "iagon.io",
        "name": data['name'],
        "type": "A",
        "content": data['content'],
        "proxiable": True,
        "proxied": True,
        "ttl": 1,
        "locked": False,
        "meta": {
            "auto_added": False,
            "managed_by_apps": False,
            "managed_by_argo_tunnel": False
        },
        "comment": None,
        "tags": [],
        "created_on": created_on,
        "modified_on": created_on
    }
    dns_server.dns_records[record_id] = record
    save_dns_records()
    return jsonify({"result": record, "success": True, "errors": [], "messages": []}), 201

@app.route('/client/v4/zones/zoneid/dns_records/<record_id>', methods=['DELETE'])
def delete_dns_record(record_id):
    if record_id in dns_server.dns_records:
        del dns_server.dns_records[record_id]
        save_dns_records()
        return jsonify({"result": {"id": record_id}, "success": True, "errors": [], "messages": []}), 200
    else:
        return jsonify({"result": {}, "success": False, "errors": [{"code": 404, "message": "Record not found"}], "messages": []}), 404

@app.route('/client/v4/zones/zoneid/dns_records/<record_id>', methods=['PATCH'])
def update_dns_record(record_id):
    if record_id in dns_server.dns_records:
        data = request.json
        record = dns_server.dns_records[record_id]
        record.update({
            "name": data.get("name", record["name"]),
            "content": data.get("content", record["content"]),
            "proxied": data.get("proxied", record["proxied"]),
            "type": data.get("type", record["type"]),
            "ttl": data.get("ttl", record["ttl"]),
            "modified_on": datetime.utcnow().isoformat() + "Z",
        })
        save_dns_records()
        return jsonify({"result": record, "success": True, "errors": [], "messages": []}), 200
    else:
        return jsonify({"result": {}, "success": False, "errors": [{"code": 404, "message": "Record not found"}], "messages": []}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
