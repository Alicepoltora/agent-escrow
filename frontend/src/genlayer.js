import { createClient, createAccount } from 'genlayer-js';
import { studioDevnet } from 'genlayer-js/chains';

export const CONTRACT_ADDRESS = '0xE01D1CE3D823126A841b64475a3D97e9CfA1d009';
export const DEPLOY_TX_HASH = '0x6b61f77c8e85a30b1413528df2732079774c80d7b870b26c340cc9a90cf179f5';
export const EXPLORER_URL = 'https://explorer-studio-dev.genlayer.com';
export const RPC_URL = 'https://studio-dev.genlayer.com/api';
export const CHAIN_ID = 61997;
export const CHAIN_HEX = '0xf22d';

// Pre-funded dev / agent accounts on Studio Next
export const DEFAULT_CREATOR_KEY = '0x1344e32ee1073b2434ed058bebb0871d3109d362630e35fc0d463c68464b6138';
export const DEFAULT_CREATOR_ADDR = '0x70BEEf62DB5F4a766E07387666f95e384C57EcCF';

export const DEFAULT_WORKER_KEY = '0x7777777777777777777777777777777777777777777777777777777777777777';
export const DEFAULT_WORKER_ADDR = '0xAe72A48c1a36bd18Af168541c53037965d26e4A8';

// Create read client
export function getReadClient() {
  return createClient({ chain: studioDevnet });
}

// Create client with account
export function getWriteClient(privateKey) {
  const account = createAccount(privateKey || DEFAULT_CREATOR_KEY);
  return {
    client: createClient({ chain: studioDevnet, account }),
    account
  };
}

// Faucet funding via sim_fundAccount
export async function fundAccount(address, amountGen = '50') {
  try {
    const wei = BigInt(Math.floor(parseFloat(amountGen) * 1e18)).toString();
    const res = await fetch(RPC_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'sim_fundAccount',
        params: [address, wei],
        id: Date.now()
      })
    });
    const data = await res.json();
    return data.result;
  } catch (err) {
    console.error('Faucet fund failed:', err);
    return null;
  }
}

// Fetch real GEN balance from RPC
export async function getAccountBalance(address) {
  try {
    const res = await fetch(RPC_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'eth_getBalance',
        params: [address, 'latest'],
        id: Date.now()
      })
    });
    const data = await res.json();
    if (data && data.result) {
      const wei = BigInt(data.result);
      const gen = Number(wei) / 1e18;
      return gen.toFixed(2);
    }
  } catch (err) {
    console.warn('Failed to fetch balance:', err);
  }
  return '0.00';
}

// Fetch all tasks directly from contract storage
export async function fetchAllTasks() {
  const client = getReadClient();
  try {
    const rawTasks = await client.readContract({
      address: CONTRACT_ADDRESS,
      functionName: 'get_all_tasks',
      args: []
    });

    if (!Array.isArray(rawTasks)) return [];

    return rawTasks.map((t) => ({
      id: Number(t.id),
      creator: String(t.creator),
      worker: String(t.worker),
      spec: String(t.spec),
      payment_wei: String(t.payment_amount || t.payment_wei || '0'),
      result_url: String(t.evidence_url || t.result_url || ''),
      result_content: String(t.result_content || ''),
      status: String(t.status || 'open'),
      score: Number(t.score || 0),
      evaluation: String(t.evaluation_summary || t.evaluation || ''),
      dispute_reason: String(t.dispute_reason || ''),
      appeal_verdict: String(t.appeal_verdict || '')
    })).reverse(); // show newest first
  } catch (err) {
    console.error('Error fetching tasks from contract:', err);
    throw err;
  }
}

// Create Task
export async function createTaskOnChain(privateKey, spec, paymentGen) {
  const { client, account } = getWriteClient(privateKey);
  const paymentWei = BigInt(Math.floor(parseFloat(paymentGen) * 1e18));

  // Ensure fees are distributed per Studio Next consensus requirements
  const fees = await client.estimateTransactionFees();

  const txHash = await client.writeContract({
    address: CONTRACT_ADDRESS,
    functionName: 'create_task',
    args: [spec, paymentWei],
    fees
  });

  await client.waitForTransactionReceipt({
    hash: txHash,
    status: 'ACCEPTED',
    interval: 2500,
    retries: 40
  });

  return { txHash, creator: account.address };
}

// Submit Work
export async function submitWorkOnChain(privateKey, taskId, deliverable, evidenceUrl) {
  const { client, account } = getWriteClient(privateKey || DEFAULT_WORKER_KEY);
  const fees = await client.estimateTransactionFees();

  const txHash = await client.writeContract({
    address: CONTRACT_ADDRESS,
    functionName: 'submit_work',
    args: [BigInt(taskId), deliverable || 'Deliverable proof submitted to GenLayer contract', evidenceUrl || ''],
    fees
  });

  await client.waitForTransactionReceipt({
    hash: txHash,
    status: 'ACCEPTED',
    interval: 2500,
    retries: 40
  });

  return { txHash, worker: account.address };
}

// Evaluate Task (AI Consensus on GenVM)
export async function evaluateTaskOnChain(privateKey, taskId) {
  const { client } = getWriteClient(privateKey);
  const fees = await client.estimateTransactionFees();

  const txHash = await client.writeContract({
    address: CONTRACT_ADDRESS,
    functionName: 'evaluate_task',
    args: [BigInt(taskId)],
    fees
  });

  await client.waitForTransactionReceipt({
    hash: txHash,
    status: 'ACCEPTED',
    interval: 3000,
    retries: 50
  });

  // Read updated task from contract to return actual consensus outcome
  const task = await client.readContract({
    address: CONTRACT_ADDRESS,
    functionName: 'get_task',
    args: [BigInt(taskId)]
  });

  return {
    txHash,
    task: {
      ...task,
      id: Number(task.id),
      score: Number(task.score),
      evaluation: String(task.evaluation_summary)
    }
  };
}

// Dispute Task (Supreme AI Arbitration)
export async function disputeTaskOnChain(privateKey, taskId, reason, counterUrl = '') {
  const { client } = getWriteClient(privateKey);
  const fees = await client.estimateTransactionFees();

  const txHash = await client.writeContract({
    address: CONTRACT_ADDRESS,
    functionName: 'dispute_task',
    args: [BigInt(taskId), reason, counterUrl],
    fees
  });

  await client.waitForTransactionReceipt({
    hash: txHash,
    status: 'ACCEPTED',
    interval: 3000,
    retries: 50
  });

  const task = await client.readContract({
    address: CONTRACT_ADDRESS,
    functionName: 'get_task',
    args: [BigInt(taskId)]
  });

  return {
    txHash,
    task: {
      ...task,
      id: Number(task.id),
      appeal_verdict: String(task.appeal_verdict),
      status: String(task.status)
    }
  };
}
