from __future__ import annotations
from . import (
    strike,
    kind,
)
import typing
from dataclasses import dataclass
from construct import Container
from solana.publickey import PublicKey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class ProductJSON(typing.TypedDict):
    market: str
    strike: strike.StrikeJSON
    dirty: bool
    kind: kind.KindJSON


@dataclass
class Product:
    layout: typing.ClassVar = borsh.CStruct(
        "market" / BorshPubkey,
        "strike" / strike.Strike.layout,
        "dirty" / borsh.Bool,
        "kind" / kind.layout,
    )
    market: PublicKey
    strike: strike.Strike
    dirty: bool
    kind: kind.KindKind

    @classmethod
    def from_decoded(cls, obj: Container) -> "Product":
        return cls(
            market=obj.market,
            strike=strike.Strike.from_decoded(obj.strike),
            dirty=obj.dirty,
            kind=kind.from_decoded(obj.kind),
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "market": self.market,
            "strike": self.strike.to_encodable(),
            "dirty": self.dirty,
            "kind": self.kind.to_encodable(),
        }

    def to_json(self) -> ProductJSON:
        return {
            "market": str(self.market),
            "strike": self.strike.to_json(),
            "dirty": self.dirty,
            "kind": self.kind.to_json(),
        }

    @classmethod
    def from_json(cls, obj: ProductJSON) -> "Product":
        return cls(
            market=PublicKey(obj["market"]),
            strike=strike.Strike.from_json(obj["strike"]),
            dirty=obj["dirty"],
            kind=kind.from_json(obj["kind"]),
        )
