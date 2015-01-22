from enum import Enum
from constants import DEFAULT_LOCAL_BITCONID_RPC_URL, SATOSHI_PER_BTC
import bitcoin_client_wrapper

bitcoin_client = bitcoin_client_wrapper.BitcoinClientWrapper(rpc_url=DEFAULT_LOCAL_BITCONID_RPC_URL)

class TxnoutType(Enum):
    TX_NONSTANDARD = 0
    TX_PUBKEY = 1
    TX_PUBKEYHASH = 2
    TX_SCRIPTHASH = 3
    TX_MULTISIG = 4
    TX_NULL_DATA = 5

class ScriptSig(object):
    def __init__(self, **kwargs):
        self.asm = kwargs.get("asm")
        self.hex = kwargs.get("hex")

class ScriptPubKey(object):
    def __init__(self, **kwargs):
        types = {
            None: TxnoutType.TX_NONSTANDARD,
            "nonstandard": TxnoutType.TX_NONSTANDARD,
            "pubkey": TxnoutType.TX_PUBKEY,
            "pubkeyhash": TxnoutType.TX_PUBKEYHASH,
            "scripthash": TxnoutType.TX_SCRIPTHASH,
            "multisig": TxnoutType.TX_MULTISIG,
            "nulldata": TxnoutType.TX_NULL_DATA
        }

        self.asm = kwargs.get("asm")
        self.hex = kwargs.get("hex")
        self.req_sigs = kwargs.get("req_sigs")
        self.type = types[kwargs.get("type")]
        self.addresses = kwargs.get("addresses")

class OutPoint(object):
    def __init__(self, **kwargs):
        if "hash" not in kwargs or "n" not in kwargs:
            self.set_null()
        else:
            self.hash = kwargs["hash"]
            self.n = kwargs["n"]

    def is_null(self):
        return self.hash == "\0" * 32 and self.n == -1

    def set_null(self):
        self.hash = "\0" * 32
        self.n = -1

class TxIn(object):
    def __init__(self, *args, **kwargs):
        self.prevout = kwargs.get("prevout")
        self.script_sig = kwargs.get("script_sig")
        self.sequence = kwargs.get("sequence")

class TxOut(object):
    def __init__(self, **kwargs):
        self.value = kwargs.get("value") * SATOSHI_PER_BTC
        self.script_pubkey = kwargs.get("script_pubkey")

class Transaction(object):
    def __init__(self, **kwargs):
        self.hash = kwargs.get("hash")
        self.version = kwargs.get("version")
        self.vin = kwargs.get("vin")
        self.vout = kwargs.get("vout")
        self.lock_time = kwargs.get("lock_time")

    def is_coinbase(self):
        return len(self.vin) == 1 and \
               self.vin[0].prevout.is_null()

    def get_value_in(self):
        global bitcoin_client

        if self.is_coinbase():
            return 0

        result = 0
        for txin in self.vin:
            txout = bitcoin_client.get_raw_txout(
                txin.prevout.hash,
                txin.prevout.n)
            assert txout is not None
            result += txout.value
        return result

    def get_value_out(self):
        result = 0
        for txout in self.vout:
            result += txout.value
        return result

    def get_fee(self):
        if self.is_coinbase():
            return 0
        else:
            return self.get_value_out() - self.get_value_in()


class BlockHeader(object):
    def __init__(self, **kwargs):
        self.version = kwargs.get("version")
        self.hash_prev_block = kwargs.get("hash_prev_block")
        self.hash_merkle_root = kwargs.get("hash_merkle_root")
        self.time = kwargs.get("time")
        self.bits = kwargs.get("bits")
        self.nonce = kwargs.get("nonce")

class Block(BlockHeader):
    def __init__(self, **kwargs):
        super(Block, self).__init__(**kwargs)
        self.hash = kwargs.get("hash")
        self.height = kwargs.get("height")
        self.confirmations = kwargs.get("confirmations")
        self.vtx = kwargs.get("vtx")
        self.difficulty = kwargs.get("difficulty")
        self.hash_next_block = kwargs.get("hash_next_block")
