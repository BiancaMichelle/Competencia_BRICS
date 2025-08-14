import hashlib
import time
import json
import os
from datetime import datetime

class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data_str = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha3_512(data_str.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_chain()

    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0")

    def add_block(self, data):
        # Formatear la fecha antes de guardar
        data["fecha"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        prev_block = self.chain[-1]
        new_block = Block(len(self.chain), data, prev_block.hash)
        self.chain.append(new_block)
        self.save_chain()

    def save_chain(self):
        with open("historial.json", "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=2, ensure_ascii=False)

    def load_chain(self):
        if os.path.exists("historial.json"):
            with open("historial.json", "r", encoding="utf-8") as f:
                bloques = json.load(f)
                self.chain = [
                    Block(b["index"], b["data"], b["previous_hash"]) for b in bloques
                ]
        else:
            self.chain = [self.create_genesis_block()]
            self.save_chain()
