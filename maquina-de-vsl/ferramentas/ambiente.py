"""Confere (e instala, se pedir) tudo que a máquina precisa. Usado pelo /comecar.

  python3 ferramentas/ambiente.py            # só confere
  python3 ferramentas/ambiente.py --instalar # instala o que faltar (avisando cada passo)
"""
from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys

from comum import ASSETS, CONFIG, REMOTION, diga, ler_json, marca


def versao(cmd: list[str]) -> str | None:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr).strip().splitlines()[0] if r.returncode == 0 else None
    except Exception:
        return None


def checar() -> dict:
    st = {}
    st["node"] = versao(["node", "-v"])
    st["ffmpeg"] = versao(["ffmpeg", "-version"])
    st["python"] = sys.version.split()[0]
    try:
        import faster_whisper  # noqa: F401
        st["whisper"] = faster_whisper.__version__
    except Exception:
        st["whisper"] = None
    st["modelo_whisper"] = None
    if st["whisper"]:
        try:
            from huggingface_hub import try_to_load_from_cache
            nome = marca().get("whisper", {}).get("modelo", "small")
            achou = try_to_load_from_cache(f"Systran/faster-whisper-{nome}", "model.bin")
            st["modelo_whisper"] = nome if isinstance(achou, str) else None
        except Exception:
            pass
    st["remotion"] = (REMOTION / "node_modules" / "remotion").exists()
    st["navegador_remotion"] = any((REMOTION / "node_modules" / ".remotion").glob("chrome-headless-shell/*")) if st["remotion"] else False
    st["sfx"] = ler_json(ASSETS / "sfx" / "index.json", {}).get("total", 0)
    st["marca_confirmada"] = bool(marca().get("confirmado"))
    st["chaves_env"] = (CONFIG / "chaves.env").exists()
    return st


def instalar(st: dict) -> None:
    so = platform.system()
    if not st["ffmpeg"]:
        diga("→ Instalando o FFmpeg (o 'cortador' de vídeo)…")
        if so == "Darwin" and shutil.which("brew"):
            subprocess.run(["brew", "install", "ffmpeg"], check=False)
        elif so == "Linux" and shutil.which("apt-get"):
            subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg"], check=False)
        elif so == "Windows" and shutil.which("winget"):
            subprocess.run(["winget", "install", "-e", "--id", "Gyan.FFmpeg"], check=False)
        else:
            diga("  Não consegui instalar sozinho. Mac: instale o Homebrew (brew.sh) e rode 'brew install ffmpeg'.")
    if not st["node"]:
        diga("→ Falta o Node.js (necessário para o Remotion). Baixe a versão LTS em nodejs.org e rode o /comecar de novo.")
    if not st["whisper"]:
        diga("→ Instalando o Whisper (faster-whisper) para as legendas…")
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "faster-whisper"], check=False)
    if not st["modelo_whisper"]:
        nome = marca().get("whisper", {}).get("modelo", "small")
        diga(f"→ Baixando o modelo de fala do Whisper ('{nome}', uma vez só, ~500 MB)…")
        subprocess.run([sys.executable, "-c",
                        f"from faster_whisper import WhisperModel; WhisperModel('{nome}', device='cpu', compute_type='int8')"],
                       check=False)
    if not st["remotion"]:
        diga("→ Instalando o Remotion (editor/render)…")
        subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=REMOTION, check=False)
    if not st.get("navegador_remotion"):
        diga("→ Baixando o navegador interno do Remotion…")
        subprocess.run(["npx", "remotion", "browser", "ensure"], cwd=REMOTION, check=False)
    if not st["sfx"]:
        diga("→ Montando o kit de efeitos sonoros…")
        subprocess.run([sys.executable, str(ASSETS.parent / "ferramentas" / "sfx_kit.py")], check=False)


def relatorio(st: dict) -> bool:
    linhas = [
        ("Node.js", st["node"]),
        ("FFmpeg (corte)", st["ffmpeg"] and st["ffmpeg"].split(" Copyright")[0]),
        ("Python", st["python"]),
        ("Whisper (legenda)", st["whisper"]),
        ("Modelo do Whisper", st["modelo_whisper"]),
        ("Remotion (edição/render)", "ok" if st["remotion"] else None),
        ("Navegador do Remotion", "ok" if st["navegador_remotion"] else None),
        ("Kit de SFX", f"{st['sfx']} efeitos" if st["sfx"] else None),
    ]
    tudo = True
    diga("Conferência do computador:")
    for nome, v in linhas:
        diga(f"   {'✅' if v else '❌'} {nome}: {v or 'falta'}")
        tudo = tudo and bool(v)
    diga(f"   {'✅' if st['marca_confirmada'] else '⬜'} Marca confirmada na entrevista")
    diga(f"   {'✅' if st['chaves_env'] else '⬜'} config/chaves.env (só precisa para o Motor B)")
    return tudo


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--instalar", action="store_true")
    a = ap.parse_args()
    st = checar()
    if a.instalar:
        instalar(st)
        st = checar()
    ok = relatorio(st)
    diga("\nAmbiente OK — o Motor A está pronto." if ok else "\nAinda falta algo (veja os ❌).")
    sys.exit(0 if ok else 1)
