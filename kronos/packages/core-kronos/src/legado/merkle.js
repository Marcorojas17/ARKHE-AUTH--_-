import { createHash } from "node:crypto";
export { sha256Leaf as hashLeaf } from "@kronos/sha256-verifier";

const NODE_PREFIX = Buffer.from([0x01]);
const HEX64 = /^[0-9a-f]{64}$/;

export function hashNode(leftHex, rightHex) {
  return createHash("sha256")
    .update(NODE_PREFIX)
    .update(Buffer.from(leftHex, "hex"))
    .update(Buffer.from(rightHex, "hex"))
    .digest("hex");
}

export class MerkleTree {
  constructor() {
    this.levels = [[]];
  }
  get size() { return this.levels[0].length; }
  root() {
    if (this.size === 0) return null;
    const top = this.levels[this.levels.length - 1];
    return top[0];
  }
  append(leafHashHex) {
    if (typeof leafHashHex !== "string" || !HEX64.test(leafHashHex.toLowerCase())) {
      throw new Error("leafHash debe ser 64 hex chars");
    }
    const idx = this.levels[0].length;
    this.levels[0].push(leafHashHex.toLowerCase());
    this._recomputeFrom(idx);
    return idx;
  }
  _recomputeFrom(leafIdx) {
    let idx = leafIdx;
    let lvl = 0;
    while (true) {
      if (lvl + 1 >= this.levels.length) this.levels.push([]);
      const cur = this.levels[lvl];
      const parent = this.levels[lvl + 1];
      const parentIdx = idx >> 1;
      if ((idx & 1) === 0) {
        if (idx + 1 < cur.length) {
          parent[parentIdx] = hashNode(cur[idx], cur[idx + 1]);
        } else {
          parent[parentIdx] = cur[idx];
        }
      } else {
        parent[parentIdx] = hashNode(cur[idx - 1], cur[idx]);
      }
      if (parent.length <= 1) return;
      idx = parentIdx;
      lvl++;
    }
  }
  proof(leafIdx) {
    if (leafIdx < 0 || leafIdx >= this.size) {
      throw new Error("indice " + leafIdx + " fuera de rango [0, " + this.size + ")");
    }
    const path = [];
    let idx = leafIdx;
    for (let lvl = 0; lvl < this.levels.length - 1; lvl++) {
      const cur = this.levels[lvl];
      if ((idx & 1) === 0) {
        if (idx + 1 < cur.length) path.push({ side: "R", hash: cur[idx + 1] });
        else path.push(null);
      } else {
        path.push({ side: "L", hash: cur[idx - 1] });
      }
      idx >>= 1;
    }
    return path;
  }
  serialize() {
    return JSON.stringify({ v: 1, leaves: this.levels[0] });
  }
  static deserialize(json) {
    const { v, leaves } = JSON.parse(json);
    if (v !== 1) throw new Error("version " + v + " desconocida");
    if (!Array.isArray(leaves)) throw new Error("campo leaves invalido");
    const t = new MerkleTree();
    for (const h of leaves) t.append(h);
    return t;
  }
}

export function verifyInclusion(leafHashHex, proof, rootHex) {
  let h = leafHashHex.toLowerCase();
  for (const step of proof) {
    if (step === null) continue;
    if (step.side === "R") h = hashNode(h, step.hash);
    else if (step.side === "L") h = hashNode(step.hash, h);
    else throw new Error("side invalido: " + step.side);
  }
  return h === rootHex.toLowerCase();
}
