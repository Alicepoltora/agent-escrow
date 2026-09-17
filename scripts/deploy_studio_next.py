import genlayer_py as gl
from eth_account import Account
import copy
import time

pk = '0x1344e32ee1073b2434ed058bebb0871d3109d362630e35fc0d463c68464b6138'
account = Account.from_key(pk)
print('Deployer:', account.address)

studio_next_chain = copy.deepcopy(gl.studionet)
studio_next_chain.id = 61997
studio_next_chain.name = 'GenLayer Studio Next'
studio_next_chain.rpc_urls = {'default': {'http': ['https://studio-dev.genlayer.com/api']}}

client = gl.create_client(studio_next_chain, account=account)
bal = client.w3.eth.get_balance(account.address)
print(f'Balance: {bal / 1e18} GEN')

with open('/root/agent-escrow/contracts/agent_escrow.py', 'r') as f:
    code = f.read()

# Update code for v0.3.0
adapted = code.replace(
    '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }',
    '# v0.3.0\n# { "Depends": "py-genlayer:5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng" }'
)
adapted = adapted.replace("from genlayer import *\nimport genlayer.gl.vm as glvm", "import genlayer as gl\nfrom genlayer.types import *")
adapted = adapted.replace("@allow_storage", "@gl.storage.allow")
adapted = adapted.replace("class AgentEscrow(gl.Contract):", "class AgentEscrow(gl.contract.Contract):")
adapted = adapted.replace("TreeMap[", "gl.storage.TreeMap[")

with open('/root/agent-escrow/contracts/agent_escrow_v3.py', 'w') as f:
    f.write(adapted)

print('Deploying contract to Studio Next (chain 61997)...')
try:
    tx_hash = client.deploy_contract(code=adapted, args=[], leader_only=False)
    tx_hex = tx_hash.hex() if hasattr(tx_hash, 'hex') else str(tx_hash)
    print('Deploy tx hash:', tx_hex)
    receipt = client.wait_for_transaction_receipt(tx_hash, status=gl.TransactionStatus.ACCEPTED, retries=60, interval=3000)
    print('Receipt status:', receipt.status)
    addr = getattr(receipt, 'contract_address', None)
    if not addr and hasattr(receipt, 'data') and isinstance(receipt.data, dict):
        addr = receipt.data.get('contract_address')
    if not addr:
        for a in ['contract_address', 'recipient', 'to', 'result']:
            val = getattr(receipt, a, None)
            if val:
                print(f'Field {a}: {val}')
                if a == 'contract_address': addr = val
    print('🎉 DEPLOYED CONTRACT ADDRESS:', addr)
except Exception as e:
    import traceback
    traceback.print_exc()
