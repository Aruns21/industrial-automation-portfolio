import socket
import struct

HOST = "127.0.0.1"
PORT = 502

def read_coils(start_addr, count):
    # Build a Modbus TCP (MBAP header + PDU) "Read Coils" (function code 0x01) request
    transaction_id = 1
    protocol_id = 0
    unit_id = 1
    function_code = 0x01
    pdu = struct.pack(">BHH", function_code, start_addr, count)
    length = len(pdu) + 1  # +1 for unit_id
    mbap = struct.pack(">HHHB", transaction_id, protocol_id, length, unit_id)
    request = mbap + pdu

    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        sock.sendall(request)
        response = sock.recv(256)

    # Response: MBAP(7 bytes) + function_code(1) + byte_count(1) + coil_bytes
    byte_count = response[8]
    coil_bytes = response[9:9 + byte_count]
    bits = []
    for byte in coil_bytes:
        for i in range(8):
            bits.append((byte >> i) & 1)
    return bits[:count]

if __name__ == "__main__":
    coils = read_coils(0, 4)
    labels = ["StartButton", "StopButton", "LevelHighSensor", "LevelLowSensor"]
    print("Connected to Modbus TCP server at", HOST, ":", PORT)
    for label, value in zip(labels, coils):
        print(f"  {label:20s} = {bool(value)}")
