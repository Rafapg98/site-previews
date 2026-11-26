"""Monta o kit de efeitos sonoros (100+) e o índice por categoria.

- assets/sfx/pack-100-cc0/      → "100 CC0 SFX" (OpenGameArt, domínio público CC0)
- assets/sfx/kenney-interface/  → "Interface Sounds" do Kenney (CC0)
- assets/sfx/assinatura/        → whoosh, riser, punch, pop, ding gerados aqui com FFmpeg
                                  (sintéticos, sem direitos de terceiros)

Uso: python3 ferramentas/sfx_kit.py   (refaz assinatura/ e index.json)
"""
from __future__ import annotations

import re
from pathlib import Path

from comum import ASSETS, diga, ffmpeg, gravar_json

SFX = ASSETS / "sfx"
ASSIN = SFX / "assinatura"

# nome → expressão aevalsrc (ou None para ruído) e duração
RECEITAS = {
    # whooshes: ruído rosa com envelope sobe-desce e filtro
    "whoosh_curto": ("ruido", 0.45, "lowpass=f=2800,highpass=f=300"),
    "whoosh_medio": ("ruido", 0.7, "lowpass=f=2200,highpass=f=200"),
    "whoosh_grave": ("ruido", 0.8, "lowpass=f=1200,highpass=f=80"),
    "whoosh_agudo": ("ruido", 0.5, "lowpass=f=6000,highpass=f=900"),
    # risers: varredura de frequência subindo
    "riser_1s": ("0.25*sin(2*PI*(180*t+260*t*t))*(t/1.0)", 1.0, "highpass=f=120"),
    "riser_2s": ("0.25*sin(2*PI*(120*t+180*t*t))*(t/2.0)", 2.0, "highpass=f=90"),
    # impacto/punch para zoom de virada
    "punch_grave": ("0.9*sin(2*PI*52*t)*exp(-9*t)+0.3*sin(2*PI*104*t)*exp(-14*t)", 0.55, "lowpass=f=900"),
    "punch_seco": ("0.8*sin(2*PI*70*t)*exp(-16*t)", 0.35, "lowpass=f=1400"),
    # pops para texto animado
    "pop_1": ("0.5*sin(2*PI*(950-2400*t)*t)*exp(-28*t)", 0.22, "highpass=f=200"),
    "pop_2": ("0.5*sin(2*PI*(1250-3000*t)*t)*exp(-30*t)", 0.2, "highpass=f=250"),
    "pop_3": ("0.45*sin(2*PI*(700-1600*t)*t)*exp(-24*t)", 0.25, "highpass=f=150"),
    # ding para revelar preço
    "ding_preco": ("0.35*sin(2*PI*1318*t)*exp(-4*t)+0.25*sin(2*PI*1975*t)*exp(-5*t)", 1.2, "highpass=f=300"),
    "caixa_registradora": ("0.3*sin(2*PI*2093*t)*exp(-6*t)+0.3*sin(2*PI*2637*(t-0.09))*exp(-6*(t-0.09))*gte(t,0.09)", 1.0, "highpass=f=400"),
}

CATEGORIAS = {
    "whoosh": [r"^assinatura/whoosh"],
    "riser": [r"^assinatura/riser"],
    "punch": [r"^assinatura/punch", r"hit_"],
    "pop": [r"^assinatura/pop", r"plop", r"pluck", r"drop_00[1-4]"],
    "ding": [r"^assinatura/ding", r"^assinatura/caixa", r"bell", r"confirmation", r"glass_0[1-2]"],
    "clique": [r"click", r"tick", r"switch_", r"select"],
    "transicao": [r"scroll", r"open_", r"close_", r"maximize", r"minimize"],
    "impacto": [r"slam", r"metal", r"gong", r"explosion"],
    "obra": [r"tools", r"wooden", r"wooded", r"machine", r"door"],
    "erro": [r"error", r"glitch", r"question"],
}


def gerar_assinatura() -> None:
    ASSIN.mkdir(parents=True, exist_ok=True)
    for nome, (expr, dur, filtro) in RECEITAS.items():
        saida = ASSIN / f"{nome}.wav"
        if expr == "ruido":
            meio = dur * 0.55
            env = f"if(lt(t,{meio}),pow(t/{meio},2),pow(({dur}-t)/({dur}-{meio}),2))"
            ffmpeg("-f", "lavfi", "-i", f"anoisesrc=color=pink:duration={dur}:amplitude=0.6",
                   "-af", f"volume='{env}':eval=frame,{filtro},afade=t=out:st={dur - 0.05}:d=0.05",
                   "-ar", "48000", "-ac", "2", str(saida))
        else:
            ffmpeg("-f", "lavfi", "-i", f"aevalsrc='{expr}':s=48000:d={dur}",
                   "-af", f"{filtro},afade=t=out:st={max(0, dur - 0.05)}:d=0.05", "-ac", "2", str(saida))


def indexar() -> dict:
    arquivos = sorted(str(p.relative_to(SFX)) for p in SFX.rglob("*") if p.suffix in {".ogg", ".wav", ".mp3"})
    cats = {}
    for cat, padroes in CATEGORIAS.items():
        cats[cat] = [f"assets/sfx/{a}" for a in arquivos if any(re.search(p, a) for p in padroes)]
    indice = {
        "_licencas": {
            "pack-100-cc0": "CC0 (domínio público) — '100 CC0 SFX', OpenGameArt",
            "kenney-interface": "CC0 — Kenney 'Interface Sounds' (ver LICENCA-CC0.txt)",
            "assinatura": "Gerados pela máquina com FFmpeg (sem direitos de terceiros)",
        },
        "total": len(arquivos),
        "categorias": cats,
        "todos": [f"assets/sfx/{a}" for a in arquivos],
    }
    gravar_json(SFX / "index.json", indice)
    return indice


if __name__ == "__main__":
    gerar_assinatura()
    i = indexar()
    diga(f"Kit de SFX pronto: {i['total']} efeitos.")
    for c, l in i["categorias"].items():
        diga(f"  {c:10s} {len(l)}")
