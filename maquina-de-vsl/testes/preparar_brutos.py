"""Cria BRUTOS DE TESTE a partir da VSL antiga do Rafael (vsl-web.mp4 na raiz do repositório).

Não é conteúdo novo: é a voz e o rosto reais dele, recortados para simular uma gravação
de celular com pausas (ruído de sala) e um take errado repetido — assim os testes provam
que a máquina corta silêncio e erro. O recorte esconde a legenda antiga queimada no vídeo.

  python3 testes/preparar_brutos.py guia    → entrada/teste-guia/teste-20s.mp4 (9:16)
  python3 testes/preparar_brutos.py curso   → entrada/teste-curso-97/01-hook.mp4 ... (9:16)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))
from comum import ENTRADA, RAIZ, diga, ffmpeg  # noqa: E402

ORIGEM = RAIZ.parent / "vsl-web.mp4"
RECORTE_916 = "crop=338:600:481:0,scale=1080:1920"
RECORTE_169 = "crop=1040:585:120:55,scale=1920:1080"
TMP = RAIZ / "testes" / ".tmp"


def trecho(a: float, b: float, saida: Path, recorte: str) -> Path:
    ffmpeg("-ss", str(a), "-to", str(b), "-i", str(ORIGEM), "-vf", f"{recorte},fps=30,setsar=1",
           "-af", "aresample=48000", "-ac", "2",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", str(saida))
    return saida


def pausa(t_frame: float, dur: float, saida: Path, recorte: str) -> Path:
    """Pausa: imagem parada + ruído de sala baixinho (como uma gravação real)."""
    ffmpeg("-ss", str(t_frame), "-i", str(ORIGEM), "-f", "lavfi",
           "-i", f"anoisesrc=color=brown:amplitude=0.003:duration={dur}:sample_rate=48000",
           "-filter_complex", f"[0:v]trim=end_frame=1,{recorte},loop=loop=-1:size=1,fps=30,setsar=1,trim=duration={dur}[v]",
           "-map", "[v]", "-map", "1:a", "-ac", "2", "-t", str(dur),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", str(saida))
    return saida


def juntar(partes: list[Path], saida: Path) -> None:
    lista = TMP / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    saida.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "18", "-c:a", "aac", "-ar", "48000", str(saida))


def montar(roteiro, saida: Path, recorte: str) -> None:
    """roteiro: lista de ("fala", a, b) ou ("pausa", t_frame, dur)."""
    TMP.mkdir(parents=True, exist_ok=True)
    partes = []
    for i, (tipo, x, y) in enumerate(roteiro):
        arq = TMP / f"p{i:02d}.mp4"
        partes.append(trecho(x, y, arq, recorte) if tipo == "fala" else pausa(x, y, arq, recorte))
    juntar(partes, saida)
    for p in partes:
        p.unlink()


def guia() -> Path:
    saida = ENTRADA / "teste-guia" / "teste-20s.mp4"
    montar([
        ("fala", 0.0, 5.1),
        ("pausa", 5.0, 1.4),
        ("fala", 9.1, 10.7),   # take errado (frase interrompida)…
        ("pausa", 10.6, 0.9),
        ("fala", 9.1, 15.9),   # …e repetido inteiro
        ("pausa", 15.8, 1.1),
        ("fala", 20.8, 28.2),
    ], saida, RECORTE_916)
    return saida


# Trechos da VSL antiga usados como "takes" de cada bloco do teste do curso (frases inteiras).
BLOCOS_CURSO = [
    ("01-hook", [("fala", 0.0, 5.1), ("pausa", 5.0, 1.0)]),
    ("02-historia", [("fala", 20.8, 28.2), ("pausa", 28.1, 1.2), ("fala", 28.2, 32.8)]),
    ("03-mecanismo", [("fala", 63.3, 73.05)]),
    ("04-oferta", [("fala", 81.65, 89.85)]),
    ("05-ecossistema", [("fala", 73.1, 76.25), ("pausa", 76.2, 0.8), ("fala", 89.95, 93.8)]),
    ("06-prova", [("fala", 32.8, 39.9)]),
    ("07-payback", [("fala", 101.05, 109.2)]),
    ("08-garantia", [("fala", 93.95, 99.35)]),
    ("09-qualificacao", [("fala", 39.9, 46.4)]),
    ("10-cta", [("fala", 46.4, 55.2), ("pausa", 55.1, 1.0)]),
]


def curso(cortes: dict | None = None) -> list[Path]:
    saidas = []
    for nome, rot in BLOCOS_CURSO:
        if cortes and nome in cortes:
            rot = cortes[nome]
        s = ENTRADA / "teste-curso-97" / f"{nome}.mp4"
        montar(rot, s, RECORTE_916)
        saidas.append(s)
    return saidas


if __name__ == "__main__":
    if not ORIGEM.exists():
        raise SystemExit(f"Não achei {ORIGEM}")
    alvo = sys.argv[1] if len(sys.argv) > 1 else "guia"
    if alvo == "guia":
        diga(f"Bruto de teste: {guia()}")
    else:
        for s in curso():
            diga(f"Take de teste: {s}")
