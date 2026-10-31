#!/usr/bin/env node
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { sha256, sha256Leaf } from "@kronos/sha256-verifier";
import { MerkleTree } from "../packages/core-kronos/src/legado/merkle.js";
import { appendAnchor } from "../packages/core-kronos/src/legado/anchor.js";
import { buildReceipt } from "../packages/core-kronos/src/legado/receipt.js";

const [,, filePath, chainDir = ".kronos-chain"] = process.argv;
if (!filePath) { console.error("Uso: seal.mjs <archivo> [chainDir]"); process.exit(1); }

const data = await readFile(filePath);
const fileSha256 = sha256(data);
const leafHash = sha256Leaf(data);

const treePath = resolve(chainDir, "tree.json");
const anchorsPath = resolve(chainDir, "anchors.jsonl");
await mkdir(chainDir, { recursive: true });

const tree = existsSync(treePath)
  ? MerkleTree.deserialize(await readFile(treePath, "utf8"))
  : new MerkleTree();

const leafIndex = tree.append(leafHash);
const treeSize = tree.size;
const root = tree.root();
const timestamp = new Date().toISOString();

await writeFile(treePath, tree.serialize(), "utf8");
await appendAnchor(anchorsPath, { size: treeSize, root });

const proof = tree.proof(leafIndex);
const receipt = buildReceipt({ fileSha256, leafHash, leafIndex, treeSize, root, proof, timestamp });
console.log(JSON.stringify(receipt, null, 2));
