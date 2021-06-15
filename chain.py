import hashlib
from tinydb import TinyDB, Query, where
from hashlib import sha256
import json
from time import time
import datetime
from urllib.parse import urlparse

import block as blo
import IOTtransaction as tr

chain_db=TinyDB('chain_db.json')
mempool_db = TinyDB('mempool_db.json')

class chain:
    def __init__(self):
        self.current_transactions=[]
        self.chain = []
        self.nodes = set()

    # Adds transaction to the mempool
    # json transaction as parameter
    # returns transaction hash
    def add_transaction_to_mempool(self,json_transaction):
        json_tran=json.loads(json_transaction)
        now_time= datetime.datetime.now()
        now_timestamp= int(now_time.timestamp())
        total_transaction=str(now_timestamp)
        for u_tran in json_tran:
            unit_tran=tr.unit_iot_transaction(u_tran["sender"],u_tran["sign"])
            total_transaction+=u_tran["sender"]+u_tran["sign"]
            for u_rec in u_tran["receivers"]:
                unit_receiver=tr.reveiver(u_rec["receiver"],u_rec["message"],u_rec["key_share"])
                total_transaction+=u_rec["receiver"]+u_rec["message"]+u_rec["key_share"]
                unit_tran.receivers.append(unit_receiver)
            print(unit_tran.sender_address)
        print(total_transaction)
        hash=sha256(total_transaction.encode('utf-8')).hexdigest()

        trans=tr.IOTtransaction(hash,now_timestamp)
        self.current_transactions.append(trans)
        mempool_db.insert({"hash":hash,"timestamp":now_timestamp,"unit_transactions":json_transaction})
        print("transaction added to mempool:",hash)
        return hash

    # displays the mempool
    def display_mem_pool(self):
        print("total no of transaction in",len(mempool_db))
        for tran in mempool_db:
            print(tran["hash"],tran["timestamp"])

    #display the chain
    def display_chain(self):
        for blck in chain_db:
            print(" height:", blck['height'],end=" ")
            print("hash:",blck['hash'],end=" ")
            print(" timestamp:",blck['timestamp'],end=" ")
            print(" n_trans:",len(blck["transactions"]))

    #display chain in details
    def display_chain_details(self):
        for blck in chain_db:
            print("##################### BLOCK "+str(blck['height'])+" #####################")
            print("height:", blck['height'],end=" \n")
            print("hash:",blck['hash'],end=" \n")
            print(" timestamp:",blck['timestamp'],end=" \n")
            print(" no of transactions:",len(blck["transactions"]))
            print("##>>> Transactions")
            for tran in blck["transactions"]:
                print("\t Hash:",tran["hash"])
                print("\t Timestamp:",tran["timestamp"])
                for u_tran in tran["transactions"]:
                    print("\t\t Sender:",u_tran["sender"])
                    print("\t\t Signature:",u_tran["signature"])
                    for u_msg in u_tran["receiver"]:
                        print("\t\t\t Receiver:", u_msg["receiver"])
                        print("\t\t\t Message:", u_msg["message"])
                        print("\t\t\t Key Share:", u_msg["key_share"])

    # checks for transactions for specific public key
    def check_for_my_transactions(self,pub_key):
        pub_key=str(pub_key)
        for blck in chain_db:

            for tran in blck["transactions"]:
                for u_tran in tran["transactions"]:
                    for u_msg in u_tran["receiver"]:
                        if(u_msg["receiver"]==pub_key):
                            print("\t\t Sender:", u_tran["sender"])
                            print("\t\t Signature:", u_tran["signature"])
                            print("\t\t\t Receiver:", u_msg["receiver"])
                            print("\t\t\t Message:", u_msg["message"])
                            print("\t\t\t Key Share:", u_msg["key_share"])

    # def display_transaction_for_pubkey(self,pubk):
    #     for blck in self.chain:
    #         for tran in blck.transactions:


    # Saves block to database
    def save_block_to_db(self,new_block):
        hash=new_block.hash
        version=new_block.version
        height = new_block.height
        timestamp = new_block.timestamp
        difficulty = new_block.difficulty
        previous_hash = new_block.previous_hash
        previous_64_hash = new_block.previous_64_hash
        merkle_root = new_block.merkle_root
        nonce =new_block.nonce
        transactions=[]
        for trans in new_block.transactions:
            transactions.append(trans.to_dict())
        json_transactions=json.dumps(transactions)
        print(hash)
        print(version)
        print(timestamp)
        print(difficulty)
        print(previous_hash)
        print(previous_64_hash)
        print(merkle_root)
        print(nonce)
        print(json_transactions)
        json_transactions=json.loads(json_transactions)
        chain_db.insert({"hash":hash,"version":version,"height":height,"timestamp":timestamp,"difficulty":difficulty,"previous_hash":previous_hash,"previous_64_hash":previous_64_hash,"merkle_root":merkle_root,"nonce":nonce,"transactions":json_transactions})

    # Mine a block
    def mine_a_block(self):
        new_block=blo.block()
        res=new_block.mine_block()
        if(res==1):
            self.chain.append(new_block)
            self.save_block_to_db(new_block)
            #remove transactions from mempool
            # for x_trans in new_block.transactions:
            #     mempool_db.remove(where('hash') == x_trans.hash)

    #remove 1 block
    #to be used to remove unnecessary blocks
    def rem_1_block(self):
        chain_db.remove(where('height') == 1)
    # def create_transaction(self):
