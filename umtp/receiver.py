import socket
from protocol import UMTPPacket

def start_server(host='0.0.0.0', port=9999):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    print(f"[*] UMTP Node Active on {host}:{port}")
    print("[*] Waiting for Matrix Injection...")

    while True:
        client_sock, address = server_socket.accept()
        print(f"[+] Connection established with Neural Node: {address}")

        try:
            # The protocol handles the reconstruction logic
            tensor_id, matrix = UMTPPacket.read_from_socket(client_sock)
            
            print(f"\n[RCV] Received Tensor ID: {tensor_id}")
            print(f"[RCV] Topology: {matrix.shape} | Type: {matrix.dtype}")
            print(f"[RCV] Data Sample (First Row):\n{matrix[0]}")
            print("-" * 40)
            
            # Here you would feed 'matrix' into PyTorch/TensorFlow
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_sock.close()

if __name__ == "__main__":
    start_server()
