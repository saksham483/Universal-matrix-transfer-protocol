# umtp_protocol.py
import struct
import json
import numpy as np

class UMTPPacket:
    """
    Universal Matrix Transfer Protocol (UMTP) - Application Layer Serializer.
    Version 3: Implements Pre-serialization Sparsity Heuristics.
    """
    def __init__(self, tensor_id, tensor, sparsity_threshold=0.25):
        self.tensor_id = tensor_id
        self.tensor = tensor
        self.threshold = sparsity_threshold
        self.VERSION = 3
        self.MAGIC = b'UMTP'
        
        # Header Format: Magic(4s), Version(I), TensorID(Q), MetaLen(I), Flags(B), Padding(4x) = 25 Bytes
        self.HEADER_FORMAT = "!4s I Q I B 4x"

    def serialize(self):
        """
        Executes the 'Inspect, then Pack' heuristic.
        Returns the fully constructed binary packet.
        """
        if self.tensor is None:
            raise ValueError("No tensor data provided.")

        # 1. Inspect: Calculate Sparsity
        total_elements = self.tensor.size
        non_zeros = np.count_nonzero(self.tensor)
        sparsity = (total_elements - non_zeros) / total_elements

        # 2. Prepare Metadata
        meta_dict = {"shape": self.tensor.shape, "dtype": str(self.tensor.dtype)}
        meta_bytes = json.dumps(meta_dict).encode('utf-8')

        # 3. Mode Selection & Payload Construction
        if sparsity > self.threshold:
            # SPARSE MODE (COO Representation)
            flags = 0x01
            indices = np.nonzero(self.tensor)
            values = self.tensor[indices]
            
            # Pack indices as uint32 and values as native float
            idx_bytes = np.vstack(indices).astype(np.uint32).tobytes()
            val_bytes = values.astype(self.tensor.dtype).tobytes()
            payload = idx_bytes + val_bytes
        else:
            # DENSE MODE (Raw Memory Buffer)
            flags = 0x00
            payload = self.tensor.tobytes()

        # 4. Construct Header
        header = struct.pack(
            self.HEADER_FORMAT, 
            self.MAGIC, 
            self.VERSION, 
            self.tensor_id, 
            len(meta_bytes), 
            flags
        )

        # 5. Return Final Packet
        return header + meta_bytes + payload
