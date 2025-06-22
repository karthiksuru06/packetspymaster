from flask import Flask, render_template, Response, request, send_file
from analyzer import PacketSniffer
import threading
import time
import json
import csv
import io

app = Flask(__name__)
sniffer = PacketSniffer()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    protocol = request.form.get("protocol")
    sniffer.set_filter(protocol)
    sniffer.start()
    return "✅ Started capturing packets..."

@app.route("/stop", methods=["POST"])
def stop():
    sniffer.stop()
    return "🛑 Packet capture stopped."

@app.route("/stream")
def stream():
    def generate():
        while sniffer.running:
            if sniffer.packets:
                data = json.dumps(sniffer.packets[-1])
                yield f"data: {data}\n\n"
            time.sleep(0.5)
    return Response(generate(), mimetype="text/event-stream")

@app.route("/download/<format>")
def download(format):
    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp", "src", "dst", "protocol", "info"])
        writer.writeheader()
        writer.writerows(sniffer.packets)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=packets.csv"}
        )
    else:
        return Response(
            json.dumps(sniffer.packets, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=packets.json"}
        )

@app.route('/clear', methods=['POST'])
def clear_logs():
    # Clear in-memory packets
    sniffer.packets.clear()

    # Overwrite CSV and JSON files
    with open('packets.json', 'w') as jf:
        json.dump([], jf)

    with open('packets.csv', 'w', newline='') as cf:
        writer = csv.writer(cf)
        writer.writerow(["timestamp", "src", "dst", "protocol", "info"])  # headers

    return "✅ Logs cleared.", 200

if __name__ == "__main__":
    app.run(debug=True)
