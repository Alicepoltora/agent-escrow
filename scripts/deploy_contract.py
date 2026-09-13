"""
Deploy AgentEscrow Intelligent Contract to GenLayer StudioNet / Testnet.
Uses the funded wallet provided by the user.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eth_account import Account
import genlayer_py as gl
PRIVATE_KEY = os.getenv("GENLAYER_PRIVATE_KEY")
CONTRACT_PATH = Path(__file__).parent.parent / "contracts" / "agent_escrow.py"



def main():
    print("=" * 60)
    print("🚀 DEPLOYING AGENTESCROW INTELLIGENT CONTRACT TO GENLAYER")
    print("=" * 60)

    if not PRIVATE_KEY:
        print("❌ Error: GENLAYER_PRIVATE_KEY environment variable is not set.")
        print("Please export your private key before running:")
        print("  export GENLAYER_PRIVATE_KEY='0x...'")
        sys.exit(1)

    account = Account.from_key(PRIVATE_KEY)
    print(f"Deployer Address: {account.address}")

    client = gl.create_client(gl.studionet, account=account)
    balance_wei = client.w3.eth.get_balance(account.address)
    balance_gen = balance_wei / 1e18
    print(f"Network: GenLayer StudioNet ({gl.studionet.rpc_urls['default']['http'][0]})")
    print(f"Account Balance: {balance_gen:.4f} GEN ({balance_wei} wei)")

    if balance_wei == 0:
        raise RuntimeError(f"Account {account.address} has 0 GEN balance on StudioNet!")

    print(f"\nReading contract from: {CONTRACT_PATH}")
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        contract_code = f.read()

    print(f"Contract size: {len(contract_code)} bytes")
    print("\nInitializing consensus contract...")
    try:
        client.initialize_consensus_smart_contract()
        print("✓ Consensus smart contract initialized")
    except Exception as e:
        print(f"Note on initialize_consensus: {e}")

    print("\nSubmitting deploy transaction to GenLayer...")
    tx_hash = client.deploy_contract(
        code=contract_code,
        args=[],
        leader_only=False,
    )
    print(f"Deploy Transaction Hash: {tx_hash.hex() if hasattr(tx_hash, 'hex') else str(tx_hash)}")

    print("Waiting for transaction receipt (status: ACCEPTED)...")
    receipt = client.wait_for_transaction_receipt(
        tx_hash,
        status=TransactionStatus.ACCEPTED,
        retries=60,
        interval=3000,
        full_transaction=True,
    )

    print(f"\nTransaction confirmed!")
    print(f"Receipt status: {receipt.status}")

    # Extract contract address
    contract_address = None
    if hasattr(receipt, "contract_address") and receipt.contract_address:
        contract_address = receipt.contract_address
    elif hasattr(receipt, "data") and isinstance(receipt.data, dict) and "contract_address" in receipt.data:
        contract_address = receipt.data["contract_address"]
    elif hasattr(receipt, "tx_data_decoded") and receipt.tx_data_decoded:
        contract_address = getattr(receipt.tx_data_decoded, "contract_address", None)
    
    # Fallback inspection of receipt fields
    if not contract_address:
        for attr in ["contract_address", "recipient", "to", "result"]:
            val = getattr(receipt, attr, None)
            if val:
                print(f"Receipt field {attr}: {val}")
                if attr == "contract_address":
                    contract_address = val

    print(f"\n🎉 DEPLOYED CONTRACT ADDRESS: {contract_address}")

    # Save to artifacts
    artifacts_dir = Path(__file__).parent.parent / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    deployment_info = {
        "network": "studionet",
        "rpc_url": gl.studionet.rpc_urls['default']['http'][0],
        "deployer": account.address,
        "contract_address": str(contract_address) if contract_address else "unknown",
        "transaction_hash": tx_hash.hex() if hasattr(tx_hash, 'hex') else str(tx_hash),
        "timestamp": int(time.time()),
    }
    with open(artifacts_dir / "deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

    print(f"Deployment info saved to: {artifacts_dir / 'deployment.json'}")

    # Test reading state from deployed contract if address exists
    if contract_address:
        try:
            print("\nVerifying deployed contract state via read_contract...")
            count = client.read_contract(contract_address, "get_task_count", [])
            print(f"✓ Initial get_task_count() returned: {count}")
        except Exception as e:
            print(f"Note on initial read: {e}")

    print("\n✅ Deployment completed successfully!")
    return contract_address


if __name__ == "__main__":
    main()
