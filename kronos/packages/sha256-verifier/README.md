# @kronos/sha256-verifier

Verificacion SHA-256 con receipts portables. Cero dependencias. Node >=18.

## Instalacion

    npm i @kronos/sha256-verifier

## API

    import { sha256, sha256File, sha256Leaf, verifyHex, seal, verifySeal } from "@kronos/sha256-verifier";

    sha256("hola")                    // hex SHA-256
    await sha256File("/ruta/archivo") // hex SHA-256 de archivo
    sha256Leaf(buffer)                // SHA-256 domain-separated (RFC 6962)
    verifyHex(a, b)                   // comparacion en tiempo constante
    seal(buffer)                      // { v, algorithm, sha256, leafHash, timestamp }
    verifySeal(buffer, sealObj)       // { ok, reason }

## CLI

    kronos-hash hash <archivo>
    kronos-hash seal <archivo>  # imprime receipt JSON
    kronos-hash verify <archivo> <seal.json>

## Por que domain separation

`sha256` produce el hash estandar, interoperable con cualquier herramienta externa.
`sha256Leaf` prefija 0x00 antes de hashear, para que hojas y nodos internos de un Merkle Tree
no colisionen (second-preimage attack). Ambos se computan del mismo input.

El campo `sha256` del seal sirve para auditores externos que solo tienen `sha256sum`.
El campo `leafHash` sirve para verificar inclusion en un Merkle Tree de Kronos.

## Licencia

MIT.
