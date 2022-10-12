import asyncio
import sys
import json
import base58
sys.path.append("../")

from newclient import Client as ZetaClient
from exchange import Exchange
from network import Network
import var_types as types
import assets
import utils
import network

from anchorpy import Wallet
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair

keypair = Keypair()

SERVER_URL = "https://server.zeta.markets"
NETWORK_URL = "https://api.devnet.solana.com"

connection = Client(NETWORK_URL, utils.default_commitment())

wallet = PublicKey("8LpEYmLf7LUcd3aEKNSmNZyYmzD8osbacK4Qb4WGTv3o")

# connection.request_airdrop(wallet, 100000000)
mint_auth = PublicKey("SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt")

PROGRAM_ID = PublicKey("BG3oRikW8d16YjUEmX3ZxHm9SiJzrGtMhsSR8aCw1Cd7")
# Fill this ins
conn = AsyncClient(NETWORK_URL)

STARTING_BALANCE = 5000

def cb(asset: assets.Asset, event, data):
    print("Asset: " + str(asset))

async def main():

    our_keypair = Keypair.from_secret_key(b"D\xc3\x9a\xfc7\x00\x17$kP\x07\xcbJn\xb7\xc0\xc3\x08H\xd72\x14\xc9\r\x04.\xa9\x929\xed\xea+e3\x04M\xd9T\x10\x97\x00\x0b\xedw'\xc2\xcd\xff\x99\x96\xc9$;\x99\xce\x07\xa0\x19\xfb_\x06\xd3\xd9\xe6")
    wll = Wallet(our_keypair)

    print("omegalulw")
    print(wll.public_key)

    import httpx
    async with httpx.AsyncClient() as client:
        print("we vibin")
        res = await client.post(
            f"{SERVER_URL}/faucet/USDC",
            data=json.dumps(
                {
                    "key": str(keypair.public_key),
                    "amount": 10000,
                }
            ),
            headers={"Content-Type": "application/json"},
        )

    exc = Exchange("","","","")
    assets_in_exchange = [assets.Asset.SOL, assets.Asset.BTC]
    await exc._init(PROGRAM_ID, network.Network.DEVNET, conn, wallet, utils.default_commitment(), assets_in_exchange)
    await exc.load(PROGRAM_ID, network.Network.DEVNET, conn, utils.default_commitment(), wallet, 0, assets_in_exchange, cb)

    cl = await ZetaClient.load(conn, wll, utils.default_commitment(), cb, 0)
    deposit_transaction = await cl.deposit(assets.Asset.SOL, 52)

    print(deposit_transaction)

asyncio.run(main())
