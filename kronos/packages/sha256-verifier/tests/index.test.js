import { test } from "node:test";
import assert from "node:assert/strict";
import { sha256, sha256Leaf, verifyHex, seal, verifySeal } from "../src/index.js";

test("sha256 string vacio", () => {
  assert.equal(sha256(""), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
});

test("sha256 string vs buffer equivalente", () => {
  assert.equal(sha256("kronos"), sha256(Buffer.from("kronos", "utf8")));
});

test("sha256 != leafHash (domain separation)", () => {
  assert.notEqual(sha256("test"), sha256Leaf("test"));
});

test("verifyHex iguales", () => {
  const h = sha256("abc");
  assert.equal(verifyHex(h, h), true);
});

test("verifyHex case-insensitive", () => {
  const h = sha256("abc");
  assert.equal(verifyHex(h.toUpperCase(), h), true);
});

test("verifyHex distintos", () => {
  assert.equal(verifyHex(sha256("a"), sha256("b")), false);
});

test("verifyHex longitudes distintas", () => {
  assert.equal(verifyHex("abc", "abcdef"), false);
});

test("verifyHex strings nulos", () => {
  assert.equal(verifyHex(null, "abc"), false);
  assert.equal(verifyHex("abc", null), false);
  assert.equal(verifyHex("", ""), false);
});

test("seal estructura", () => {
  const s = seal("hola");
  assert.equal(s.v, 1);
  assert.equal(s.algorithm, "sha256-rfc6962");
  assert.equal(typeof s.sha256, "string");
  assert.equal(s.sha256.length, 64);
  assert.equal(typeof s.leafHash, "string");
  assert.equal(s.leafHash.length, 64);
  assert.ok(s.timestamp.match(/^\d{4}-\d{2}-\d{2}T/));
});

test("verifySeal OK", () => {
  const data = "contenido del documento";
  const s = seal(data);
  assert.deepEqual(verifySeal(data, s), { ok: true, reason: null });
});

test("verifySeal contenido alterado", () => {
  const s = seal("original");
  const r = verifySeal("alterado", s);
  assert.equal(r.ok, false);
  assert.ok(r.reason);
});

test("verifySeal version desconocida", () => {
  const r = verifySeal("x", { v: 99 });
  assert.equal(r.ok, false);
});

test("verifySeal algorithm no soportado", () => {
  const r = verifySeal("x", { v: 1, algorithm: "md5" });
  assert.equal(r.ok, false);
});

test("verifySeal seal nulo", () => {
  const r = verifySeal("x", null);
  assert.equal(r.ok, false);
});

test("seal determinista en campos no-timestamp", () => {
  const a = seal("x");
  const b = seal("x");
  assert.equal(a.sha256, b.sha256);
  assert.equal(a.leafHash, b.leafHash);
});

test("toBuffer rechaza tipos invalidos", () => {
  assert.throws(() => sha256(123), /input debe ser/);
  assert.throws(() => sha256(null), /input debe ser/);
  assert.throws(() => sha256({}), /input debe ser/);
});
