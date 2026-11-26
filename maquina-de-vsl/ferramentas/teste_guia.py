"""Teste de 20 segundos do Motor A (passo 4 do /comecar).

Pega a gravação-guia do Rafael (entrada/teste-guia/*.mp4, ou o arquivo passado),
roda o pipeline inteiro e confere: corte de silêncio + legenda palavra por palavra +
pelo menos 1 zoom + pelo menos 1 SFX.

  python3 ferramentas/teste_guia.py [arquivo] [--formato 9:16]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import editar
import render
from comum import ENTRADA, FORMATOS, FPS, PROJETOS, diga, duracao, gravar_json, ler_json, marca


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo", nargs="?")
    ap.add_argument("--formato", default="9:16", choices=list(FORMATOS))
    a = ap.parse_args()
    if a.arquivo:
        bruto = Path(a.arquivo).resolve()
    else:
        achados = sorted((ENTRADA / "teste-guia").glob("*.mp4")) + sorted((ENTRADA / "teste-guia").glob("*.mov"))
        if not achados:
            diga("Coloque a gravação-guia (uns 20–30s) em entrada/teste-guia/ e rode de novo.")
            return 1
        bruto = achados[-1]
    pasta = PROJETOS / "_teste-guia"
    cena = pasta / "cenas" / "01-teste"
    diga(f"Editando {bruto.name} com o Motor A…")
    ed = editar.editar(bruto, cena, a.formato, com_broll=False)
    pal = ler_json(cena / "legenda.json", [])
    ef = ler_json(cena / "efeitos.json", {})
    m = marca()
    f = FORMATOS[a.formato]
    props = {
        "largura": f["largura"], "altura": f["altura"], "fps": FPS,
        "duracaoFrames": round(ed["duracao_cortado"] * FPS), "modo": "fala",
        "video": str(cena / "cortado.mp4"), "palavras": pal, "zooms": ef["zooms"], "textos": ef["textos"],
        "sfx": [{"t": s["t"], "src": s["arquivo"], "volume": s["volume"]} for s in ef["sfx"]],
        "brolls": [], "tela": {"tipo": "nenhuma"}, "cores": m["cores"], "lowerThird": m.get("lower_third"),
        "assinatura": m.get("assinatura", ""), "palavrasPorTela": m["legenda"]["palavras_por_tela"], "musica": None,
    }
    render.garantir_bundle()
    saida = pasta / "final" / "teste-20s-editado.mp4"
    diga("Renderizando…")
    with render.ServidorLocal() as srv:
        p = dict(props)
        p["video"] = srv.url(p["video"])
        p["sfx"] = [{**s, "src": srv.url(Path(editar.ASSETS.parent) / s["src"])} for s in p["sfx"]]
        render.renderizar_cena(p, f["composicao"], saida, 1.0)
    d_final = duracao(saida)
    checks = {
        "corte_de_silencio": ed["duracao_bruto"] - ed["duracao_cortado"] > 0.5,
        "erros_removidos": len(ed["erros_removidos"]),
        "legenda_palavra_por_palavra": len(pal) > 10,
        "zoom": len([z for z in ef["zooms"] if z["escala"] > 1.0]) >= 1,
        "sfx": len(ef["sfx"]) >= 1,
    }
    gravar_json(pasta / "resultado.json", {"bruto": str(bruto), **ed, "checks": checks, "final": str(saida)})
    diga("")
    diga(f"Bruto: {ed['duracao_bruto']:.1f}s → editado: {d_final:.1f}s")
    diga(f"   {'✅' if checks['corte_de_silencio'] else '❌'} silêncios cortados ({ed['duracao_bruto'] - ed['duracao_cortado']:.1f}s a menos)")
    for e in ed["erros_removidos"]:
        diga(f"   ✂️  {e}")
    diga(f"   {'✅' if checks['legenda_palavra_por_palavra'] else '❌'} legenda palavra por palavra ({len(pal)} palavras)")
    diga(f"   {'✅' if checks['zoom'] else '❌'} zoom punch-in ({len([z for z in ef['zooms'] if z['escala'] > 1])})")
    diga(f"   {'✅' if checks['sfx'] else '❌'} efeitos sonoros ({len(ef['sfx'])})")
    diga(f"\nVídeo: {saida.relative_to(PROJETOS.parent)}")
    return 0 if all(v for k, v in checks.items() if k != "erros_removidos") else 1


if __name__ == "__main__":
    sys.exit(main())
