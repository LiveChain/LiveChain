from hashlib import *
import binascii
from binascii import unhexlify
import hashlib
from tinydb import TinyDB, Query
import random
import IOTtransaction as tr
import chain
import datetime

mempool_db = TinyDB('mempool_db.json')
chain_db = TinyDB('chain_db.json')

class block:
    def __init__(self):
        self.version=1
        self.hash=""
        self.height=0
        self.timestamp=0
        self.difficulty=1
        self.previous_hash="8dc11f4b29b5f5081e364892cd430f8aa1b931c15b3001bf3e13d25060096a5e"
        self.previous_64_hash="8dc11f4b29b5f5081e364892cd430f8aa1b931c15b3001bf3e13d25060096a5e"
        self.merkle_root=""
        self.nonce=0

        self.transactions=[]

    #1 calculating merkle root
    def hashIt(self,firstTxHash, secondTxHash):
        # Reverse inputs before and after hashing
        # due to big-endian
        unhex_reverse_first = binascii.unhexlify(firstTxHash)[::-1]
        unhex_reverse_second = binascii.unhexlify(secondTxHash)[::-1]

        concat_inputs = unhex_reverse_first + unhex_reverse_second
        first_hash_inputs = hashlib.sha256(concat_inputs).digest()
        final_hash_inputs = hashlib.sha256(first_hash_inputs).digest()
        # reverse final hash and hex result
        return binascii.hexlify(final_hash_inputs[::-1])

    def merkleCalculatorDFS(self,hashList):
        if len(hashList) == 1:
            return hashList[0]
        newHashList = []
        # Process pairs. For odd length, the last is skipped
        for i in range(0, len(hashList) - 1, 2):
            newHashList.append(self.hashIt(hashList[i], hashList[i + 1]))
        if len(hashList) % 2 == 1:  # odd, hash last item twice
            newHashList.append(self.hashIt(hashList[-1], hashList[-1]))
        return self.merkleCalculator(newHashList)

    def merkleCalculator(self,hashList):
        if len(hashList)==0:
            return sha256("mukul".encode('utf-8')).hexdigest()
        if len(hashList) == 1:
            return hashList[0]

        while(len(hashList)>1):
            newHashList = []
            # Process pairs. For odd length, the last is skipped
            for i in range(0, len(hashList) - 1, 2):
                newHashList.append(self.hashIt(hashList[i], hashList[i + 1]))
            if len(hashList) % 2 == 1:  # odd, hash last item twice
                newHashList.append(self.hashIt(hashList[-1], hashList[-1]))
            hashList=newHashList
        return hashList[0].decode('utf-8')
    #
    # generate merkle root
    def calculate_merkle_root(self):
        print("calculating markle root")
        hashstore=[]
        for tnx in self.transactions:
            currentItem = tnx.hash
            hashstore.append(currentItem)

        self.merkle_root=self.merkleCalculator(hashstore)

    #2 setting properties

    def set_height(self,h):
        self.height=h
    def set_version(self,h):
        self.version=h
    def set_hash(self,h):
        self.hash=h
    def set_timestamp(self,t):
        self.timestamp=t
    def set_difficulty(self,d):
        self.difficulty=d
    def set_previous_hash(self,h):
        self.previous_hash=h
    def set_previous_64_hash(self,h):
        self.previous_64_hash=h
    def set_nonce(self,n):
        self.nonce=n

    def add_transactions(self,transaction):
        self.transactions.append(transaction)

    #3 calculate last 64 hash
    def calculate_last_64_hash(self):
        ln=len(chain_db)
        end=ln-1
        strt=max(end-64,0)
        all_last_64_hash=[]
        blocks = Query()
        blocks_res=chain_db.search((blocks.height<=end) & (blocks.height>=strt))
        for blk in blocks_res:
            all_last_64_hash.append(blk["hash"]+str(self.timestamp))
        h=self.merkleCalculator(all_last_64_hash)
        self.set_previous_64_hash(h)

    # previous hash calculation
    def calculate_previous_hash(self):
        ln = len(chain_db)
        ln-=1
        blocks = Query()
        blocks_res = chain_db.search(blocks["height"]==ln)
        for blk in blocks_res:
            self.previous_hash=blk["previous_hash"]

    #4 calculate hash
    def littleEndian(self,string):
        splited = [str(string)[i:i + 2] for i in range(0, len(str(string)), 2)]
        splited.reverse()
        return "".join(splited)

    def calculate_block_hash(self):
        version = self.littleEndian('0'*(16-len(hex(self.version)[2:]))+hex(self.version)[2:])
        little_endian_previousHash = self.littleEndian(self.previous_hash)
        little_endian_previous64Hash = self.littleEndian(self.previous_64_hash)
        little_endian_merkleRoot = self.littleEndian(self.merkle_root)
        little_endian_time = self.littleEndian('0'*(16-len(hex(self.timestamp)[2:]))+hex(self.timestamp)[2:])
        little_endian_difficultyBits = self.littleEndian('0'*(16-len(hex(self.difficulty)[2:]))+hex(self.difficulty)[2:])
        little_endian_nonce = self.littleEndian('0'*(16-len(hex(self.nonce)[2:]))+hex(self.nonce)[2:])

        # print(little_endian_merkleRoot[1:-1])
        header = version + little_endian_previousHash + little_endian_previous64Hash[1:-1] + little_endian_merkleRoot[1:-1] + little_endian_time + little_endian_difficultyBits + little_endian_nonce
        # print(header)
        if len(header)%2==1:
            header='0'+header
        header = unhexlify(header)
        CalculatedHash = sha256(sha256(header).digest()).hexdigest()
        self.set_hash(CalculatedHash)

    #mine a block from available transaction in mempool
    def mine_block(self):
        self.construct_block()
        for i in range(100000):#1000 is a demo value
            self.nonce=i
            self.calculate_block_hash()
            if int('0x'+self.hash,16)<(2**240):
                print("block is mined successfully!")
                print(self.hash)
                return 1
        #if int('0x' + self.hash,16)>=(2 ** 254):
        print("block is mined failed!")
        return 0
        #add to block chain

    #get height
    def get_height(self):
        height=0
        for blck in chain_db:
            height=blck['height']
        height+=1
        return height

    #construct block
    def construct_block(self):
        n=10
        if len(mempool_db)<n:
            n=len(mempool_db)
        else:
            n=random.randrange(n//2,n)

        for tran in mempool_db:
            transaction=tr.IOTtransaction(tran["hash"],tran["timestamp"])
            transaction.add_json_transactions(tran["unit_transactions"])
            self.transactions.append(transaction)
            n-=1
            if n==0:
                break
        now_time = datetime.datetime.now()
        now_timestamp = int(now_time.timestamp())
        self.timestamp=now_timestamp
        height=self.get_height()#len(chain_db)
        self.height=height
        # print("height:",height)
        if(height>0):
            self.calculate_previous_hash()
            self.calculate_last_64_hash()
        self.calculate_merkle_root()
        self.calculate_block_hash()








