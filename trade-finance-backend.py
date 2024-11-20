# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
import json
import hashlib
from datetime import datetime
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
load_dotenv()

# Connect to local blockchain (replace with actual network details in production)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Load smart contract ABI and address
with open('LetterOfCredit.json', 'r') as f:
    contract_json = json.load(f)
    
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_json['abi'])

class TradeFinanceSystem:
    @staticmethod
    def hash_document(document_content):
        """Generate hash for document content"""
        return hashlib.sha256(document_content.encode()).hexdigest()
    
    @staticmethod
    def validate_address(address):
        """Validate Ethereum address"""
        return Web3.is_address(address)

@app.route('/api/lc/create', methods=['POST'])
def create_lc():
    try:
        data = request.json
        required_fields = ['seller', 'sellerBank', 'amount', 'expiryDays']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Validate addresses
        if not all(TradeFinanceSystem.validate_address(addr) for addr in [data['seller'], data['sellerBank']]):
            return jsonify({'error': 'Invalid Ethereum address'}), 400

        # Create LC transaction
        transaction = contract.functions.createLC(
            data['seller'],
            data['sellerBank'],
            int(data['amount']),
            int(data['expiryDays'])
        ).build_transaction({
            'from': w3.eth.accounts[0],
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(w3.eth.accounts[0])
        })

        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, os.getenv('PRIVATE_KEY'))
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            'message': 'LC created successfully',
            'transactionHash': receipt['transactionHash'].hex(),
            'lcId': receipt['logs'][0]['data']  # Extract LC ID from event logs
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lc/approve/<int:lc_id>', methods=['POST'])
def approve_lc(lc_id):
    try:
        # Verify sender is buyer's bank
        transaction = contract.functions.approveLCByBank(lc_id).build_transaction({
            'from': w3.eth.accounts[0],
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(w3.eth.accounts[0])
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, os.getenv('PRIVATE_KEY'))
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            'message': 'LC approved successfully',
            'transactionHash': receipt['transactionHash'].hex()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lc/submit-documents/<int:lc_id>', methods=['POST'])
def submit_documents(lc_id):
    try:
        if 'documents' not in request.files:
            return jsonify({'error': 'No documents provided'}), 400

        documents = request.files['documents']
        document_hash = TradeFinanceSystem.hash_document(documents.read().decode())

        transaction = contract.functions.submitDocuments(lc_id, document_hash).build_transaction({
            'from': w3.eth.accounts[0],
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(w3.eth.accounts[0])
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, os.getenv('PRIVATE_KEY'))
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            'message': 'Documents submitted successfully',
            'documentHash': document_hash,
            'transactionHash': receipt['transactionHash'].hex()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lc/details/<int:lc_id>', methods=['GET'])
def get_lc_details(lc_id):
    try:
        details = contract.functions.getLCDetails(lc_id).call()
        
        return jsonify({
            'buyer': details[0],
            'seller': details[1],
            'amount': details[2],
            'expiryDate': datetime.fromtimestamp(details[3]).isoformat(),
            'state': details[4],
            'isActive': details[5]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
