import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { MerkleTree, hashLeaf, hashNode, verifyInclusion } from "../src/legado/merkle.js";

const mk = (s) => hashLeaf(Buffer.from(s, "utf8"));

test("vacio", () => { assert.equal(new MerkleTree().root(), null); });

test("1 leaf", () => {
  const t = new MerkleTree(); t.append(mk("A"));
  assert.equal(t.root(), mk("A"));
});

test("2 leaves", () => {
  const t = new MerkleTree();
  const a = mk("A"), b = mk("B");
  t.append(a); t.append(b);
  assert.equal(t.root(), hashNode(a, b));
});

test("3 leaves promueve impar", () => {
  const t = new MerkleTree();
  const [a,b,c] = ["A","B","C"].map(mk);
  [a,b,c].forEach(h => t.append(h));
  assert.equal(t.root(), hashNode(hashNode(a,b), c));
});

test("4 leaves balanceado", () => {
  const t = new MerkleTree();
  const [a,b,c,d] = ["A","B","C","D"].map(mk);
  [a,b,c,d].forEach(h => t.append(h));
  assert.equal(t.root(), hashNode(hashNode(a,b), hashNode(c,d)));
});

test("proof N=5 verifica todos", () => {
  const t = new MerkleTree();
  const leaves = [];
  for (let i=0;i<5;i++){const h=mk("L"+i);leaves.push(h);t.append(h);}
  const root = t.root();
  for (let i=0;i<5;i++) assert.equal(verifyInclusion(leaves[i], t.proof(i), root), true);
});

test("proof N=100 verifica todos", () => {
  const t = new MerkleTree();
  const leaves = [];
  for (let i=0;i<100;i++){const h=mk("X"+i);leaves.push(h);t.append(h);}
  const root = t.root();
  for (let i=0;i<100;i++) assert.equal(verifyInclusion(leaves[i], t.proof(i), root), true);
});

test("leaf incorrecto falla", () => {
  const t = new MerkleTree();
  [mk("A"),mk("B"),mk("C")].forEach(h=>t.append(h));
  assert.equal(verifyInclusion(mk("X"), t.proof(1), t.root()), false);
});

test("proof manipulada falla", () => {
  const t = new MerkleTree();
  [mk("A"),mk("B"),mk("C"),mk("D")].forEach(h=>t.append(h));
  const tampered = t.proof(0).map(s => s ? Object.assign({},s,{hash:"f".repeat(64)}) : null);
  assert.equal(verifyInclusion(mk("A"), tampered, t.root()), false);
});

test("root falsa falla", () => {
  const t = new MerkleTree();
  [mk("A"),mk("B")].forEach(h=>t.append(h));
  assert.equal(verifyInclusion(mk("A"), t.proof(0), "f".repeat(64)), false);
});

test("serialize roundtrip", () => {
  const t = new MerkleTree();
  for (let i=0;i<10;i++) t.append(mk("s"+i));
  const t2 = MerkleTree.deserialize(t.serialize());
  assert.equal(t2.root(), t.root());
  assert.equal(t2.size, t.size);
});

test("determinismo", () => {
  const build = () => { const t=new MerkleTree(); for(let i=0;i<20;i++) t.append(mk("y"+i)); return t.root(); };
  assert.equal(build(), build());
});

test("orden importa", () => {
  const a=mk("A"), b=mk("B");
  const t1=new MerkleTree(); t1.append(a); t1.append(b);
  const t2=new MerkleTree(); t2.append(b); t2.append(a);
  assert.notEqual(t1.root(), t2.root());
});

test("domain separation", () => {
  const data = Buffer.from("test");
  const plain = createHash("sha256").update(data).digest("hex");
  assert.notEqual(hashLeaf(data), plain);
});

test("leaf formato invalido rechazado", () => {
  const t = new MerkleTree();
  assert.throws(() => t.append("xyz"), /64 hex/);
  assert.throws(() => t.append("a".repeat(63)), /64 hex/);
  assert.throws(() => t.append(123), /64 hex/);
});
