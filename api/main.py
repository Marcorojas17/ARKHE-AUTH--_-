"""Arkhe Auth API — firma, verificacion y PWA con FastAPI."""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import base64
import json
import os
import sys

from core.signer.signer import sign_artifact, load_pk
from core.verifier.verifier import verify_receipt

app = FastAPI(title="Arkhe Auth API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/v1/keys")
def keys(): return {"ML-DSA-87": base64.b64encode(load_pk()).decode()}

@app.post("/v1/sign")
async def sign(
    file: UploadFile = File(...),
    author: str = Form("Anonimo"),
    origin: str = Form("Humano"),
    ai_tool: str = Form("Ninguna")
):
    data = await file.read()
    if not data:
        raise HTTPException(400, "archivo vacio")
    
    # Límite de 50MB para evitar caídas del túnel o falta de memoria en el móvil
    if len(data) > 50 * 1024 * 1024:
        raise HTTPException(413, "El archivo supera el límite de 50MB")

    receipt = sign_artifact(data)
    receipt["metadata"] = {"author": author, "origin": origin, "ai_tool": ai_tool}
    return receipt

@app.post("/v1/verify")
async def verify(file: UploadFile = File(...), receipt: UploadFile = File(...)):
    try:
        r = json.loads(await receipt.read())
    except Exception:
        raise HTTPException(400, "receipt no es JSON valido")
    return verify_receipt(await file.read(), r)

if getattr(sys, 'frozen', False):
    WEB_DIR = os.path.join(sys._MEIPASS, 'web')
else:
    WEB_DIR = "web"

if os.path.exists(WEB_DIR):
    app.mount("/app", StaticFiles(directory=WEB_DIR, html=True), name="app")
    @app.get("/")
    def redirect_to_app(): return RedirectResponse(url="/app/")
