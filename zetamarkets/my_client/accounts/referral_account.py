import typing
from dataclasses import dataclass
from base64 import b64decode
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID


class ReferralAccountJSON(typing.TypedDict):
    nonce: int
    referrer: str
    user: str
    timestamp: int
    pending_rewards: int
    claimed_rewards: int


@dataclass
class ReferralAccount:
    discriminator: typing.ClassVar = b"\xed\xa2PN\xc4\xe9[\x02"
    layout: typing.ClassVar = borsh.CStruct(
        "nonce" / borsh.U8,
        "referrer" / BorshPubkey,
        "user" / BorshPubkey,
        "timestamp" / borsh.U64,
        "pending_rewards" / borsh.U64,
        "claimed_rewards" / borsh.U64,
    )
    nonce: int
    referrer: PublicKey
    user: PublicKey
    timestamp: int
    pending_rewards: int
    claimed_rewards: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: PublicKey,
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.Optional["ReferralAccount"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp["result"]["value"]
        if info is None:
            return None
        if info["owner"] != str(PROGRAM_ID):
            raise ValueError("Account does not belong to this program")
        bytes_data = b64decode(info["data"][0])
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[PublicKey],
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.List[typing.Optional["ReferralAccount"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["ReferralAccount"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != PROGRAM_ID:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "ReferralAccount":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = ReferralAccount.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            nonce=dec.nonce,
            referrer=dec.referrer,
            user=dec.user,
            timestamp=dec.timestamp,
            pending_rewards=dec.pending_rewards,
            claimed_rewards=dec.claimed_rewards,
        )

    def to_json(self) -> ReferralAccountJSON:
        return {
            "nonce": self.nonce,
            "referrer": str(self.referrer),
            "user": str(self.user),
            "timestamp": self.timestamp,
            "pending_rewards": self.pending_rewards,
            "claimed_rewards": self.claimed_rewards,
        }

    @classmethod
    def from_json(cls, obj: ReferralAccountJSON) -> "ReferralAccount":
        return cls(
            nonce=obj["nonce"],
            referrer=PublicKey(obj["referrer"]),
            user=PublicKey(obj["user"]),
            timestamp=obj["timestamp"],
            pending_rewards=obj["pending_rewards"],
            claimed_rewards=obj["claimed_rewards"],
        )
