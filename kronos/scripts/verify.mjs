#!/usr/bin/env node
// Uso: node scripts/verify.mjs <archivo> <receipt.json>
import { readFile } from 'node:fs/promises';
import { verifyReceipt } from '../packages/core-kronos/src/legado/receipt.js';

const [,, filePath, receiptPath] = process.argv;
if (!filePath || !receiptPath) {
  console.error('Uso: verify.mjs <archivo> <receipt.json>'); process.exit(1);
}
const fileBytes = await readFile(filePath);
const receipt = JSON.parse(await readFile(receiptPath, 'utf8'));
const result = verifyReceipt(fileBytes, receipt);
console.log(result.ok ? `OK ${receipt.root}` : `FAIL ${result.reason}`);
process.exit(result.ok ? 0 : 2);
