import hashlib
import json
import time
import os

class Block:
    def __init__(self, index, timestamp, data, previous_hash, firma):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.firma = firma
        self.hash = self.calcular_hash()

    def calcular_hash(self):
        bloque_str = f"{self.index}{self.timestamp}{json.dumps(self.data)}{self.previous_hash}{self.firma}"
        return hashlib.sha256(bloque_str.encode()).hexdigest()

    def to_dict(self):
        return self.__dict__

class Blockchain:
    def __init__(self, archivo='cadena.json'):
        self.archivo = archivo
        self.cadena = []
        self.cargar()

    def crear_bloque_genesis(self):
        genesis = Block(0, time.time(), {"mensaje": "Bloque génesis"}, "0", "sistema")
        self.cadena.append(genesis)
        self.guardar()

    def agregar_bloque(self, data, firma):
        anterior = self.cadena[-1]
        nuevo = Block(len(self.cadena), time.time(), data, anterior.hash, firma)
        self.cadena.append(nuevo)
        self.guardar()

    def guardar(self):
        with open(self.archivo, 'w') as f:
            json.dump([bloque.to_dict() for bloque in self.cadena], f, indent=4)

    def cargar(self):
        if os.path.exists(self.archivo):
            with open(self.archivo, 'r') as f:
                datos = json.load(f)
                self.cadena = [
                    Block(b["index"], b["timestamp"], b["data"], b["previous_hash"], b["firma"])
                    for b in datos
                ]
        else:
            self.crear_bloque_genesis()

    def es_valida(self):
        for i in range(1, len(self.cadena)):
            actual = self.cadena[i]
            anterior = self.cadena[i - 1]
            if actual.previous_hash != anterior.hash or actual.hash != actual.calcular_hash():
                return False
        return True
