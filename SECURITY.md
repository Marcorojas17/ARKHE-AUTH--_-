# Security Policy

## Reportar una vulnerabilidad

**No** abras un issue público para vulnerabilidades de seguridad.

Contacto privado: **marco.a.rojas.v@hotmail.com**

- Tiempo de respuesta esperado: 72 horas
- Divulgación coordinada: 90 días o hasta el fix, lo que ocurra primero
- Cifrado del reporte: si necesitas PGP, escríbeme y te envío mi clave

## Alcance

Aplica a:
- Firma ML-DSA-87 (`core/signer/`)
- Verificador offline (`core/verifier/`)
- API pública (`api/main.py`)
- Contrato JSON Schema (`spec/verification-v1.json`)

## Fuera de alcance

- Túneles `trycloudflare.com` (infraestructura de Cloudflare)
- Red Bitcoin (infraestructura externa)
- Termux y paquetes de su repositorio

## Versiones soportadas

| Versión | Soportada |
|---------|-----------|
| 0.1.x   | ✅        |
