import json

class IOTtransaction:
    def __init__(self,hash,timestamp):
        self.hash=hash
        self.timestamp=timestamp
        self.transactions=[]

    # def __init__(self):
    #     self.hash=""
    #     self.timestamp=0
    #     self.transactions=[]
    #1.
    #set hash
    def set_hash(self,hash):
        self.hash=hash

    #set timestamp
    def set_timestamp(self,timestamp):
        self.timestamp=timestamp

    #add unit transaction
    def add_unit_transaction(self,transaction):
        self.transactions.append(transaction)

    def to_dict(self):
        data={}
        data["hash"]=self.hash
        data["timestamp"]=self.timestamp
        unit_tran_data=[]
        for unit_tran in self.transactions:
            unit_tran_data.append(unit_tran.to_dict())
        data["transactions"]=unit_tran_data
        return data

    #to JSON
    def to_json(self):
        data={}
        data["hash"]=self.hash
        data["timestamp"]=self.timestamp
        unit_tran_data=[]
        for unit_tran in self.transactions:
            unit_tran_data.append(unit_tran.to_dict())
        data["transactions"]=unit_tran_data
        return json.dumps(data)

    #add or load JSON transaction
    def add_json_transactions(self,json_transactions):
        json_tran = json.loads(json_transactions)
        for u_tran in json_tran:
            unit_tran=unit_iot_transaction(u_tran["sender"],u_tran["sign"])
            for u_rec in u_tran["receivers"]:
                unit_receiver=reveiver(u_rec["receiver"],u_rec["message"],u_rec["key_share"])
                unit_tran.receivers.append(unit_receiver)
            self.add_unit_transaction(unit_tran)

#unit transaction class
class unit_iot_transaction:
    def __init__(self,address,signature):
        self.sender_address=address
        self.signature=signature
        self.receivers=[]
    #1.
    #set sender address
    def set_sender_address(self,address):
        self.sender_address=address

    #add receiver address
    def add_receiver(self,receiver):
        self.receivers.append(receiver)

    def to_dict(self):
        data = {}
        data["sender"] = self.sender_address
        data["signature"] = self.signature
        receiver_data=[]
        for rec in self.receivers:
            receiver_data.append(rec.to_dict())
        data["receiver"] =receiver_data;
        return data

    #convert to JSON format
    def to_json(self):
        data = {}
        data["sender"] = self.sender_address
        data["signature"] = self.signature
        receiver_data = []
        for rec in self.receivers:
            receiver_data.append(rec.to_dict())
        data["receiver"] = receiver_data;
        return json.dumps(data)



#receiverclass
class reveiver:
    def __init__(self,address,message,key_share):
        self.address=address
        self.message=message
        self.key_share=key_share

    #1 seting data
    def set_address(self, address):
        self.address = address
    def set_message(self, message):
        self.message = message
    def set_key_share(self, key_share):
        self.key_share = key_share

    def to_dict(self):
        data = {}
        data["receiver"] = self.address
        data["message"] = self.message
        data["key_share"] = self.key_share
        return data

    #converting into JSON format
    def to_json(self):
        data = {}
        data["receiver"] = self.address
        data["message"] = self.message
        data["key_share"] = self.key_share
        return json.dumps(data)



