import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PUBLIC = join(__dirname, "public");
const PORT = Number(process.env.PORT) || 3000;
const HOST = process.env.HOST || "127.0.0.1";

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js":   "text/javascript; charset=utf-8",
  ".css":  "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg":  "image/svg+xml"
};

function safePath(urlPath) {
  const clean = urlPath.split("?")[0];
  const base = clean === "/" ? "index.html" : clean;
  const candidates = base.includes(".") ? [base] : [base + ".html", base + "/index.html", base];
  for (const c of candidates) {
    const resolved = normalize(join(PUBLIC, c));
    if (resolved.startsWith(PUBLIC) && existsSync(resolved)) return resolved;
  }
  return null;
}

const server = createServer(async (req, res) => {
  if (req.url === "/api/health") {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ ok: true, service: "web-verify", ts: new Date().toISOString() }));
    return;
  }
  const path = safePath(req.url || "/");
  if (!path) { res.writeHead(400); res.end("bad path"); return; }
  try {
    const data = await readFile(path);
    const ct = MIME[extname(path)] || "application/octet-stream";
    res.writeHead(200, {
      "content-type": ct,
      "cache-control": "no-cache",
      "x-content-type-options": "nosniff",
      "x-frame-options": "DENY",
      "referrer-policy": "no-referrer"
    });
    res.end(data);
  } catch (e) {
    if (e.code === "ENOENT") { res.writeHead(404); res.end("not found"); }
    else { console.error(e); res.writeHead(500); res.end("internal error"); }
  }
});

server.listen(PORT, HOST, () => {
  console.log("web-verify en http://" + HOST + ":" + PORT);
  console.log("health: http://" + HOST + ":" + PORT + "/api/health");
});
