from iconservice import *

TAG = 'MUMU'


class MUMU(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self.names = DictDB("names", db, value_type=str)
        self.size = VarDB("size", db, value_type=int)

    def on_install(self) -> None:
        super().on_install()
        self.size.set(10)

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def get_size(self) -> int:
        return self.size.get()

    @external(readonly=True)
    def get_name(self, i: int) -> str:
        return self.names[i]

    @external(readonly=True)
    def test_recover_key(self, msg_hash: bytes, signature: bytes, compressed: bool = True) -> bytes:
        pub = recover_key(msg_hash, signature, compressed)
        if pub == None:
            return b''
        return pub

    @external(readonly=True)
    def test_sha3(self, data: bytes) -> bytes:
        return sha3_256(data)

    @external
    def add_name(self, name: str) -> None:
        self.names[self.size.get()] = name
        self.size.set(self.size.get() + 1)
