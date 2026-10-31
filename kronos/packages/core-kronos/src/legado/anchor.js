// Log append-only de raíces. Cada línea: {"ts":..., "size":N, "root":"hex"}
// Permite probar "el documento X existía cuando el árbol tenía root R".
// En producción esto se replica fuera de banda (on-chain, fase 5).
import { appendFile, readFile } from 'node:fs/promises';

export async function appendAnchor(path, { size, root }) {
  if (typeof size !== 'number' || size < 0) throw new Error('size inválido');
  if (typeof root !== 'string' || root.length !== 64) throw new Error('root inválido');
  const entry = { ts: new Date().toISOString(), size, root: root.toLowerCase() };
  await appendFile(path, JSON.stringify(entry) + '\n', 'utf8');
  return entry;
}

export async function readAnchors(path) {
  const content = await readFile(path, 'utf8');
  return content.split('\n').filter(Boolean).map((l, i) => {
    try { return JSON.parse(l); }
    catch { throw new Error(`línea ${i + 1} corrupta en ${path}`); }
  });
}

export async function latestAnchor(path) {
  const anchors = await readAnchors(path);
  return anchors.length ? anchors[anchors.length - 1] : null;
}
