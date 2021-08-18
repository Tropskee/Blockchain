import hashlib
import json
from time import time
from uuid import uuid4
import requests
from flask import Flask, request, jsonify
from urllib.parse import urlparse

class Blockchain(object):
    '''
    Responsible for managing the chain. It will
    store transactions, and will have methods for adding
    new blocks to the chain
    '''
    def __init__(self):
        self.chain = []
        self.nodes = set() # Using set() to ensure no dupes
        self.current_transactions = []

        # Create genesis block
        self.new_block(previous_hash = '1', proof = 100)

    def register_node(self, address):
        """
        Add new node to list of current nodes

        :param address: Address of current node - ex. 'http://187.158.0.7:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accept an URL without address like '187.158.0.7:5000'
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')
    
    def valid_chain(self, chain):
        """
        Determine if the given blockchain is valid

        :param chain: A blockchain
        :return: True if valid chain, False if not
        """

        current_index = 1
        last_block = chain[0]

        # Loop through all blocks in chain
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Verify hash of last block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False
            
            # Check that proof is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            # If block is true, update block and iterator
            last_block = block
            current_index += 1

        return True
        
    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain
        
        :param proof: Proof given by Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """
        
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        
        :param sender: Address of the Sender
        :param recipient: Address of the recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    # Python decorator to make defining last_block easy
    @property
    def last_block(self):
        return self.chain[-1]

    # Python decorator to easily return hash
    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a block
        
        :param block: Block
        :return: hexadecimal hash of Block
        """

        # Ensure that the Dict is ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Proof of Work Algorithm
        
        Basics:
        - Find a numper p' such that hash(pp') contains 4 leading zeroes
        - Where p is the previous proof, and p' is the new proof
        
        :param last_block: <dict> last Block
        :return: <int> 
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1
        
        return proof
    

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof
        
        :param last_proof: <int> Previous Proof
        :param proof: <int> current Proof
        :param last_hash: <str> The hash of the previous Block
        :return: <bool> True if correct, False if not
        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest
        return guess_hash[:4] == "0000"

    # NEED FINISH
    def resolve_conflicts(self):
        """
        Contains the consensus algorithm. Resolves any conflicts
        by replacing the current chain with the longest one in the 
        network.
        
        :return: True if our chain was replaced, False if not
        """

        neighbors = self.nodes
        new_chain = None

        # Checking chains longer than ours
        max_length = len(self.chain)

        # Verify chains from all nodes currently in our network
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Now check if length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        
        return False

    
# Instantiate the node
app = Flask(__name__)

# Create a globally unique address for this node
node_identifier = str(uuid4()).replace('-','')

# Instantiate the Blockchain
blockchain = Blockchain()



