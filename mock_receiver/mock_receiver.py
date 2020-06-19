from iconservice import *

TAG = 'MOCK_RECEIVER'


class BRIDGE(InterfaceScore):
    @interface
    def set_count(self, count: int) -> int:
        pass

    @interface
    def get_count(self):
        pass


class MOCK_RECEIVER(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self.bridge_address = VarDB("bridge_address", db, value_type=Address)
        self.local_count = VarDB("local_count", db, value_type=int)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def get_bridge_address(self) -> Address:
        return self.bridge_address.get()

    @external(readonly=True)
    def get_local_count(self) -> int:
        return self.local_count.get()

    @external(readonly=True)
    def get_count_from_bridge(self) -> int:
        bridge = self.create_interface_score(self.bridge_address.get(), BRIDGE)
        return bridge.get_count()

    @external
    def set_bridge(self, bridge_address: Address) -> None:
        self.bridge_address.set(bridge_address)

    @external
    def set_local_count(self, count: int) -> None:
        bridge = self.create_interface_score(self.bridge_address.get(), BRIDGE)
        count = bridge.set_count(count)
        self.local_count.set(count)
