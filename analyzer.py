from scapy.all import sniff, IP, TCP, UDP, ICMP
from datetime import datetime
import threading

class PacketSniffer:
    def __init__(self):
        self.running = False
        self.thread = None
        self.packets = []
        self.filter_protocol = None

    def set_filter(self, protocol):
        self.filter_protocol = protocol

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.sniff_packets)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def sniff_packets(self):
        sniff(prn=self.packet_callback, store=False, filter="ip", stop_filter=lambda _: not self.running)

    def packet_callback(self, packet):
        if IP in packet:
            proto = packet.proto
            protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
            protocol = protocol_map.get(proto, "Other")

            if self.filter_protocol and protocol != self.filter_protocol:
                return

            packet_info = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "src": packet[IP].src,
                "dst": packet[IP].dst,
                "protocol": protocol,
                "info": ""
            }

            if TCP in packet:
                packet_info["info"] = f"TCP {packet[TCP].sport} → {packet[TCP].dport}"
            elif UDP in packet:
                packet_info["info"] = f"UDP {packet[UDP].sport} → {packet[UDP].dport}"
            elif ICMP in packet:
                packet_info["info"] = "ICMP Packet"

            self.packets.append(packet_info)
