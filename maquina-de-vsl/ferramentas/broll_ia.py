"""B-roll: real primeiro, gráfico (custo zero) como padrão, IA só se o projeto ligar.

Ordem de preferência para cada marca de B-roll do plano de efeitos:
  1. B-roll REAL das obras dele em assets/broll-real/ (nome do arquivo contém o termo,
     ex.: "google-perfil.mp4", "obra-cozinha.mp4"). Nunca fingimos que IA é obra dele.
  2. B-roll gráfico do Remotion (cartão animado com o termo) — custo zero.
  3. B-roll por IA (fal.ai, texto→vídeo, ~3–5s), SÓ se projeto.broll_ia.ligado = true com
     autorização e custo aceito. Sempre ilustrativo genérico.
"""
from __future__ import annotations

from pathlib import Path

import apis
from comum import ASSETS, diga, gravar_json, hash_dados, ler_json
from editar import normalizar

MODELO_BROLL = "fal-ai/kling-video/v2.1/standard/text-to-video"

PROMPTS = {
    "LLC": "close-up of business registration paperwork on a desk, construction company office, cinematic, no text",
    "Google": "smartphone showing a local business map listing, contractor truck in background, cinematic, no logos",
    "Site": "laptop showing a clean construction company website, job site in background, cinematic, no readable text",
    "Website": "laptop showing a clean construction company website, job site in background, cinematic, no readable text",
    "Dashboard": "tablet with charts and project timeline on a job site table, cinematic, no readable text",
    "Orçamento": "contractor reviewing an estimate on a clipboard inside a renovated kitchen, cinematic",
    "Orçamentos": "contractor reviewing estimates on a clipboard inside a renovated kitchen, cinematic",
}


def preencher(proj: dict, cena_dir: Path) -> None:
    arq = cena_dir / "efeitos.json"
    ef = ler_json(arq, {})
    reais = list((ASSETS / "broll-real").glob("*.mp4")) + list((ASSETS / "broll-real").glob("*.mov"))
    mudou = False
    for b in ef.get("brolls", []):
        chave = b.get("chave") or normalizar(b["termo"])
        real = next((r for r in reais if chave and normalizar(r.stem).startswith(chave)), None)
        if real:
            b.update({"fonte": "real", "src": str(real)})
            mudou = True
            continue
        if not proj.get("broll_ia", {}).get("ligado"):
            continue
        prompt = PROMPTS.get(b["termo"])
        if not prompt:
            continue
        destino = ASSETS.parent / "projetos" / proj["slug"] / "broll" / f"{hash_dados(prompt)}.mp4"
        if not destino.exists():
            diga(f"   • B-roll IA: {b['termo']} (custo aprovado)…")
            cab = {"Authorization": f"Key {apis.chave('FAL_KEY')}"}
            import time
            ped = apis.chamar(proj["slug"], "fal_broll", f"https://queue.fal.run/{MODELO_BROLL}",
                              {"prompt": prompt, "duration": "5", "aspect_ratio": "16:9" if proj["formato"] == "16:9" else "9:16"}, cab)
            for _ in range(240):
                st = apis.chamar(proj["slug"], "fal_broll", ped["status_url"], None, cab, metodo="GET")
                if st.get("status") == "COMPLETED":
                    break
                time.sleep(5)
            res = apis.chamar(proj["slug"], "fal_broll", ped["response_url"], None, cab, metodo="GET")
            apis.baixar(res["video"]["url"], destino)
        b.update({"fonte": "ia", "src": str(destino)})
        mudou = True
    if mudou:
        gravar_json(arq, ef)
