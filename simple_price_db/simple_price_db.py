from iconservice import *
from .pyobi import *

TAG = 'SIMPLE_PRICE_DB'


class BRIDGE(InterfaceScore):
    @interface
    def get_latest_response(self, encoded_request: bytes) -> dict:
        pass


class SIMPLE_PRICE_DB(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self.bridge_address = VarDB("bridge_address", db, value_type=Address)
        self.latest_icx_price = VarDB("latest_icx_price", db, value_type=int)
        self.latest_request_timestamp = VarDB(
            "latest_request_timestamp", db, value_type=int)
        self.latest_resolve_timestamp = VarDB(
            "latest_resolve_timestamp", db, value_type=int)
        self.multiplier = VarDB("multiplier", db, value_type=int)
        self.encoded_request = VarDB("encoded_request", db, value_type=bytes)

    def on_install(self, encoded_request: bytes, bridge_address: Address) -> None:
        super().on_install()
        req = PyObi(
            """
            {
                client_id: string,
                oracle_script_id: u64,
                calldata: bytes,
                ask_count: u64,
                min_count: u64
            }
            """
        ).decode(encoded_request)

        calldata_dict = PyObi(
            """
            {
                base_symbol: string,
                quote_symbol: string,
                multiplier: u64
            }
            """
        ).decode(req["calldata"])

        self.multiplier.set(calldata_dict["multiplier"])
        self.encoded_request.set(encoded_request)
        self.bridge_address.set(bridge_address)

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def get_bridge_address(self) -> Address:
        return self.bridge_address.get()

    @external(readonly=True)
    def get_encoded_request_template(self) -> bytes:
        return self.encoded_request.get()

    @external(readonly=True)
    def value(self) -> int:
        res = self.get_latest_response_from_bridge(self.encoded_request.get())
        return PyObi("""u64""").decode(res["result"])

    @external(readonly=True)
    def get_multiplier(self) -> int:
        return self.multiplier.get()

    @external(readonly=True)
    def get_latest_request_timestamp(self) -> int:
        res = self.get_latest_response_from_bridge(self.encoded_request.get())
        return res["request_time"]

    @external(readonly=True)
    def get_latest_resolve_timestamp(self) -> int:
        res = self.get_latest_response_from_bridge(self.encoded_request.get())
        return res["resolve_time"]

    @external(readonly=True)
    def get_latest_response_from_bridge(self, encoded_request: bytes) -> dict:
        bridge = self.create_interface_score(self.bridge_address.get(), BRIDGE)
        return bridge.get_latest_response(encoded_request)

    @external
    def set_bridge(self, bridge_address: Address) -> None:
        if self.msg.sender != self.owner:
            self.revert("NOT_AUTHORIZED")

        self.bridge_address.set(bridge_address)

    @external
    def set_encoded_request(self, encoded_request: bytes) -> None:
        if self.msg.sender != self.owner:
            self.revert("NOT_AUTHORIZED")

        self.encoded_request.set(encoded_request)
