from iconservice import *

TAG = 'BRIDGE'

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


class BRIDGE(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        # request_id => bytes
        self.requests = DictDB("requests", db, value_type=bytes, depth=3)

        # address => voting_power
        self.validators = DictDB("validators", db, value_type=int)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def get_owner(self) -> Address:
        return self.owner

    @external(readonly=True)
    def get_power(self, address: Address) -> int:
        return self.validators[address]

    @external(readonly=True)
    def get_request_info(self, id: int, key1: str, key2: str) -> bytes:
        return self.requests[id][key1][key2]

    @external
    def set_validators(self, data: bytes) -> None:
        (n, validators) = decode_int(data, 32)
        size_of_each = len(validators)//n
        for i in range(n):
            l_v_vp = validators[size_of_each*i:size_of_each*(i+1)]
            (l, v_vp) = decode_int(l_v_vp, 32)
            (v, vp) = decode_bytes_fix_size(v_vp, l)
            (p, _) = decode_int(vp, 64)
            self.validators[Address.from_bytes(v)] = p

    @external
    def relay_and_verify(self, data: bytes) -> dict:
        # request packet
        req = {}
        (req["client_id"], next) = decode_str(data)
        (req["oracle_script_id"], next) = decode_int(next, 64)
        (req["calldata"], next) = decode_bytes(next)
        (req["ask_count"], next) = decode_int(next, 64)
        (req["min_count"], next) = decode_int(next, 64)

        # response packet
        res = {}
        (_, next) = decode_str(next)
        (res["request_id"], next) = decode_int(next, 64)
        (res["ans_count"], next) = decode_int(next, 64)
        (res["request_time"], next) = decode_int(next, 64)
        (res["resolve_time"], next) = decode_int(next, 64)
        (res["resolve_status"], next) = decode_int(next, 8)
        (res["result"], next) = decode_bytes(next)

        for key, value in req.items():
            self.requests[res["request_id"]]["req"][key] = value

        for key, value in res.items():
            self.requests[res["request_id"]]["res"][key] = value

        result = {}
        result["req"] = req
        result["res"] = res

        return result
