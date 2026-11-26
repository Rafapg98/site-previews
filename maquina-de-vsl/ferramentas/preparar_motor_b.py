"""Confere a gravação-base do Motor B e prepara os arquivos (tudo local, custo zero).

  python3 ferramentas/preparar_motor_b.py entrada/motor-b/gravacao-base.mp4

Checa: duração (60–120s), resolução, fundo silencioso (sem música/ruído), cortes de edição.
Se passar: assets/motor-b/voz-clone.wav (para o clone no ElevenLabs) e assets/motor-b/foto-base.jpg (avatar).
Não chama nenhuma API.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

from comum import ASSETS, diga, duracao, ffmpeg, ler_wav_float, rodar

DESTINO = ASSETS / "motor-b"


def resolucao(v: Path) -> tuple[int, int]:
    r = rodar(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
               "-of", "csv=p=0:s=x", str(v)])
    w, h = r.stdout.strip().split("x")[:2]
    return int(w), int(h)


def piso_de_ruido(wav: Path) -> float:
    a = ler_wav_float(wav)
    janela = 800  # 50 ms a 16 kHz
    fr = a[: len(a) // janela * janela].reshape(-1, janela)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    return float(np.percentile(db, 5))


def cortes(v: Path) -> list[float]:
    r = rodar(["ffmpeg", "-hide_banner", "-i", str(v), "-vf", "scale=320:-2,scdet=threshold=6", "-an", "-f", "null", "-"])
    return [float(x) for x in re.findall(r"lavfi\.scd\.time: ([\d.]+)", r.stderr)]


def main(arquivo: str) -> int:
    v = Path(arquivo)
    DESTINO.mkdir(parents=True, exist_ok=True)
    d = duracao(v)
    w, h = resolucao(v)
    wav = DESTINO / "_tmp16k.wav"
    ffmpeg("-i", str(v), "-vn", "-ac", "1", "-ar", "16000", str(wav))
    piso = piso_de_ruido(wav)
    wav.unlink()
    cs = cortes(v)
    menor_lado = min(w, h)
    checks = [
        ("Duração 60–120 s", 60 <= d <= 120, f"{d:.0f} s"),
        ("Resolução ≥ 1080p", menor_lado >= 1080, f"{w}×{h}"),
        ("Fundo silencioso (sem música/ruído)", piso < -50, f"piso {piso:.0f} dB (precisa < −50 dB)"),
        ("Tomada contínua (sem cortes)", len(cs) == 0, f"{len(cs)} corte(s)"),
    ]
    diga("Conferência da gravação-base do Motor B:")
    for nome, ok, det in checks:
        diga(f"   {'✅' if ok else '❌'} {nome}: {det}")
    if not all(ok for _, ok, _ in checks):
        diga("\nNão serve ainda. Veja assets/motor-b/ROTEIRO-GRAVACAO.md e grave de novo.")
        return 1
    # áudio para o clone: limpa graves, normaliza, mantém qualidade alta
    ffmpeg("-i", str(v), "-vn", "-ac", "1", "-ar", "44100", "-af", "highpass=f=70,loudnorm=I=-18:TP=-2",
           str(DESTINO / "voz-clone.wav"))
    # foto do avatar: 1 s dentro do vídeo (você parado, boca fechada)
    ffmpeg("-ss", "1.0", "-i", str(v), "-frames:v", "1", "-q:v", "2", str(DESTINO / "foto-base.jpg"))
    diga("\n✅ Pronto: assets/motor-b/voz-clone.wav (sobe no ElevenLabs) e assets/motor-b/foto-base.jpg (avatar).")
    diga("Nada foi enviado para nenhum serviço.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        diga("Uso: python3 ferramentas/preparar_motor_b.py entrada/motor-b/gravacao-base.mp4")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
