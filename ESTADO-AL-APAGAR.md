# Protocolos de Internet — estado al apagar (2026-08-26)

## Lo único que falta

Mergear el PR **#50** (el clasificador me bloquea `gh pr merge`):

    cd ~/Documentos/github/codeaerospace_contenido-algebra && gh pr merge 50 --merge

Y después, retomar diciendo **"continuamos con el curso de protocolos de
internet"**: el plan y la memoria tienen el resto.

## Dónde está todo

- Plan y tablero: `docs/plan_contenido/curso-23-protocolos-internet.md`
- Rama: `curso/protocolos-internet` (todo commiteado y empujado)
- 96 renders `qh`: `render_jobs/qh/protocolos-internet-*/ClipN.mp4`
- 18 vídeos publicados: `~/Documentos/github/codeaerospace_contenido/exports/`

## Estado

| Lote | Contenido | Estado |
|---|---|---|
| 1 | Paquetes, capas, Ethernet, IP, CIDR, IPv6 | publicado (PR #47) |
| 2 | Ruteo y transporte | publicado (PR #48) |
| 3 | DNS, NAT, ICMP, HTTP, TLS, QUIC | publicado (PR #49) |
| 4 | CDN, colas, tiempo real, órbita, DTN, CCSDS | **PR #50 sin mergear** |

24 lecciones escritas y validadas · 96 clips · 18 en producción, narradas y
muxeadas · los 24 `qh` del lote 4 ya hechos, listos para subir.

## Pasos del lote 4 tras el merge

1. VPS: `git pull` + `subir_curso.py` ×6
2. `scp` de los qh a `/root/staging-protocolos/{7-1,7-2,7-3,8-1,8-2,8-3}`
3. `adoptar_renders.py` con fragmentos **cortos y sin tildes** (`· 7.1`)
4. Narración **serial** (nunca en paralelo: 429 del TTS)
5. Mux local con la marca sonora; medir picos y re-muxear los que pasen de
   −0.5 dB
