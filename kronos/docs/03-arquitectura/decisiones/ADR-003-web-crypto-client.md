# ADR-003: Verificacion client-side con Web Crypto

**Estado:** aceptado
**Fecha:** 2026-10-31
**Contexto:** diseno de apps/web-verify para verificacion publica

---

## Decision

La verificacion de receipts ocurre **100% en el navegador del usuario** con crypto.subtle. Los archivos del usuario **nunca salen de su dispositivo**. Cero backend para verificacion.

## Alternativas

| Opcion | Problema |
|---|---|
| Backend recibe archivo | Privacidad (PII), storage, auth, costo |
| Backend recibe solo hash | Requiere confiar en que el backend no registra |
| Web Crypto client-side (elegido) | Requiere HTTPS o localhost, falla sobre IP LAN HTTP |

## Justificacion

- Cero PII enviada a servidores
- Cero storage. No hay archivos subidos, no hay retencion
- Cero auth. Cualquiera verifica sin cuenta
- Deploy estatico. web-verify servible desde Vercel sin funciones

## Consecuencias

Positivas:
- Reproducible offline. El receipt viaja con el documento
- Deploy gratis en Vercel free tier (100 GB/mes)
- Sin superficie de ataque server-side

Negativas:
- crypto.subtle requiere contexto seguro. Funciona en localhost y HTTPS, falla en IP LAN por HTTP
- Verificado empiricamente: VALIDO e INVALIDO probados en navegador Android real

## Codigo

apps/web-verify/public/verify.js — crypto.subtle.digest, verifyInclusion cliente-side

## Referencias

- MDN: Web Crypto API
- W3C: Web Cryptography Level 2

---

*Si el proyecto requiere SSR/SEO en el futuro, ver ADR-004.*
