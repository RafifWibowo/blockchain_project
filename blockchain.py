import datetime
import hashlib
import json
from flask import Flask, jsonify, request

class Blockchain:
    def __init__(self):
        self.chain = []

        #genesis block
        self.create_block(proof= 1, data= None, prev_hash= '0', proof_of_work= None)
    
    def create_block(self, proof, data, prev_hash, proof_of_work):
        block = {
            'id_block': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'data': data,
            'proof': proof,
            'prev_hash': prev_hash,
            'proof_of_work': proof_of_work
        }
        newKey = 'hash'
        hashed_block = self.get_hash(block)
        block = {**block, newKey: hashed_block}
        self.chain.append(block)
        return block
    
    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof, hash_operation
    
    def get_hash(self, block):
        hash_operation = hashlib.sha256(json.dumps(block).encode()).hexdigest()
        return hash_operation

    def is_chain_valid(self):
        prev_block = self.chain[0]
        now_index = 1
        while now_index < len(self.chain):
            now_block = self.chain[now_index]

            # cek hash now block == prev hash
            prev_hash = prev_block['hash']
            if prev_hash != now_block['prev_hash']:
                return False
            
            # cek proof of work true
            now_proof = now_block['proof']
            prev_proof = prev_block['proof']
            hash_operation = hashlib.sha256(str(now_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            
            prev_block = now_block
            now_index += 1

        return True

app = Flask(__name__)

balok = Blockchain()

@app.route("/get_chain", methods=['GET'])
def get_chain():
    response = {
        'chain': balok.chain,
        'length': len(balok.chain)
    }
    return jsonify(response), 200

@app.route("/mining", methods=['GET'])
def mining():
    prev_block = balok.get_last_block()

    #get prev proof
    prev_proof = prev_block['proof']
    proof, proof_of_work = balok.proof_of_work(prev_proof)

    #get prev hash
    prev_hash = balok.get_hash(prev_block)

    #create block
    created_balok = balok.create_block(proof, prev_hash, proof_of_work)
    response = {
        'message': "Blockhain is created",
        'created_block': created_balok
    }
    return jsonify(response), 200

@app.route("/create_block", methods=['POST'])
def create_block():
    name = request.form
    prev_block = balok.get_last_block()

    #get prev proof
    prev_proof = prev_block['proof']
    proof, proof_of_work = balok.proof_of_work(prev_proof)

    #get prev hash
    prev_hash = prev_block['hash']

    #create block
    created_balok = balok.create_block(proof, name, prev_hash, proof_of_work)
    response = {
        'message': "Blockhain is created",
        'created_block': created_balok
    }
    return jsonify(response), 200

@app.route("/modify_block", methods=['POST'])
def modify_block():
    content_type = request.headers.get('Content-Type')
    data = request.get_json()

    id_block = data['id_block']
    name = data['name']

    block = balok.chain[id_block-1]
    block['data'] = name

    new_hash = balok.get_hash(block)
    block['hash'] = new_hash

    response = {
        'message': "Block Modified",
        'id_block': id_block
    }
    return jsonify(response), 200

@app.route("/check_chain", methods=['GET'])
def check_chain():
    check = balok.is_chain_valid()
    # message = ''
    # if check != True:
    #     message = "Chain tidak valid"
    # else:
    #     message = "Chain valid"
    
    response = {
        'message': check
    }
    return jsonify(response), 200

app.run()