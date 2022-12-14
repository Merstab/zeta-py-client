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
from .. import types


class MarginAccountJSON(typing.TypedDict):
    authority: str
    nonce: int
    balance: int
    force_cancel_flag: bool
    open_orders_nonce: list[int]
    series_expiry: list[int]
    product_ledgers: list[types.product_ledger.ProductLedgerJSON]
    product_ledgers_padding: list[types.product_ledger.ProductLedgerJSON]
    rebalance_amount: int
    asset: types.asset.AssetJSON
    account_type: types.margin_account_type.MarginAccountTypeJSON
    padding: list[int]


@dataclass
class MarginAccount:
    discriminator: typing.ClassVar = b"\x85\xdc\xad\xd5\xb3\xd3+\xee"
    layout: typing.ClassVar = borsh.CStruct(
        "authority" / BorshPubkey,
        "nonce" / borsh.U8,
        "balance" / borsh.U64,
        "force_cancel_flag" / borsh.Bool,
        "open_orders_nonce" / borsh.U8[138],
        "series_expiry" / borsh.U64[6],
        "product_ledgers" / types.product_ledger.ProductLedger.layout[46],
        "product_ledgers_padding" / types.product_ledger.ProductLedger.layout[92],
        "rebalance_amount" / borsh.I64,
        "asset" / types.asset.layout,
        "account_type" / types.margin_account_type.layout,
        "padding" / borsh.U8[386],
    )
    authority: PublicKey
    nonce: int
    balance: int
    force_cancel_flag: bool
    open_orders_nonce: list[int]
    series_expiry: list[int]
    product_ledgers: list[types.product_ledger.ProductLedger]
    product_ledgers_padding: list[types.product_ledger.ProductLedger]
    rebalance_amount: int
    asset: types.asset.AssetKind
    account_type: types.margin_account_type.MarginAccountTypeKind
    padding: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: PublicKey,
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.Optional["MarginAccount"]:
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
    ) -> typing.List[typing.Optional["MarginAccount"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["MarginAccount"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != PROGRAM_ID:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "MarginAccount":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = MarginAccount.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            authority=dec.authority,
            nonce=dec.nonce,
            balance=dec.balance,
            force_cancel_flag=dec.force_cancel_flag,
            open_orders_nonce=dec.open_orders_nonce,
            series_expiry=dec.series_expiry,
            product_ledgers=list(
                map(
                    lambda item: types.product_ledger.ProductLedger.from_decoded(item),
                    dec.product_ledgers,
                )
            ),
            product_ledgers_padding=list(
                map(
                    lambda item: types.product_ledger.ProductLedger.from_decoded(item),
                    dec.product_ledgers_padding,
                )
            ),
            rebalance_amount=dec.rebalance_amount,
            asset=types.asset.from_decoded(dec.asset),
            account_type=types.margin_account_type.from_decoded(dec.account_type),
            padding=dec.padding,
        )

    def to_json(self) -> MarginAccountJSON:
        return {
            "authority": str(self.authority),
            "nonce": self.nonce,
            "balance": self.balance,
            "force_cancel_flag": self.force_cancel_flag,
            "open_orders_nonce": self.open_orders_nonce,
            "series_expiry": self.series_expiry,
            "product_ledgers": list(
                map(lambda item: item.to_json(), self.product_ledgers)
            ),
            "product_ledgers_padding": list(
                map(lambda item: item.to_json(), self.product_ledgers_padding)
            ),
            "rebalance_amount": self.rebalance_amount,
            "asset": self.asset.to_json(),
            "account_type": self.account_type.to_json(),
            "padding": self.padding,
        }

    @classmethod
    def from_json(cls, obj: MarginAccountJSON) -> "MarginAccount":
        return cls(
            authority=PublicKey(obj["authority"]),
            nonce=obj["nonce"],
            balance=obj["balance"],
            force_cancel_flag=obj["force_cancel_flag"],
            open_orders_nonce=obj["open_orders_nonce"],
            series_expiry=obj["series_expiry"],
            product_ledgers=list(
                map(
                    lambda item: types.product_ledger.ProductLedger.from_json(item),
                    obj["product_ledgers"],
                )
            ),
            product_ledgers_padding=list(
                map(
                    lambda item: types.product_ledger.ProductLedger.from_json(item),
                    obj["product_ledgers_padding"],
                )
            ),
            rebalance_amount=obj["rebalance_amount"],
            asset=types.asset.from_json(obj["asset"]),
            account_type=types.margin_account_type.from_json(obj["account_type"]),
            padding=obj["padding"],
        )
