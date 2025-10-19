from cosmpy.aerial.client import LedgerClient, NetworkConfig

config = NetworkConfig(
    chain_id="dorado-1",
    url="grpc+https://grpc-dorado.fetch.ai:443",  # ✅ gRPC endpoint
    fee_minimum_gas_price=0.025,
    fee_denomination="afet",
    staking_denomination="afet"
)

ledger = LedgerClient(config)
ledger = LedgerClient(config)

# ✅ Print network info
print("✅ Connected to Fetch.ai network")
print("Chain ID:", config.chain_id)

# ✅ Get latest block height
latest_height = ledger.query_height()
print("Latest block height:", latest_height)
