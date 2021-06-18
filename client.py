from tinydb import TinyDB, Query
import crypto as crp
from hashlib import sha256
import binascii
from binascii import unhexlify
import IOTtransaction as iotr

import chain
wallet_db = TinyDB('wallet_db.json')
class client:
    #validate receiver
    def validate_receiver(self,receiver):
        if(receiver.isnumeric()):
            receiver=int(receiver)
            xx=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
            if(receiver<xx and receiver>0):
                return True
        return False

    def make_transaction(self):
        print("enter receiver: ")
        receiver=input()
        if(self.validate_receiver(receiver)):
            msg=input("enter message: ")
            l=len(wallet_db)
            if(l==0):
                self.create_new_address()
                l=1
            i=1
            pubkey_map=[]
            prvkey_map=[]
            for address in wallet_db:
                print(i,": ",address["pbk"])
                pubkey_map.append(address["pbk"])
                prvkey_map.append(address["prv"])
                i+=1
            n_sender=input("from which one do you want to send: ")
            if(n_sender.isnumeric()):
                n_sender=int(n_sender)
                if(n_sender<=l):
                    print("receiver:",receiver)
                    print("message:",msg)
                    print("sender:",pubkey_map[n_sender-1])
                    total_transaction=receiver+msg+str(pubkey_map[n_sender-1])
                    hash = sha256(total_transaction.encode('utf-8')).hexdigest()
                    print(hash)
                    cr=crp.crypto()
                    (rx,sign)=cr.sign_message(int("0x"+hash,16),prvkey_map[n_sender-1])

                    json_data='[{"sender":"'+str(pubkey_map[n_sender-1])+'","sign":"'+str(rx)+','+str(sign)+'","receivers":[{"receiver":"'+str(receiver)+'","message":"'+msg+'","key_share":"'+str(pubkey_map[n_sender-1])+'"}]}]'

                    lc = chain.chain()
                    lc.add_transaction_to_mempool(json_data)
                    lc.display_mem_pool()
                    #more to be done




    #create new address
    def create_new_address(self):
        cr=crp.crypto()
        pv_k=cr.generate_private_key()
        pub_k=cr.private_to_public(pv_k)
        wallet_db.insert({"prv":pv_k,"pbk":pub_k})

    #view all address in the wallet
    def view_addresses(self):
        for address in wallet_db:
            print(address)
