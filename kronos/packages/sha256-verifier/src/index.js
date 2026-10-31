import { createHash, timingSafeEqual } from "node:crypto";
import { readFile } from "node:fs/promises";

const LEAF_PREFIX = Buffer.from([0x00]);

function toBuffer(input) {
  if (Buffer.isBuffer(input)) return input;
  if (typeof input === "string") return Buffer.from(input, "utf8");
  if (input instanceof Uint8Array) return Buffer.from(input);
  throw new TypeError("input debe ser Buffer, Uint8Array o string");
}

export function sha256(input) {
  return createHash("sha256").update(toBuffer(input)).digest("hex");
}

export async function sha256File(path) {
  const buf = await readFile(path);
  return sha256(buf);
}

export function sha256Leaf(input) {
  return createHash("sha256").update(LEAF_PREFIX).update(toBuffer(input)).digest("hex");
}

export function verifyHex(expected, actual) {
  if (typeof expected !== "string" || typeof actual !== "string") return false;
  const a = Buffer.from(expected.toLowerCase(), "hex");
  const b = Buffer.from(actual.toLowerCase(), "hex");
  if (a.length !== b.length || a.length === 0) return false;
  return timingSafeEqual(a, b);
}

export function seal(input) {
  const buf = toBuffer(input);
  return {
    v: 1,
    algorithm: "sha256-rfc6962",
    sha256: sha256(buf),
    leafHash: sha256Leaf(buf),
    timestamp: new Date().toISOString()
  };
}

export function verifySeal(input, sealObj) {
  if (!sealObj || sealObj.v !== 1) return { ok: false, reason: "seal version invalido o ausente" };
  if (sealObj.algorithm !== "sha256-rfc6962") return { ok: false, reason: "algorithm " + sealObj.algorithm + " no soportado" };
  const buf = toBuffer(input);
  if (!verifyHex(sha256(buf), sealObj.sha256)) return { ok: false, reason: "sha256 no coincide" };
  if (!verifyHex(sha256Leaf(buf), sealObj.leafHash)) return { ok: false, reason: "leafHash no coincide" };
  return { ok: true, reason: null };
}
