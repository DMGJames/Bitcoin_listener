from sqlalchemy.sql.functions import func
from sqlalchemy import desc

from models import Block
from models import Transaction
from models import Input
from models import Output
from models import Address
from models import OutputsAddress

class MainchainMixin(object):
    def select_block(self, **kwargs):
        assert len(kwargs) == 1 and \
               ("id" in kwargs or
                "hash" in kwargs)
        if "id" in kwargs:
            return self.session.query(Block). \
                filter(Block.id == kwargs["id"]). \
                first()
        if "hash" in kwargs:
            return self.session.query(Block).\
                filter(Block.hsh == func.unhex(kwargs["hash"])). \
                first()

    def select_blocks(self, **kwargs):
        assert len(kwargs) == 1 and \
               "address" in kwargs
        if "address" in kwargs:
            p = self.session.query(Block). \
                select_from(Address). \
                join(Output, Address.id == Output.address_id). \
                join(Transaction, Output.tx_id == Transaction.id). \
                join(Block, Transaction.block_id == Block.id). \
                filter(Address.address == kwargs["address"])
            q = self.session.query(Block). \
                select_from(Address). \
                join(OutputsAddress, Address.id == OutputsAddress.address_id). \
                join(Output, OutputsAddress.output_id == Output.id). \
                join(Transaction, Output.tx_id == Transaction.id). \
                join(Block, Transaction.block_id == Block.id). \
                filter(Address.address == kwargs["address"])
            q = p.union_all(q).distinct().order_by(Block.id)
            return q.all()

    def select_transaction(self, **kwargs):
        assert len(kwargs) == 1 and \
               ("id" in kwargs or
                "hash" in kwargs)
        if "id" in kwargs:
            return self.session.query(Transaction). \
                filter(Transaction.id == kwargs["id"]). \
                first()
        if "hash" in kwargs:
            return self.session.query(Transaction).\
                filter(Transaction.hsh == func.unhex(kwargs["hash"])). \
                first()

    def select_transactions(self, **kwargs):
        assert len(kwargs) == 1 and \
               "block_id" in kwargs
        if "block_id" in kwargs:
            return self.session.query(Transaction). \
                filter(Transaction.block_id == kwargs["block_id"]). \
                order_by(Transaction.id). \
                all()

    def select_inputs(self, **kwargs):
        assert len(kwargs) == 1 and \
               "block_id" in kwargs
        if "block_id" in kwargs:
            return self.session.query(Input). \
                join(Transaction, Input.tx_id == Transaction.id). \
                filter(Transaction.block_id == kwargs["block_id"]). \
                order_by(Input.id). \
                all()

    def select_output(self, **kwargs):
        if __debug__:
            if len(kwargs) == 1:
                assert "id" in kwargs
            elif len(kwargs) == 2:
                assert "hash" in kwargs and "offset" in kwargs
            else:
                raise AssertionError

        if len(kwargs) == 1:
            if "id" in kwargs:
                return self.session.query(Output). \
                    filter(Output.id == kwargs["id"]). \
                    first()
        else:
            return self.session.query(Output). \
                join(Transaction, Output.tx_id == Transaction.id). \
                filter(Transaction.hsh == func.unhex(kwargs["hash"])). \
                filter(Output.offset == kwargs["offset"]). \
                first()

    def select_outputs(self, **kwargs):
        assert len(kwargs) == 1 and \
               "block_id" in kwargs
        if "block_id" in kwargs:
            return self.session.query(Output). \
                join(Transaction, Output.tx_id == Transaction.id). \
                filter(Transaction.block_id == kwargs["block_id"]). \
                order_by(Output.id). \
                all()

    def select_address(self, **kwargs):
        assert len(kwargs) == 1 and ( \
               "id" in kwargs or \
               "address" in kwargs)
        if "id" in kwargs:
            return self.session.query(Address). \
                filter(Address.id == kwargs["id"]). \
                first()
        if "address" in kwargs:
            return self.session.query(Address). \
                filter(Address.address == kwargs["address"]). \
                first()

    def select_outputs_addresses(self, **kwargs):
        assert len(kwargs) == 1 and \
               "output_id" in kwargs
        if "output_id" in kwargs:
            return self.session.query(OutputsAddress). \
                filter(OutputsAddress.output_id == kwargs["output_id"]). \
                all()

    def select_tip(self):
        return self.session.query(Block). \
            order_by(desc(Block.id)). \
            first()

    def select_max_id(self, table):
        if table == "blocks":
            return self.session.query(func.max(Block.id)).first()[0]
        if table =="transactions":
            return self.session.query(func.max(Transaction.id)).first()[0]
        if table =="inputs":
            return self.session.query(func.max(Input.id)).first()[0]
        if table =="outputs":
            return self.session.query(func.max(Output.id)).first()[0]
        if table =="addresses":
            return self.session.query(func.max(Address.id)).first()[0]
        assert False

class MainchainSession(MainchainMixin):
    def __init__(self, session):
        self.session = session

    def __getattr__(self, name):
        return getattr(self.session, name)