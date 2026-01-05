import struct
import json
import numpy as np
import io

# UMTP CONSTANTS
UMTP_MAGIC = b'UMTP' # The handshake signature
VERSION = 1
HEADER_FORMAT = "!4s I Q I"  # Magic(4s), Version(Int), ID(Long), MetaLength(Int)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

class UMTPPacket:
    def __init__(self, tensor_id=0, tensor=None):
        self.tensor_id = tensor_id
        self.tensor = tensor
        self.metadata = {}
    
    def serialize(self):
        """
        Converts a NumPy tensor into a UMTP binary stream.
        Structure: [HEADER] + [METADATA_JSON] + [RAW_BYTES]
        """
        if self.tensor is None:
            raise ValueError("No tensor data to serialize.")

        # 1. Extract Topology (Shape and Type)
        tensor_bytes = self.tensor.tobytes()
        self.metadata = {
            "shape": self.tensor.shape,
            "dtype": str(self.tensor.dtype),
            "byte_order": "little", # Standardize on little-endian
            "payload_size": len(tensor_bytes)
        }
        
        # 2. Serialize Metadata
        meta_bytes = json.dumps(self.metadata).encode('utf-8')
        meta_length = len(meta_bytes)

        # 3. Pack Header (Big Endian standard for network)
        # Magic | Version | Tensor ID | Metadata Length
        header = struct.pack(HEADER_FORMAT, UMTP_MAGIC, VERSION, self.tensor_id, meta_length)

        # 4. Return the full packet
        return header + meta_bytes + tensor_bytes

    @staticmethod
    def read_from_socket(sock):
        """
        Reads a UMTP packet from a TCP socket stream and reconstructs the Tensor.
        This handles the logic of 'rebuilding' the matrix on the other side.
        """
        # Helper to ensure we read exactly N bytes
        def recvall(n):
            data = b''
            while len(data) < n:
                packet = sock.recv(n - len(data))
                if not packet: return None
                data += packet
            return data

        # 1. Read Fixed Header
        raw_header = recvall(HEADER_SIZE)
        if not raw_header: return None
        
        magic, ver, t_id, meta_len = struct.unpack(HEADER_FORMAT, raw_header)
        
        if magic != UMTP_MAGIC:
            raise ValueError("Invalid Protocol: Not a UMTP packet")

        # 2. Read Metadata
        raw_meta = recvall(meta_len)
        metadata = json.loads(raw_meta.decode('utf-8'))

        # 3. Read Payload (The Heavy Matrix)
        payload_size = metadata["payload_size"]
        raw_payload = recvall(payload_size)

        # 4. Reconstruct Reality (Bytes -> Tensor)
        dtype = np.dtype(metadata["dtype"])
        shape = tuple(metadata["shape"])
        
        reconstructed_tensor = np.frombuffer(raw_payload, dtype=dtype).reshape(shape)
        
        return t_id, reconstructed_tensor
