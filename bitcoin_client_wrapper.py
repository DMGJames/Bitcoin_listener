from bitcoin_client import BitcoinClient

class BitcoinClientExcpetion(RuntimeError):
    pass

class NextBlockHashNotReady(BitcoinClientExcpetion):
    pass

class BitcoinClientWrapper(object):
    def __init__(self, rpc_url):
        self.client = BitcoinClient(rpc_url=rpc_url)

    def get_block_hash(self, height):
        return self.client.getblockhash(height)

    def get_block(self, hash):
        data = self.client.getblock(hash)
        data["vtx"] = self.get_block_txes(hash)
        return self.__create_block__(data)

    def get_blocks(self, hashes):
        result = []
        for i in hashes:
            result.append(self.get_block(i))
        return result

    def get_blocks_since(self, hash, max_active_blocks):
        data = self.client.getblockssince(hash, max_active_blocks)
        active_hashes = [d["hash"] for d in data["active"]]
        orphaned_hashes = [d["hash"] for d in data["orphaned"]]
        active_blocks = self.get_blocks(active_hashes)
        orphaned_blocks = self.get_blocks(orphaned_hashes)
        return { "active": active_blocks, "orphaned": orphaned_blocks }

    def get_block_txes(self, hash):
        data = self.client.getblocktxes(hash)
        return self.__create_transactions__(data)

    def get_raw_transaction(self, hash):
        data = self.client.getrawtransaction(hash, 1)
        return self.__create_transaction__(data)

    def get_raw_txout(self, tx_hash, offset):
        tx = self.get_raw_transaction(tx_hash)
        return tx.vout[offset]

    """
    Input JSON example:

    {
        "hash" : "000000000fe549a89848c76070d4132872cfb6efe5315d01d7ef77e4900f2d39",
        "confirmations" : 88029,
        "size" : 189,
        "height" : 227252,
        "version" : 2,
        "merkleroot" : "c738fb8e22750b6d3511ed0049a96558b0bc57046f3f77771ec825b22d6a6f4a",
        "tx" : [
            "c738fb8e22750b6d3511ed0049a96558b0bc57046f3f77771ec825b22d6a6f4a"
        ],
        "time" : 1398824312,
        "nonce" : 1883462912,
        "bits" : "1d00ffff",
        "difficulty" : 1.00000000,
        "chainwork" : "000000000000000000000000000000000000000000000000083ada4a4009841a",
        "previousblockhash" : "00000000c7f4990e6ebf71ad7e21a47131dfeb22c759505b3998d7a814c011df",
        "nextblockhash" : "00000000afe1928529ac766f1237657819a11cfcc8ca6d67f119e868ed5b6188"
    }
    """
    def __create_block__(self, data):
        return Block(
            version=data["version"],
            hash_prev_block=data.get("previousblockhash"),
            hash_merkle_root=data["merkleroot"],
            time=data["time"],
            bits=data["bits"],
            nonce=data["nonce"],
            hash=data["hash"],
            height=data["height"],
            confirmations=data["confirmations"],
            vtx=data["vtx"],
            difficulty=data["difficulty"])

    """
    Input JSON example:

    [
        <block_1>,
        <block_2>,
        ...
    ]
    """
    def __create_blocks__(self, data):
        result = []
        for i in data:
            result.append(self.__create_block__(i))
        return result

    """
    Input JSON example:


    [
        <transaction_1>,
        <transaction_2>,
        ...
    ]
    """
    def __create_transactions__(self, data):
        result = []
        for i in data:
            result.append(self.__create_transaction__(i))
        return result

    """
    Input JSON example:

    {
        "hex" : "0100000001268a9ad7bfb21d3c086f0ff28f73a064964aa069ebb69a9e437da85c7e55c7d7000000006b483045022100ee69171016b7dd218491faf6e13f53d40d64f4b40123a2de52560feb95de63b902206f23a0919471eaa1e45a0982ed288d374397d30dff541b2dd45a4c3d0041acc0012103a7c1fd1fdec50e1cf3f0cc8cb4378cd8e9a2cee8ca9b3118f3db16cbbcf8f326ffffffff0350ac6002000000001976a91456847befbd2360df0e35b4e3b77bae48585ae06888ac80969800000000001976a9142b14950b8d31620c6cc923c5408a701b1ec0a02088ac002d3101000000001976a9140dfc8bafc8419853b34d5e072ad37d1a5159f58488ac00000000",
        "txid" : "ef7c0cbf6ba5af68d2ea239bba709b26ff7b0b669839a63bb01c2cb8e8de481e",
        "version" : 1,
        "locktime" : 0,
        "vin" : <vin>,
        "vout" : <vout>,
        "blockhash" : "00000000103e0091b7d27e5dc744a305108f0c752be249893c749e19c1c82317",
        "confirmations" : 88192,
        "time" : 1398734825,
        "blocktime" : 1398734825
    }
    """
    def __create_transaction__(self, data):
        return Transaction(
            hash=data["txid"],
            version=data["version"],
            vin=self.__create_vin__(data["vin"]),
            vout=self.__create_vout__(data["vout"]),
            lock_time=data["locktime"])

    """
    Input JSON example:

    [
        <txin_1>,
        <txin_2>,
        ...
    ]
    """
    def __create_vin__(self, data):
        result = []
        for i in data:
            txin = self.__create_txin__(i)
            result.append(txin)
        return result

    """
    Input JSON example:

    For a coinbase:
    {
        "coinbase": "04ffff001d0104",
        "sequence" : 4294967295
    }

    For a non-coinbase input:
    {
        "txid" : "d7c7557e5ca87d439e9ab6eb69a04a9664a0738ff20f6f083c1db2bfd79a8a26",
        "vout" : 0,
        "scriptSig" : <script_sig>,
        "sequence" : 4294967295
    }
    """
    def __create_txin__(self, data):
        if "coinbase" in data:
            prevout = OutPoint()
            script_sig = self.__create_script_sig__({
                "asm": None,
                "hex": data["coinbase"]})
        else:
            prevout = OutPoint(
                hash=data["txid"],
                n=data["vout"])
            script_sig = self.__create_script_sig__(data["scriptSig"])

        return TxIn(
            prevout=prevout,
            script_sig=script_sig,
            sequence=data["sequence"])

    """
    Input JSON example:

    [
        <txout_1>,
        <txout_2>,
        ...
    ]
    """
    def __create_vout__(self, data):
        result = []
        for i in data:
            txout = self.__create_txout__(i)
            result.append(txout)
        return result

    """
    Input JSON example:

    {
        "value" : 0.39890000,
        "n" : 0,
        "scriptPubKey" : <script_pubkey>
    }
    """
    def __create_txout__(self, data):
        script_pubkey = self.__create_script_pubkey__(data["scriptPubKey"])

        return TxOut(
            value=data["value"],
            script_pubkey=script_pubkey)

    """
    Input JSON example:

    {
        "asm" : "3045022100ee69171016b7dd218491faf6e13f53d40d64f4b40123a2de52560feb95de63b902206f23a0919471eaa1e45a0982ed288d374397d30dff541b2dd45a4c3d0041acc001 03a7c1fd1fdec50e1cf3f0cc8cb4378cd8e9a2cee8ca9b3118f3db16cbbcf8f326",
        "hex" : "483045022100ee69171016b7dd218491faf6e13f53d40d64f4b40123a2de52560feb95de63b902206f23a0919471eaa1e45a0982ed288d374397d30dff541b2dd45a4c3d0041acc0012103a7c1fd1fdec50e1cf3f0cc8cb4378cd8e9a2cee8ca9b3118f3db16cbbcf8f326"
    }
    """
    def __create_script_sig__(self, data):
        return ScriptSig(
            asm=data["asm"],
            hex=data["hex"])

    """
    Input JSON example:

    {
        "asm" : "OP_DUP OP_HASH160 56847befbd2360df0e35b4e3b77bae48585ae068 OP_EQUALVERIFY OP_CHECKSIG",
        "hex" : "76a91456847befbd2360df0e35b4e3b77bae48585ae06888ac",
        "reqSigs" : 1,
        "type" : "pubkeyhash",
        "addresses" : [
            "moQR7i8XM4rSGoNwEsw3h4YEuduuP6mxw7",
            ...
        ]
    }
    """
    def __create_script_pubkey__(self, data):
        return ScriptPubKey(
            asm=data["asm"],
            hex=data["hex"],
            req_sigs=data.get("reqSigs"),
            type=data["type"],
            addresses=data.get("addresses"))

from bitcoin_core import Block, Transaction, TxIn, TxOut, \
    OutPoint, ScriptPubKey, ScriptSig