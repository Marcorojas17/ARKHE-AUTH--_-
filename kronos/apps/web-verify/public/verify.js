const $ = (s) => document.querySelector(s);
const drop = $("#drop"), fileInput = $("#file"), dropFile = $("#drop-file");
const receiptInput = $("#receipt"), btn = $("#verify"), result = $("#result");

receiptInput.placeholder = JSON.stringify({
  v: 1,
  algorithm: "sha256-rfc6962",
  fileSha256: "...",
  leafHash: "...",
  leafIndex: 0,
  treeSize: 1,
  root: "...",
  proof: [],
  timestamp: "..."
}, null, 2);

let currentFile = null;

function showResult(cls, html) {
  result.className = "result show " + cls;
  result.innerHTML = html;
}

function clearResult() {
  result.className = "result";
  result.innerHTML = "";
}

function updateButton() {
  btn.disabled = !(currentFile && receiptInput.value.trim());
}

drop.addEventListener("click", () => fileInput.click());
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("over"); });
drop.addEventListener("dragleave", () => drop.classList.remove("over"));
drop.addEventListener("drop", (e) => {
  e.preventDefault(); drop.classList.remove("over");
  if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener("change", () => { if (fileInput.files.length) handleFile(fileInput.files[0]); });
receiptInput.addEventListener("input", updateButton);

function handleFile(f) {
  currentFile = f;
  dropFile.textContent = f.name + " (" + f.size + " bytes)";
  updateButton();
  clearResult();
}

const hex = (buf) => Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");

async function sha256(bytes) {
  return hex(await crypto.subtle.digest("SHA-256", bytes));
}

async function sha256Leaf(bytes) {
  const prefix = new Uint8Array([0x00]);
  const combined = new Uint8Array(prefix.length + bytes.byteLength);
  combined.set(prefix, 0);
  combined.set(new Uint8Array(bytes), prefix.length);
  return hex(await crypto.subtle.digest("SHA-256", combined));
}

function hexToBytes(h) {
  const out = new Uint8Array(h.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(h.substr(i * 2, 2), 16);
  return out;
}

async function hashNode(leftHex, rightHex) {
  const l = hexToBytes(leftHex), r = hexToBytes(rightHex);
  const buf = new Uint8Array(1 + 32 + 32);
  buf[0] = 0x01;
  buf.set(l, 1);
  buf.set(r, 33);
  return hex(await crypto.subtle.digest("SHA-256", buf));
}

async function verifyInclusion(leafHash, proof, root) {
  let h = leafHash.toLowerCase();
  for (const step of proof) {
    if (step === null) continue;
    if (step.side === "R") h = await hashNode(h, step.hash);
    else if (step.side === "L") h = await hashNode(step.hash, h);
    else return { ok: false, computed: h };
  }
  return { ok: h === root.toLowerCase(), computed: h };
}

function checkItem(ok, label, detail) {
  const cls = ok ? "ok" : "fail";
  const marker = ok ? "OK" : "X";
  return "<li class=\"" + cls + "\"><span class=\"marker\">" + marker + "</span><span>" + label + (detail ? " — " + detail : "") + "</span></li>";
}

btn.addEventListener("click", async () => {
  if (!currentFile) return;
  btn.disabled = true;
  showResult("info", "Verificando...");
  try {
    const receipt = JSON.parse(receiptInput.value);
    if (!receipt || receipt.v !== 1) throw new Error("Receipt version invalida");
    if (receipt.algorithm !== "sha256-rfc6962") throw new Error("Algorithm no soportado: " + receipt.algorithm);

    const buf = await currentFile.arrayBuffer();
    const fileSha = await sha256(buf);
    const leaf = await sha256Leaf(buf);

    const check1 = fileSha === receipt.fileSha256;
    const check2 = leaf === receipt.leafHash;
    const inclusion = await verifyInclusion(leaf, receipt.proof, receipt.root);
    const check3 = inclusion.ok;

    const allOk = check1 && check2 && check3;
    const checks = "<ul class=\"checks\">" +
      checkItem(check1, "SHA-256 del archivo", check1 ? null : "no coincide con receipt") +
      checkItem(check2, "Leaf hash (RFC 6962)", check2 ? null : "no coincide con receipt") +
      checkItem(check3, "Proof de inclusion contra root", check3 ? null : "fallo la reconstruccion") +
      "</ul>";

    if (allOk) {
      showResult("ok",
        "<strong style=\"font-size:1.1rem;letter-spacing:.05em\">VALIDO</strong>" +
        checks +
        "<div class=\"hashes\">" +
        "<div><b>fileSha256</b>" + fileSha + "</div>" +
        "<div><b>leafHash</b>" + leaf + "</div>" +
        "<div><b>root</b>" + receipt.root + "</div>" +
        "<div><b>posicion</b>" + receipt.leafIndex + " / " + receipt.treeSize + "</div>" +
        "<div><b>sello</b>" + (receipt.timestamp || "—") + "</div>" +
        "</div>");
    } else {
      const reason = !check1 ? "SHA-256 del archivo no coincide" : !check2 ? "Leaf hash no coincide" : "Proof de inclusion fallo";
      showResult("fail",
        "<strong style=\"font-size:1.1rem;letter-spacing:.05em\">INVALIDO</strong>" +
        "<div style=\"margin:.5rem 0;opacity:.85\">" + reason + "</div>" +
        checks);
    }
  } catch (e) {
    showResult("fail", "<strong>INVALIDO</strong><div style=\"margin:.5rem 0;opacity:.85\">" + e.message + "</div>");
  } finally {
    btn.disabled = false;
  }
});
