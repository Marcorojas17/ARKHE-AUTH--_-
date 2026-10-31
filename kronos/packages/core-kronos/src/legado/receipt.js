import { sha256, sha256Leaf } from "@kronos/sha256-verifier";
import { verifyInclusion } from "./merkle.js";

export function buildReceipt({ fileSha256, leafHash, leafIndex, treeSize, root, proof, timestamp }) {
  return {
    v: 1,
    fileSha256,
    leafHash,
    leafIndex,
    treeSize,
    root,
    proof,
    timestamp,
    algorithm: "sha256-rfc6962"
  };
}

export function verifyReceipt(fileBytes, receipt) {
  if (!receipt || receipt.v !== 1) {
    return { ok: false, reason: "receipt version invalida o ausente" };
  }
  if (receipt.algorithm !== "sha256-rfc6962") {
    return { ok: false, reason: "algorithm " + receipt.algorithm + " no soportado" };
  }
  const fileSha256 = sha256(fileBytes);
  if (fileSha256 !== receipt.fileSha256) {
    return { ok: false, reason: "file sha256 no coincide" };
  }
  const leafHash = sha256Leaf(fileBytes);
  if (leafHash !== receipt.leafHash) {
    return { ok: false, reason: "leaf hash no coincide" };
  }
  if (!verifyInclusion(leafHash, receipt.proof, receipt.root)) {
    return { ok: false, reason: "proof de inclusion fallo contra root" };
  }
  return { ok: true, reason: null };
}
