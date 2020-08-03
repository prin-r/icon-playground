from iconservice import *

TAG = 'BRIDGE_2'


# =-=-=-=-=-=-=-=-=-=-=-=-= OBI =-=-=-=-=-=-=-=-=-=-=-=-=


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

# =-=-=-=-=-=-=-=-=-=-=-=-= OBI =-=-=-=-=-=-=-=-=-=-=-=-=


# =-=-=-=-=-=-=-=-=-=-=-=-= \Sha256 =-=-=-=-=-=-=-=-=-=-=-=-=
F32 = 0xFFFFFFFF

_k = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
      0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
      0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
      0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
      0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
      0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
      0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
      0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
      0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
      0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
      0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
      0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
      0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
      0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
      0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
      0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

_h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]


def _pad(msglen):
    mdi = msglen & 0x3F
    length = (msglen << 3).to_bytes(8, byteorder='big')

    if mdi < 56:
        padlen = 55 - mdi
    else:
        padlen = 119 - mdi

    return b'\x80' + (b'\x00' * padlen) + length


def _rotr(x, y):
    return ((x >> y) | (x << (32 - y))) & F32


def _maj(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)


def _ch(x, y, z):
    return (x & y) ^ ((~x) & z)


def _compress(c, hh):
    k = _k[:]
    w = [0] * 64
    w[0:16] = tuple([int.from_bytes(c[i*4:i*4+4], byteorder='big')
                     for i in range(16)])

    for i in range(16, 64):
        s0 = _rotr(w[i-15], 7) ^ _rotr(w[i-15], 18) ^ (w[i-15] >> 3)
        s1 = _rotr(w[i-2], 17) ^ _rotr(w[i-2], 19) ^ (w[i-2] >> 10)
        w[i] = (w[i-16] + s0 + w[i-7] + s1) & F32

    a, b, c, d, e, f, g, h = hh

    for i in range(64):
        s0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
        t2 = s0 + _maj(a, b, c)
        s1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
        t1 = h + s1 + _ch(e, f, g) + k[i] + w[i]

        h = g
        g = f
        f = e
        e = (d + t1) & F32
        d = c
        c = b
        b = a
        a = (t1 + t2) & F32

    for i, (x, y) in enumerate(zip(hh, [a, b, c, d, e, f, g, h])):
        hh[i] = (x + y) & F32

    return hh


