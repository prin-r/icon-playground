from iconservice import *

TAG = 'SIMPLE_PRICE_DB'

# ---------- obi -----------


def decode_int(b: bytes, n_bits: int) -> (int, bytes):
    acc = 0
    i = 0
    r = n_bits >> 3
    while i < r:
        acc <<= 8
        acc += int(b[i])
        i += 1
    return (acc, b[r:])


def decode_bool(b: bytes) -> (int, bytes):
    return (int(b[0]) != 0, b[1:])


def decode_bytes_fix_size(b: bytes, size: int) -> (bytes, bytes):
    return (b[:size], b[size:])


def decode_bytes(b: bytes) -> (bytes, bytes):
    (size, remaining) = decode_int(b, 32)
    return (remaining[:size], remaining[size:])


def decode_str(b: bytes) -> (str, bytes):
    (size, remaining) = decode_int(b, 32)
    return (remaining[:size].decode("utf-8"), remaining[size:])

# ---------- obi -----------


class BRIDGE(InterfaceScore):
    @interface
    def get_request_info(self, id: int, key1: str, key2: str) -> bytes:
        pass

    @interface
    def relay_and_verify(self, proof: bytes) -> (dict, dict):
        pass


class SIMPLE_PRICE_DB(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self.bridge_address = VarDB("bridge_address", db, value_type=Address)
        self.latest_icx_price = VarDB("latest_icx_price", db, value_type=int)
        self.latest_request_timestamp = VarDB(
            "latest_request_timestamp", db, value_type=int)
        self.latest_response_timestamp = VarDB(
            "latest_response_timestamp", db, value_type=int)
        self.multiplier = VarDB("multiplier", db, value_type=int)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    def decode_params(self, b: bytes) -> (str, int):
        (symbol, next) = decode_str(b)
        (multiplier, next) = decode_int(next, 64)
        return (symbol, multiplier)

    def decode_result(self, b: bytes) -> int:
        (price, _) = decode_int(b, 64)
        return price

    @external(readonly=True)
    def get_bridge_address(self) -> Address:
        return self.bridge_address.get()

    @external(readonly=True)
    def value(self) -> int:
        return self.latest_icx_price.get()

    @external(readonly=True)
    def get_multiplier(self) -> int:
        return self.multiplier.get()

    @external(readonly=True)
    def get_latest_request_timestamp(self) -> int:
        return self.latest_request_timestamp.get()

    @external(readonly=True)
    def get_latest_response_timestamp(self) -> int:
        return self.latest_response_timestamp.get()

    @external(readonly=True)
    def get_all_info_from_bridge(self, request_id: int) -> str:
        bridge = self.create_interface_score(self.bridge_address.get(), BRIDGE)
        info_str = ""
        # req
        info_str += bridge.get_request_info(
            request_id, "req", "client_id").decode("utf-8") + ", "
        info_str += str(int.from_bytes(bridge.get_request_info(
            request_id, "req", "oracle_script_id"), "big")) + ", "
        info_str += bridge.get_request_info(
            request_id, "req", "calldata").hex() + ", "
        info_str += str(int.from_bytes(bridge.get_request_info(
            request_id, "req", "ask_count"), "big")) + ", "
        info_str += str(int.from_bytes(bridge.get_request_info(
            request_id, "req", "min_count"), "big")) + ","
        # res
        info_str += str(int.from_bytes(bridge.get_request_info(
            request_id, "res", "ans_count"), "big")) + ", "
        info_str += str(int.from_bytes(bridge.get_request_info(
            request_id, "res", "request_time"), "big")) + ", "
        info_str += str(int.from_bytes(bridge.get_request_info(
            request_id, "res", "resolve_time"), "big")) + ", "
        info_str += str(int.from_bytes(bridge.get_request_info(
            request_id, "res", "resolve_status"), "big")) + ", "
        info_str += bridge.get_request_info(
            request_id, "res", "result").hex()

        return info_str

    @external
    def set_bridge(self, bridge_address: Address) -> None:
        self.bridge_address.set(bridge_address)

    @external
    def set_price(self, proof: bytes) -> None:
        bridge = self.create_interface_score(self.bridge_address.get(), BRIDGE)
        req_res = bridge.relay_and_verify(proof)
        oracle_script_id = req_res["req"]["oracle_script_id"]
        params = req_res["req"]["calldata"]
        result = req_res["res"]["result"]

        if oracle_script_id != 1:
            revert(
                f"error oracle script id should be 1 but got {oracle_script_id}")

        (symbol, multiplier) = self.decode_params(params)
        if symbol != "ICX":
            revert(f"error symbol should be 'ICX' but got '{symbol}'")

        price = self.decode_result(result)

        self.multiplier.set(multiplier)
        self.latest_icx_price.set(price)

        self.latest_request_timestamp.set(req_res["res"]["request_time"])
        self.latest_response_timestamp.set(req_res["res"]["resolve_time"])
