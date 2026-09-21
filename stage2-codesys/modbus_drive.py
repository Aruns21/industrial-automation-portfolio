import socket
import struct
import time

HOST = "127.0.0.1"
PORT = 502

def _txn(pdu):
    transaction_id = 1
    protocol_id = 0
    unit_id = 1
    length = len(pdu) + 1
    mbap = struct.pack(">HHHB", transaction_id, protocol_id, length, unit_id)
    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        sock.sendall(mbap + pdu)
        return sock.recv(256)

def write_coil(addr, value):
    pdu = struct.pack(">BHH", 0x05, addr, 0xFF00 if value else 0x0000)
    _txn(pdu)

def read_bits(function_code, start_addr, count):
    pdu = struct.pack(">BHH", function_code, start_addr, count)
    response = _txn(pdu)
    byte_count = response[8]
    coil_bytes = response[9:9 + byte_count]
    bits = []
    for byte in coil_bytes:
        for i in range(8):
            bits.append((byte >> i) & 1)
    return bits[:count]

def read_coils(start_addr, count):
    return read_bits(0x01, start_addr, count)

def read_discrete_inputs(start_addr, count):
    return read_bits(0x02, start_addr, count)

if __name__ == "__main__":
    coil_labels = ["StartButton", "StopButton", "LevelHighSensor", "LevelLowSensor"]
    di_labels = ["InletValve", "Heater", "DrainValve"]

    print("Initial state:")
    print("  Coils:", dict(zip(coil_labels, map(bool, read_coils(0, 4)))))
    print("  Discrete Inputs:", dict(zip(di_labels, map(bool, read_discrete_inputs(0, 3)))))

    print("\nWriting StartButton = TRUE via Modbus (function code 0x05)...")
    write_coil(0, True)
    time.sleep(0.3)
    print("Resetting StartButton back to FALSE (it's momentary in the PLC logic)...")
    write_coil(0, False)
    time.sleep(0.3)

    print("\nState after start:")
    print("  Coils:", dict(zip(coil_labels, map(bool, read_coils(0, 4)))))
    print("  Discrete Inputs:", dict(zip(di_labels, map(bool, read_discrete_inputs(0, 3)))))
