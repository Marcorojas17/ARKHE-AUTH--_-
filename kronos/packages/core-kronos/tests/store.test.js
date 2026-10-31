import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, rm, writeFile, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { existsSync } from "node:fs";
import { MerkleStore } from "../src/legado/store.js";
import { hashLeaf } from "../src/legado/merkle.js";

const mk = (s) => hashLeaf(Buffer.from(s, "utf8"));

test("open dir vacio", async () => {
  const dir = await mkdtemp(join(tmpdir(), "kronos-store-"));
  const s = await MerkleStore.open(dir);
  assert.equal(s.size, 0);
  assert.equal(s.root, null);
  await rm(dir, { recursive: true });
});

test("append 3 hojas persiste tras reopen", async () => {
  const dir = await mkdtemp(join(tmpdir(), "kronos-store-"));
  const s = await MerkleStore.open(dir);
  await s.append(mk("A"));
  await s.append(mk("B"));
  await s.append(mk("C"));
  const s2 = await MerkleStore.open(dir);
  assert.equal(s2.size, 3);
  assert.equal(s2.root, s.root);
  await rm(dir, { recursive: true });
});

test("lock stale se recupera", async () => {
  const dir = await mkdtemp(join(tmpdir(), "kronos-store-"));
  const s = await MerkleStore.open(dir);
  await writeFile(join(dir, ".lock"), JSON.stringify({ pid: 999999, host: "fake", ts: Date.now() - 10000000 }));
  await s.append(mk("A"));
  assert.equal(s.size, 1);
  await rm(dir, { recursive: true });
});
test("recovery trunca linea parcial", async () => {
  const dir = await mkdtemp(join(tmpdir(), "kronos-store-"));
  const s = await MerkleStore.open(dir);
  await s.append(mk("A"));
  await s.append(mk("B"));
  const p = join(dir, "leaves.jsonl");
  const c = await readFile(p, "utf8");
  await writeFile(p, c.slice(0, -1));
  const s2 = await MerkleStore.open(dir);
  assert.equal(s2.size, 2);
  assert.ok(s2.recovery.truncated >= 0);
  await rm(dir, { recursive: true });
});

test("root stale regenerada", async () => {
  const dir = await mkdtemp(join(tmpdir(), "kronos-store-"));
  const s = await MerkleStore.open(dir);
  await s.append(mk("A"));
  await rm(join(dir, "roots.jsonl"));
  const s2 = await MerkleStore.open(dir);
  assert.equal(s2.size, 1);
  assert.ok(existsSync(join(dir, "roots.jsonl")));
  const lines = (await readFile(join(dir, "roots.jsonl"), "utf8")).trim().split("\n");
  assert.equal(lines.length, 1);
  await rm(dir, { recursive: true });
});

test("proof funciona tras reopen", async () => {
  const dir = await mkdtemp(join(tmpdir(), "kronos-store-"));
  const s = await MerkleStore.open(dir);
  const leaves = [];
  for (let i = 0; i < 5; i++) { const h = mk("L" + i); leaves.push(h); await s.append(h); }
  const s2 = await MerkleStore.open(dir);
  const { verifyInclusion } = await import("../src/legado/merkle.js");
  for (let i = 0; i < 5; i++) assert.equal(verifyInclusion(leaves[i], s2.proof(i), s2.root), true);
  await rm(dir, { recursive: true });
});
