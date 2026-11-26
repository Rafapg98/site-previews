"""Utilidades compartilhadas da Máquina de VSL (caminhos, config, FFmpeg, hash, log)."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "config"
ASSETS = RAIZ / "assets"
ENTRADA = RAIZ / "entrada"
PROJETOS = RAIZ / "projetos"
REMOTION = RAIZ / "remotion"

FORMATOS = {
    "16:9": {"largura": 1920, "altura": 1080, "composicao": "Cena169"},
    "9:16": {"largura": 1080, "altura": 1920, "composicao": "Cena916"},
}
FPS = 30


def diga(msg: str) -> None:
    """Mensagem em português simples para o Rafael."""
    print(msg, flush=True)


def erro(msg: str, codigo: int = 1) -> None:
    print(f"\n✋ {msg}", file=sys.stderr, flush=True)
    sys.exit(codigo)


def ler_json(caminho: Path, padrao=None):
    if not caminho.exists():
        return padrao
    return json.loads(caminho.read_text(encoding="utf-8"))


def gravar_json(caminho: Path, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def marca() -> dict:
    return ler_json(CONFIG / "marca.json", {})


def produtos() -> dict:
    return ler_json(CONFIG / "produtos.json", {})


def rodar(cmd: list[str], silencioso: bool = True, **kw) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=silencioso, text=True, **kw)
    if r.returncode != 0:
        detalhe = (r.stderr or "")[-2500:] if silencioso else ""
        raise RuntimeError(f"Comando falhou: {' '.join(cmd[:4])}...\n{detalhe}")
    return r


def ffmpeg(*args: str) -> None:
    rodar(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args])


def duracao(arquivo: Path) -> float:
    r = rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", str(arquivo)])
    return float(r.stdout.strip())


def tem_audio(arquivo: Path) -> bool:
    r = rodar(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
               "stream=index", "-of", "csv=p=0", str(arquivo)])
    return bool(r.stdout.strip())


def extrair_wav16k(video: Path, saida: Path) -> Path:
    ffmpeg("-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(saida))
    return saida


def ler_wav_float(caminho: Path):
    import numpy as np
    with wave.open(str(caminho)) as w:
        dados = w.readframes(w.getnframes())
    return np.frombuffer(dados, dtype=np.int16).astype(np.float32) / 32768.0


def hash_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()[:16]


def hash_dados(dados) -> str:
    return hashlib.sha256(json.dumps(dados, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def hash_pasta(pasta: Path, padroes=("**/*.ts", "**/*.tsx", "**/*.css")) -> str:
    h = hashlib.sha256()
    for p in padroes:
        for arq in sorted(pasta.glob(p)):
            h.update(str(arq.relative_to(pasta)).encode())
            h.update(arq.read_bytes())
    return h.hexdigest()[:16]


def carregar_chaves() -> dict:
    """Lê config/chaves.env (local). Nunca imprime valores."""
    chaves = {}
    arq = CONFIG / "chaves.env"
    if arq.exists():
        for linha in arq.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            k, v = linha.split("=", 1)
            if v.strip():
                chaves[k.strip()] = v.strip()
    return chaves


def precisa(programa: str) -> bool:
    return shutil.which(programa) is not None


def moeda(valor: float) -> str:
    """US$ 1.750 / US$ 9,90 (formato brasileiro)."""
    if abs(valor - round(valor)) < 1e-9:
        return "US$ " + f"{int(round(valor)):,}".replace(",", ".")
    inteiro, dec = f"{valor:,.2f}".split(".")
    return "US$ " + inteiro.replace(",", ".") + "," + dec


os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
