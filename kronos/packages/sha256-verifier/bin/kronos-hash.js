#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { sha256File, seal, verifySeal } from "../src/index.js";

const [, , cmd, ...args] = process.argv;

function usage() {
  console.error("Uso:");
  console.error("  kronos-hash hash <archivo>");
  console.error("  kronos-hash seal <archivo>");
  console.error("  kronos-hash verify <archivo> <seal.json>");
}

async function main() {
  if (cmd === "hash") {
    if (!args[0]) { usage(); process.exit(1); }
    console.log(await sha256File(args[0]));
    return;
  }
  if (cmd === "seal") {
    if (!args[0]) { usage(); process.exit(1); }
    console.log(JSON.stringify(seal(await readFile(args[0])), null, 2));
    return;
  }
  if (cmd === "verify") {
    if (!args[0] || !args[1]) { usage(); process.exit(1); }
    const buf = await readFile(args[0]);
    const s = JSON.parse(await readFile(args[1], "utf8"));
    const r = verifySeal(buf, s);
    console.log(r.ok ? "OK" : "FAIL " + r.reason);
    process.exit(r.ok ? 0 : 2);
  }
  usage();
  process.exit(1);
}

main().catch((e) => { console.error(e.message); process.exit(1); });
