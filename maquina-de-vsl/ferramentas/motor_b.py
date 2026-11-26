"""MOTOR B — avatar + voz clonada. DESLIGADO por padrão.

Só roda quando:
  1. o Rafael disse explicitamente "usa o motor B nesta VSL" (gravado em projeto.json), e
  2. o custo foi mostrado e aceito.
Quem garante isso é apis.chamar() — este arquivo não fala com a internet por conta própria.

Fluxo por bloco: texto da fala → ElevenLabs (voz clonada dele) → fal.ai (avatar com
lip-sync a partir da foto/vídeo-base dele) → vídeo que entra no mesmo editor do Motor A
(legenda, zoom, SFX), como se fosse um take.

Arquivos-base (gravados no /comecar, passo 5): assets/motor-b/foto-base.jpg (ou .png).
"""
from __future__ import annotations

import base64
import time
from pathlib import Path

import apis
from roteiro import renderizar
from comum import ASSETS, diga, ffmpeg

MODELO_AVATAR_PADRAO = "veed/fabric-1.0"   # imagem + áudio → vídeo falando (fal.ai)


def _data_uri(arq: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(arq.read_bytes()).decode()


def gerar_voz(proj: dict, bloco: dict, destino: Path) -> Path:
    voz = apis.chave("ELEVENLABS_VOICE_ID")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voz}?output_format=mp3_44100_128"
    audio = apis.chamar(proj["slug"], "elevenlabs", url,
                        {"text": renderizar(bloco["fala"]), "model_id": "eleven_multilingual_v2"},
                        {"xi-api-key": apis.chave("ELEVENLABS_API_KEY")}, binario=True)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(audio)
    return destino


def gerar_avatar(proj: dict, audio: Path, destino: Path) -> Path:
    foto = next((p for p in (ASSETS / "motor-b").glob("foto-base.*")), None)
    if not foto:
        raise apis.APIBloqueada("Falta assets/motor-b/foto-base.jpg (passo 5 do /comecar).")
    modelo = proj.get("motor_b", {}).get("modelo_avatar", MODELO_AVATAR_PADRAO)
    cab = {"Authorization": f"Key {apis.chave('FAL_KEY')}"}
    mime = "image/png" if foto.suffix.lower() == ".png" else "image/jpeg"
    pedido = apis.chamar(proj["slug"], "fal_avatar", f"https://queue.fal.run/{modelo}",
                         {"image_url": _data_uri(foto, mime), "audio_url": _data_uri(audio, "audio/mpeg"),
                          "resolution": "720p"}, cab)
    status_url, resposta_url = pedido["status_url"], pedido["response_url"]
    for _ in range(240):
        st = apis.chamar(proj["slug"], "fal_avatar", status_url, None, cab, metodo="GET")
        if st.get("status") == "COMPLETED":
            break
        time.sleep(5)
    else:
        raise RuntimeError("O avatar demorou demais na fal.ai.")
    res = apis.chamar(proj["slug"], "fal_avatar", resposta_url, None, cab, metodo="GET")
    return apis.baixar(res["video"]["url"], destino)


def gerar_bruto(proj: dict, bloco: dict, cena_dir: Path) -> Path:
    """Gera (ou reaproveita) o 'take sintético' do bloco."""
    bruto = cena_dir / "motor_b_bruto.mp4"
    texto_arq = cena_dir / "motor_b_texto.txt"
    fala = renderizar(bloco["fala"])
    if bruto.exists() and texto_arq.exists() and texto_arq.read_text() == fala:
        return bruto
    diga("   • Motor B: gerando voz clonada e avatar (custo aprovado)…")
    audio = gerar_voz(proj, bloco, cena_dir / "motor_b_voz.mp3")
    video = gerar_avatar(proj, audio, cena_dir / "motor_b_avatar.mp4")
    ffmpeg("-i", str(video), "-c", "copy", str(bruto))
    texto_arq.write_text(fala)
    return bruto
