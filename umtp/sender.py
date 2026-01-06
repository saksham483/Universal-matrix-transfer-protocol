import socket
import numpy as np
import time
from protocol import UMTPPacket

def send_matrix(host='127.0.0.1', port=9999):
    try:
        # 1. Generate Artificial Data (Simulating a Neural Layer output)
        # Let's create a 3D Tensor (Batch, Time, Features)
        print("[*] Generating Neural Matrix...")
        neural_weights = np.random.rand(4, 8, 8).astype(np.float32)
        
        # 2. Encapsulate in UMTP
        # We assign it ID #101 (could be a layer ID or object ID)
        packet = UMTPPacket(tensor_id=101, tensor=neural_weights)
        serialized_data = packet.serialize()
        
        print(f"[*] Serialized Size: {len(serialized_data)} bytes")

        # 3. Open Stream
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        
        # 4. Transmit Reality
        print("[*] Streaming Matrix...")
        s.sendall(serialized_data)
        
        print("[*] Transfer Complete.")
        s.close()
        
    except ConnectionRefusedError:
        print("[!] Error: Target Node is offline.")

if __name__ == "__main__":
    send_matrix()
