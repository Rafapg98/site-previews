"""Render das cenas no Remotion (com cache) e montagem final com FFmpeg."""
from __future__ import annotations

import http.server
import os
import socketserver
import threading
from functools import partial
from pathlib import Path

from comum import ASSETS, REMOTION, RAIZ, diga, ffmpeg, gravar_json, hash_pasta, ler_json, rodar

BUILD = REMOTION / "build"


class _ServidorComRange(http.server.SimpleHTTPRequestHandler):
    """Servidor local (127.0.0.1) que entrega os vídeos ao Remotion com suporte a Range."""

    def log_message(self, *a):
        pass

    def send_head(self):
        caminho = self.translate_path(self.path)
        rng = self.headers.get("Range")
        if not rng or not os.path.isfile(caminho):
            return super().send_head()
        tamanho = os.path.getsize(caminho)
        ini_txt, _, fim_txt = rng.replace("bytes=", "").partition("-")
        ini = int(ini_txt or 0)
        fim = int(fim_txt) if fim_txt else tamanho - 1
        fim = min(fim, tamanho - 1)
        f = open(caminho, "rb")
        f.seek(ini)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(caminho))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {ini}-{fim}/{tamanho}")
        self.send_header("Content-Length", str(fim - ini + 1))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self._restante = fim - ini + 1
        return f

    def copyfile(self, origem, destino):
        restante = getattr(self, "_restante", None)
        if restante is None:
            return super().copyfile(origem, destino)
        while restante > 0:
            bloco = origem.read(min(1 << 16, restante))
            if not bloco:
                break
            destino.write(bloco)
            restante -= len(bloco)

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()


class ServidorLocal:
    def __enter__(self):
        handler = partial(_ServidorComRange, directory=str(RAIZ))
        socketserver.ThreadingTCPServer.allow_reuse_address = True
        self.srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
        self.srv.daemon_threads = True
        self.porta = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        return self

    def url(self, caminho: Path | str) -> str:
        rel = Path(caminho).resolve().relative_to(RAIZ)
        return f"http://127.0.0.1:{self.porta}/{rel.as_posix()}"

    def __exit__(self, *a):
        self.srv.shutdown()


def hash_remotion() -> str:
    return hash_pasta(REMOTION / "src")


def garantir_bundle() -> str:
    """Empacota o projeto Remotion só quando o código mudou."""
    h = hash_remotion()
    marca_arq = BUILD / ".hash"
    if marca_arq.exists() and marca_arq.read_text() == h:
        return h
    diga("   • preparando o Remotion (empacotando as composições)…")
    rodar(["npx", "remotion", "bundle", "src/index.ts", "--out-dir", "build"], cwd=REMOTION)
    marca_arq.write_text(h)
    return h


def renderizar_cena(props: dict, composicao: str, saida: Path, escala: float = 1.0) -> None:
    saida.parent.mkdir(parents=True, exist_ok=True)
    arq_props = saida.with_suffix(".props.json")
    gravar_json(arq_props, props)
    cmd = ["npx", "remotion", "render", "build", composicao, str(saida),
           f"--props={arq_props}", f"--scale={escala}", "--log=error",
           f"--concurrency={max(1, (os.cpu_count() or 2))}", "--crf=20"]
    rodar(cmd, cwd=REMOTION)


def juntar_cenas(cenas: list[Path], saida: Path, musica: Path | None = None) -> None:
    """Concatena as cenas (já no mesmo formato) e, se houver, mistura música baixa."""
    saida.parent.mkdir(parents=True, exist_ok=True)
    lista = saida.with_suffix(".lista.txt")
    lista.write_text("".join(f"file '{c.resolve()}'\n" for c in cenas))
    if musica:
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-stream_loop", "-1", "-i", str(musica),
               "-filter_complex",
               "[1:a]volume=0.07[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=2,"
               "loudnorm=I=-14:TP=-1.5:LRA=11[a]",
               "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
               "-movflags", "+faststart", str(saida))
    else:
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-c:v", "copy",
               "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
               "-movflags", "+faststart", str(saida))
    lista.unlink(missing_ok=True)


def musica_de_fundo() -> Path | None:
    pasta = ASSETS / "musica"
    for ext in ("*.mp3", "*.wav", "*.m4a", "*.ogg"):
        achados = sorted(pasta.glob(ext))
        if achados:
            return achados[0]
    return None


def ler_cache(arq: Path) -> dict:
    return ler_json(arq, {})