def update(counter, cache, m, h):
    if not m:
        return counter, cache, h

    counter += len(m)
    m = cache + m

    for i in range(0, len(m) // 64):
        h = _compress(m[64 * i:64 * (i + 1)], h)
    cache = m[-(len(m) % 64):]

    return counter, cache, h


def sha256(_m):
    output_size = 8
    counter, cache, h = update(0, b'', _m, _h[:])
    m = _pad(counter)
    counter, cache, h = update(counter, cache, _pad(counter), h)
    data = [(i).to_bytes(4, byteorder='big') for i in h[:output_size]]
    return b''.join(data)

# =-=-=-=-=-=-=-=-=-=-=-=-= /Sha256 =-=-=-=-=-=-=-=-=-=-=-=-=

# =-=-=-=-=-=-=-=-=-=-=-=-= \ECRecoverPubKey =-=-=-=-=-=-=-=-=-=-=-=-=


_p = 115792089237316195423570985008687907853269984665640564039457584007908834671663
_n = 115792089237316195423570985008687907852837564279074904382605163141518161494337
_a = 0
_b = 7
_gx = int('79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798', 16)
_gy = int('483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8', 16)
_g = (_gx, _gy)


def inv_mod(a, n=_p):
    lm, hm = 1, 0
    low, high = a % n, n
    while low > 1:
        ratio = high//low
        nm, new = hm-lm*ratio, high-low*ratio
        lm, low, hm, high = nm, new, lm, low
    return lm % n


def ecc_add(a, b):
    l = ((b[1] - a[1]) * inv_mod(b[0] - a[0])) % _p
    x = (l*l - a[0]-b[0]) % _p
    y = (l*(a[0] - x) - a[1]) % _p
    return (x, y)


def ecc_double(a):
    l = ((3*a[0]*a[0]+_a) * inv_mod((2*a[1]))) % _p
    x = (l*l-2*a[0]) % _p
    y = (l*(a[0]-x)-a[1]) % _p
    return (x, y)


def ecc_mul(point, scalar):
    if scalar == 0 or scalar >= _p:
        revert("INVALID_SCALAR_OR_PRIVATEKEY")
    scalar_bin = str(bin(scalar))[2:]
    q = point
    for i in range(1, len(scalar_bin)):
        q = ecc_double(q)
        if scalar_bin[i] == "1":
            q = ecc_add(q, point)
    return (q)


def to_base(n, b):
    if(n < 2):
        return [n]
    temp = n
    ans = []
    while(temp != 0):
        ans = [temp % b] + ans
        temp //= b
    return ans


def ecc_sqrt(n, p):
    n %= p
    if(n == 0 or n == 1):
        return (n, -n % p)
    phi = p - 1
    if(pow(n, phi//2, p) != 1):
        return ()
    if(p % 4 == 3):
        ans = pow(n, (p+1)//4, p)
        return (ans, -ans % p)
    aa = 0
    for i in range(1, p):
        temp = pow((i*i-n) % p, phi//2, p)
        if(temp == phi):
            aa = i
            break
    exponent = to_base((p+1)//2, 2)

    def cipolla_mult(ab, cd, w, p):
        a, b = ab
        c, d = cd
        return ((a*c+b*d*w) % p, (a*d+b*c) % p)
    x1 = (aa, 1)
    x2 = cipolla_mult(x1, x1, aa*aa-n, p)
    for i in range(1, len(exponent)):
        if(exponent[i] == 0):
            x2 = cipolla_mult(x2, x1, aa*aa-n, p)
            x1 = cipolla_mult(x1, x1, aa*aa-n, p)
        else:
            x1 = cipolla_mult(x1, x2, aa*aa-n, p)
            x2 = cipolla_mult(x2, x2, aa*aa-n, p)

    return (x1[0], -x1[0] % p)


def ecrecover(_e: bytes, _r: bytes, _s: bytes, v):
    e = int.from_bytes(_e, "big")
    r = int.from_bytes(_r, "big")
    s = int.from_bytes(_s, "big")

    x = r % _n
    y1, y2 = ecc_sqrt(r*r*r + r*_a + _b, _p)
    if y1 % 2 == y2 % 2:
        revert(f'ECRECOVER_ERROR: y1%2 == y2%2, ({y1},{y2})')

    if v == 27:
        y = y1 if y1 % 2 == 0 else y2
    elif v == 28:
        y = y1 if y1 % 2 == 1 else y2
    else:
        revert(f'ECRECOVER_ERROR: v must be 27 or 28 but got {v}')

    R = (x, y % _n)
    r_inv = inv_mod(x, _n)
    gxh = ecc_mul(_g, -e % _n)

    pub = ecc_mul(ecc_add(gxh, ecc_mul(R, s)), r_inv)

    return bytes.fromhex("%064x" % pub[0] + "%064x" % pub[1])

# =-=-=-=-=-=-=-=-=-=-=-=-= /ECRecoverPubKey =-=-=-=-=-=-=-=-=-=-=-=-=

# =-=-=-=-=-=-=-=-=-=-=-=-= \Utils =-=-=-=-=-=-=-=-=-=-=-=-=


def merkle_leaf_hash(value: bytes) -> bytes:
    return sha256(b'\x00' + value)


def merkle_inner_hash(left: bytes, right: bytes) -> bytes:
    return sha256(b'\x01' + left + right)


# =-=-=-=-=-=-=-=-=-=-=-=-= /Utils =-=-=-=-=-=-=-=-=-=-=-=-=


class BRIDGE_2(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        # address => voting_power
        self.validator_powers = DictDB("validator_powers", db, value_type=int)
        # total validator power
        self.total_validator_power = VarDB(
            "total_validator_power", db, value_type=int)
        # str => str
        self.test = DictDB("test", db, value_type=str)

    def on_install(self) -> None:
        super().on_install()
        self.test["t1"] = merkle_leaf_hash(b'aaa').hex()

    def on_update(self) -> None:
        super().on_update()

    # =-=-=-=-=-=-=-=-=-=-=-=-= \Utils =-=-=-=-=-=-=-=-=-=-=-=-=

    @external(readonly=True)
    def merkle_leaf_hash(self, value: bytes) -> bytes:
        return sha256(b'\x00' + value)

    @external(readonly=True)
    def merkle_inner_hash(self, left: bytes, right: bytes) -> bytes:
        return sha256(b'\x01' + left + right)

    @external(readonly=True)
    def encode_varint_unsigned(self, value: int) -> bytes:
        temp_value = value
        size = 0
        while temp_value > 0:
            size += 1
            temp_value >>= 7

        result = b''
        temp_value = value
        for i in range(size):
            result += (128 | (temp_value & 127)).to_bytes(1, "big")
            temp_value >>= 7

        return result[:size - 1] + (result[size - 1] & 127).to_bytes(1, "big")

    @external(readonly=True)
    def encode_varint_signed(self, value: int) -> bytes:
        return self.encode_varint_unsigned(value * 2)

    # =-=-=-=-=-=-=-=-=-=-=-=-= /Utils =-=-=-=-=-=-=-=-=-=-=-=-=

    # =-=-=-=-=-=-=-=-=-=-=-=-= \BlockHeaderMerkleParts =-=-=-=-=-=-=-=-=-=-=-=-=

    @external(readonly=True)
    def get_block_header(self, data: bytes, app_hash: bytes, block_height: int) -> bytes:
        return merkle_inner_hash(  # [BlockHeader]
            merkle_inner_hash(  # [3A]
                merkle_inner_hash(  # [2A]
                    data[0:32],  # [1A]
                    merkle_inner_hash(  # [1B]
                        merkle_leaf_hash(  # [2]
                            self.encode_varint_unsigned(block_height)
                        ),
                        data[32:64]  # [3]
                    )
                ),
                data[64:96]  # [2B]
            ),
            merkle_inner_hash(  # [3B]
                merkle_inner_hash(  # [2C]
                    data[96:128],  # [1E]
                    merkle_inner_hash(  # [1F]
                        merkle_leaf_hash(  # [A]
                            (32).to_bytes(1, "big") + app_hash
                        ),
                        data[128:160]  # [B]
                    )
                ),
                data[160:192]  # [2D]
            )
        )

    # =-=-=-=-=-=-=-=-=-=-=-=-= /BlockHeaderMerkleParts =-=-=-=-=-=-=-=-=-=-=-=-=

    # =-=-=-=-=-=-=-=-=-=-=-=-= \TMSignature =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    @external(readonly=True)
    def recover_signer(
        self,
        r: bytes,
        s: bytes,
        v: int,
        signed_data_prefix: bytes,
        signed_data_suffix: bytes,
        block_hash: bytes
    ) -> bytes:
        return ecrecover(sha256(signed_data_prefix+block_hash+signed_data_suffix), r, s, v)

    @external(readonly=True)
    def recover_signers(self, signatures: bytes, block_hash: bytes) -> list:
        pubkeys = []
        len_sigs, remaining = decode_int(signatures, 32)
        for i in range(len_sigs):
            r, remaining = decode_bytes(remaining)
            s, remaining = decode_bytes(remaining)
            v, remaining = decode_int(remaining, 8)
            signed_data_prefix, remaining = decode_bytes(remaining)
            signed_data_suffix, remaining = decode_bytes(remaining)
            pubkeys.append(self.recover_signer(r, s, v, signed_data_prefix,
                                               signed_data_suffix, block_hash))
        return pubkeys

    # =-=-=-=-=-=-=-=-=-=-=-=-= /TMSignature =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # =-=-=-=-=-=-=-=-=-=-=-=-= \IAVLMerklePath =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    @external(readonly=True)
    def get_parent_hash(
        self,
        is_data_on_right: bool,
        subtree_height: int,
        subtree_size: int,
        subtree_version: int,
        sibling_hash: bytes,
        data_subtree_hash: bytes
    ) -> bytes:
        left_subtree = sibling_hash if is_data_on_right else data_subtree_hash
        right_subtree = data_subtree_hash if is_data_on_right else sibling_hash
        return sha256(
            ((subtree_height << 1) & 255).to_bytes(1, "big") +
            self.encode_varint_signed(subtree_size) +
            self.encode_varint_signed(subtree_version) +
            (32).to_bytes(1, "big") +
            left_subtree +
            (32).to_bytes(1, "big") +
            right_subtree
        )

    # =-=-=-=-=-=-=-=-=-=-=-=-= /IAVLMerklePath =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # =-=-=-=-=-=-=-=-=-=-=-=-= \MultiStore =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Computes Tendermint's application state hash at this given block. AppHash is actually a
    # Merkle hash on muliple stores.
    #                         ________________[AppHash]_______________
    #                        /                                        \
    #             _______[I9]______                          ________[I10]________
    #            /                  \                       /                     \
    #       __[I5]__             __[I6]__              __[I7]__               __[I8]__
    #      /         \          /         \           /         \            /         \
    #    [I1]       [I2]     [I3]        [I4]       [8]        [9]          [A]        [B]
    #   /   \      /   \    /    \      /    \
    # [0]   [1]  [2]   [3] [4]   [5]  [6]    [7]
    # [0] - acc      [1] - distr   [2] - evidence  [3] - gov
    # [4] - main     [5] - mint    [6] - oracle    [7] - params
    # [8] - slashing [9] - staking [A] - supply    [D] - upgrade
    # Notice that NOT all leaves of the Merkle tree are needed in order to compute the Merkle
    # root hash, since we only want to validate the correctness of [6] In fact, only
    # [7], [I3], [I5], and [I10] are needed in order to compute [AppHash].

    @external(readonly=True)
    def get_app_hash(
        self,
        multi_store: bytes,
    ) -> bytes:
        acc_to_gov_stores_merkle_hash = multi_store[0:32]  # [I5]
        main_and_mint_stores_merkle_hash = multi_store[32:64]  # [I3]
        oracle_iavl_state_hash = multi_store[64:96]  # [6]
        params_stores_merkle_hash = multi_store[96:128]  # [7]
        slashing_to_upgrade_stores_merkle_hash = multi_store[128:160]  # [I10]
        return (
            merkle_inner_hash(  # [AppHash]
                merkle_inner_hash(  # [I9]
                    acc_to_gov_stores_merkle_hash,  # [I5]
                    merkle_inner_hash(  # [I6]
                        main_and_mint_stores_merkle_hash,  # [I3]
                        merkle_inner_hash(
                            merkle_leaf_hash(  # [I4]
                                # [6]
                                # oracle prefix (uint8(6) + "oracle" + uint8(32))
                                bytes.fromhex("066f7261636c6520") +
                                sha256(sha256(oracle_iavl_state_hash))
                            ),
                            params_stores_merkle_hash  # [7]
                        )
                    )
                ),
                slashing_to_upgrade_stores_merkle_hash  # [I10]
            )
        )

    # =-=-=-=-=-=-=-=-=-=-=-=-= /MultiStore =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # =-=-=-=-=-=-=-=-=-=-=-=-= \Bridge =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def relay_oracle_state(
        self,
        block_height: int,
        multi_store: bytes,
        merkle_parts: bytes,
        signatures: bytes,
    ) -> bytes:
        app_hash = self.get_app_hash(multi_store)
        block_hash = self.get_block_header(
            merkle_parts,
            app_hash,
            block_height
        )
        recover_signers = self.recover_signers(signatures, block_hash)

        sum_voting_power = 0
        signers_checking = set()
        for signer in recover_signers:
            if signer in signers_checking:
                revert(f'REPEATED_PUBKEY_FOUND: {signer}')

            signers_checking.add(signer)
            sum_voting_power += self.validator_powers[signer]

        if sum_voting_power * 3 <= self.total_validator_power.get() * 2:
            revert("INSUFFICIENT_VALIDATOR_SIGNATURES")

        return multi_store[64:96]

    # =-=-=-=-=-=-=-=-=-=-=-=-= /Bridge =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    @external
    def set_validators(self, data: bytes) -> None:
        (n, remaining) = decode_int(data, 32)
        sum_power = 0
        for i in range(n):
            (pub_key, remaining) = decode_bytes(data)
            if len(pub_key) != 64:
                revert(
                    f'PUBKEY_SHOULD_BE_64_BYTES_BUT_GOT_{len(pub_key)}_BYTES')

            (power, remaining) = decode_int(data, 64)

            self.validators[pub_key] = power
            sum_power += power

        self.total_validator_power.set(sum_power)

    @external(readonly=True)
    def get_test(self) -> str:
        return self.test["t1"]

    @external
    def set_test(self, data: bytes, app_hash: bytes, block_height: int) -> None:
        self.test["t1"] = self.get_block_header(
            data, app_hash, block_height).hex()

    @external
    def set_test_1(
        self,
        signed_data_prefix: bytes,
        signed_data_suffix: bytes,
        r: bytes,
        s: bytes,
        v: int,
        block_hash: bytes
    ) -> None:
        self.test["t1"] = self.recover_signer(
            r, s, v, signed_data_prefix, signed_data_suffix, block_hash).hex()

    @external(readonly=True)
    def hello(self) -> str:
        Logger.debug(f'Hello, world!', TAG)
        return "Hello"

    @external(readonly=True)
    def get_test_1(
        self,
        e: bytes,
        r: bytes,
        s: bytes,
        v: int
    ) -> str:
        return ecrecover(e, r, s, v).hex()
