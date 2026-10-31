import { open, readFile, unlink, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { hostname } from "node:os";
import { MerkleTree } from "./merkle.js";

const STALE_MS = 300000;

async function acquireLock(path) {
  try {
    const fh = await open(path, "wx");
    await fh.writeFile(JSON.stringify({ pid: process.pid, host: hostname(), ts: Date.now() }));
    await fh.sync();
    await fh.close();
    return true;
  } catch (e) {
    if (e.code !== "EEXIST") throw e;
    let info = {};
    try { info = JSON.parse(await readFile(path, "utf8")); } catch { return false; }
    const age = Date.now() - (info.ts || 0);
    if (age < STALE_MS && info.host === hostname()) {
      try { process.kill(info.pid, 0); return false; } catch {}
    }
    await unlink(path).catch(() => {});
    return acquireLock(path);
  }
}

async function releaseLock(path) { await unlink(path).catch(() => {}); }

async function appendFsync(path, line) {
  const fh = await open(path, "a");
  try { await fh.writeFile(line); await fh.sync(); }
  finally { await fh.close(); }
}
async function readJsonl(path) {
  if (!existsSync(path)) return [];
  const raw = await readFile(path, "utf8");
  const out = [];
  const lines = raw.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const s = lines[i].trim();
    if (!s) continue;
    try { out.push(JSON.parse(s)); }
    catch { if (i >= lines.length - 2) continue; throw new Error("corrupt line " + (i+1)); }
  }
  return out;
}

async function recoverTail(path) {
  if (!existsSync(path)) return { truncated: 0 };
  const raw = await readFile(path, "utf8");
  if (!raw || raw.endsWith("\n")) return { truncated: 0 };
  const idx = raw.lastIndexOf("\n");
  const tail = idx >= 0 ? raw.slice(idx + 1) : raw;
  let validJson = false;
  try { JSON.parse(tail); validJson = true; } catch {}
  if (validJson) {
    const fh = await open(path, "a");
    try { await fh.write("\n"); await fh.sync(); } finally { await fh.close(); }
    return { truncated: 0, completed: true };
  }
  const keep = idx >= 0 ? idx + 1 : 0;
  const discarded = raw.length - keep;
  const fh = await open(path, "r+");
  try { await fh.truncate(keep); await fh.sync(); } finally { await fh.close(); }
  return { truncated: discarded };
}

export class MerkleStore {
  constructor(dir) {
    this.dir = dir;
    this.leavesPath = resolve(dir, "leaves.jsonl");
    this.rootsPath = resolve(dir, "roots.jsonl");
    this.lockPath = resolve(dir, ".lock");
    this.tree = new MerkleTree();
    this.recovery = null;
  }
  static async open(dir) {
    await mkdir(dir, { recursive: true });
    const s = new MerkleStore(dir);
    const rt = await recoverTail(s.leavesPath);
    const rr = await recoverTail(s.rootsPath);
    const leaves = await readJsonl(s.leavesPath);
    for (const l of leaves) s.tree.append(l.h);
    const roots = await readJsonl(s.rootsPath);
    const last = roots.length ? roots[roots.length - 1] : null;
    if (s.tree.size > 0) {
      const cur = s.tree.root();
      if (!last || last.size !== s.tree.size || last.root !== cur) {
        await appendFsync(s.rootsPath, JSON.stringify({ ts: new Date().toISOString(), size: s.tree.size, root: cur, recovery: true }) + "\n");
        s.recovery = { reason: "root_stale", size: s.tree.size, root: cur };
      }
    }
    s.recovery = Object.assign({}, rt, rr, s.recovery || {});
    return s;
  }
  get size() { return this.tree.size; }
  get root() { return this.tree.root(); }
  async append(leafHash) {
    const ok = await acquireLock(this.lockPath);
    if (!ok) throw new Error("lock held by another process");
    try {
      const idx = this.tree.size;
      const ts = new Date().toISOString();
      await appendFsync(this.leavesPath, JSON.stringify({ i: idx, h: leafHash, ts }) + "\n");
      this.tree.append(leafHash);
      await appendFsync(this.rootsPath, JSON.stringify({ ts, size: this.tree.size, root: this.tree.root() }) + "\n");
      return idx;
    } finally { await releaseLock(this.lockPath); }
  }
  proof(idx) { return this.tree.proof(idx); }
}
