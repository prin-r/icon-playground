from iconservice import *

TAG = 'momo'


class momo(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self.test_value = VarDB("test_value", db, value_type=str)
        self.bridge = VarDB("bridge", db, value_type=Address)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def hello(self) -> str:
        Logger.debug(f'Hello, world!', TAG)
        return "Hello mom -> " + self.test_value

    @external
    def add_name(self, new_val: str) -> None:
        self.test_value.set(new_val)
