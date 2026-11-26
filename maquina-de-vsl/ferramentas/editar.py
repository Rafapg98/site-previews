"""MOTOR A — edita uma gravação REAL do Rafael.

Passos (equivalente ao workflow FFmpeg + Whisper + efeitos automáticos):
  1. Whisper transcreve o bruto com tempo de cada palavra.
  2. Acha silêncios (FFmpeg silencedetect) e frases.
  3. Remove erros: frase com a palavra "corta" (o sinal dele de "errei") e
     frases que recomeçam igual à seguinte (take repetido → fica o último).
  4. Corta e junta com FFmpeg (já no formato 16:9 ou 9:16, áudio normalizado).
  5. Whisper de novo no vídeo cortado → legenda palavra por palavra exata.
  6. Plano automático de efeitos: zoom punch-in a cada 2–4s, texto animado nas
     palavras-chave, SFX discreto nos zooms de virada e nos textos, e marcas de
     B-roll (~3s) nas menções de produto.

Uso direto (teste):  python3 ferramentas/editar.py <bruto.mp4> <pasta_saida> --formato 9:16
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

from comum import (ASSETS, FORMATOS, FPS, diga, duracao, extrair_wav16k, ffmpeg, gravar_json,
                   hash_arquivo, hash_dados, ler_json, ler_wav_float, marca, rodar)

VERSAO_EDITOR = "1.0"
_MODELO = None


# ---------------------------------------------------------------- Whisper
def modelo_whisper(nome: str):
    global _MODELO
    if _MODELO is None:
        from faster_whisper import WhisperModel
        _MODELO = WhisperModel(nome, device="cpu", compute_type="int8")
    return _MODELO


def _palavras(audio, offset: float = 0.0, idioma: str = "pt") -> list[dict]:
    cfg = marca().get("whisper", {})
    segs, _ = modelo_whisper(cfg.get("modelo", "small")).transcribe(
        audio, language=idioma, word_timestamps=True, vad_filter=False,
        initial_prompt=cfg.get("prompt_inicial"), condition_on_previous_text=False)
    correcoes = cfg.get("correcoes", {})
    palavras = []
    for s in segs:
        for w in s.words or []:
            texto = w.word.strip()
            if not texto:
                continue
            for errado, certo in correcoes.items():
                texto = re.sub(rf"\b{re.escape(errado)}\b", certo, texto)
            palavras.append({"w": texto, "ini": round(w.start + offset, 3), "fim": round(w.end + offset, 3)})
    return palavras


def _audio(video: Path, trabalho: Path):
    wav = extrair_wav16k(video, trabalho / "_audio16k.wav")
    audio = ler_wav_float(wav)
    wav.unlink(missing_ok=True)
    return audio


def transcrever(video: Path, trabalho: Path, idioma: str = "pt") -> list[dict]:
    """Lista de palavras [{w, ini, fim}] do arquivo inteiro (correções da marca aplicadas)."""
    return _palavras(_audio(video, trabalho), 0.0, idioma)


def trechos_de_fala(sil: list[tuple[float, float]], total: float) -> list[tuple[float, float]]:
    fala, t = [], 0.0
    for s0, s1 in sil:
        if s0 - t > 0.2:
            fala.append((t, s0))
        t = max(t, s1)
    if total - t > 0.2:
        fala.append((t, total))
    return fala


def transcrever_por_trecho(video: Path, trabalho: Path, sil, total: float) -> list[list[dict]]:
    """Transcreve cada trecho de fala (entre silêncios) SEPARADAMENTE.
    Assim o Whisper não 'funde' um take errado com a repetição dele."""
    audio = _audio(video, trabalho)
    sr = 16000
    grupos = []
    for a, b in trechos_de_fala(sil, total):
        pedaco = audio[int(max(0, a - 0.05) * sr): int(min(total, b + 0.05) * sr)]
        ps = _palavras(pedaco, max(0, a - 0.05))
        if ps:
            grupos.append(ps)
    return grupos


def normalizar(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9$ ]", "", t).strip()


# ---------------------------------------------------------------- Corte
def silencios(video: Path, limiar_db: float = -35, minimo: float = 0.35) -> list[tuple[float, float]]:
    r = rodar(["ffmpeg", "-hide_banner", "-i", str(video), "-af",
               f"silencedetect=noise={limiar_db}dB:d={minimo}", "-f", "null", "-"])
    ini, lista = None, []
    for linha in r.stderr.splitlines():
        if "silence_start" in linha:
            ini = float(linha.split("silence_start:")[1].split()[0])
        elif "silence_end" in linha and ini is not None:
            fim = float(linha.split("silence_end:")[1].split()[0])
            lista.append((max(0.0, ini), fim))
            ini = None
    if ini is not None:
        lista.append((ini, 1e9))
    return lista


def frases(palavras: list[dict], pausa: float = 0.5) -> list[list[dict]]:
    grupos, atual = [], []
    for p in palavras:
        if atual and (p["ini"] - atual[-1]["fim"] > pausa or re.search(r"[.!?]$", atual[-1]["w"])):
            grupos.append(atual)
            atual = []
        atual.append(p)
    if atual:
        grupos.append(atual)
    return grupos


def remover_erros(grupos: list[list[dict]]) -> tuple[list[list[dict]], list[str]]:
    """Tira frases marcadas com 'corta' e takes repetidos (fica o último)."""
    removidas, saida = [], []
    for i, g in enumerate(grupos):
        texto = " ".join(p["w"] for p in g)
        norm = [normalizar(p["w"]) for p in g]
        if "corta" in norm:
            removidas.append(f"sinal 'corta': “{texto}”")
            continue
        prox = grupos[i + 1] if i + 1 < len(grupos) else None
        if prox:
            nprox = [normalizar(p["w"]) for p in prox]
            k = 3 if len(norm) >= 3 else 2
            if len(norm) >= 2 and norm[:k] == nprox[:k] and len(norm) <= len(nprox) + 1:
                removidas.append(f"take repetido: “{texto}”")
                continue
        saida.append(g)
    return saida, removidas


def trechos_para_manter(grupos, sil, total, pausa_max=0.5, folga_ini=0.10, folga_fim=0.16):
    trechos = []
    for g in grupos:
        # divide a frase onde houver pausa longa entre palavras
        atual = [g[0]]
        for p in g[1:]:
            if p["ini"] - atual[-1]["fim"] > pausa_max:
                trechos.append((atual[0]["ini"], atual[-1]["fim"]))
                atual = []
            atual.append(p)
        trechos.append((atual[0]["ini"], atual[-1]["fim"]))
    ajustados = []
    for a, b in trechos:
        a, b = a - folga_ini, b + folga_fim
        for s0, s1 in sil:  # aperta as bordas que caíram dentro de silêncio
            if s0 <= a < s1:
                a = max(a, s1 - folga_ini)
            if s0 < b <= s1:
                b = min(b, s0 + folga_fim)
        a, b = max(0.0, a), min(total, b)
        if b - a > 0.15:
            ajustados.append([a, b])
    ajustados.sort()
    juntos = []
    for a, b in ajustados:
        if juntos and a - juntos[-1][1] < 0.12:
            juntos[-1][1] = max(juntos[-1][1], b)
        else:
            juntos.append([a, b])
    return [(round(a, 3), round(b, 3)) for a, b in juntos]


def filtro_formato(formato: str) -> str:
    f = FORMATOS[formato]
    w, h = f["largura"], f["altura"]
    return (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
            f"fps={FPS},setsar=1,format=yuv420p")


def cortar(bruto: Path, trechos, saida: Path, formato: str) -> None:
    partes, rotulos = [], []
    for i, (a, b) in enumerate(trechos):
        d = b - a
        fade = min(0.012, d / 4)
        partes.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];")
        partes.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,"
                      f"afade=t=in:d={fade},afade=t=out:st={d - fade:.3f}:d={fade}[a{i}];")
        rotulos.append(f"[v{i}][a{i}]")
    grafo = "".join(partes) + "".join(rotulos) + f"concat=n={len(trechos)}:v=1:a=1[vc][ac];"
    grafo += f"[vc]{filtro_formato(formato)}[vo];[ac]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[ao]"
    script = saida.with_suffix(".filtro.txt")
    script.write_text(grafo)
    ffmpeg("-i", str(bruto), "-filter_complex_script", str(script), "-map", "[vo]", "-map", "[ao]",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
           "-ac", "2", "-movflags", "+faststart", str(saida))
    script.unlink(missing_ok=True)


# ---------------------------------------------------------------- Efeitos
def indice_sfx() -> dict:
    return ler_json(ASSETS / "sfx" / "index.json", {"categorias": {}})


def escolher_sfx(categoria: str, n: int) -> str | None:
    opcoes = indice_sfx().get("categorias", {}).get(categoria, [])
    return opcoes[n % len(opcoes)] if opcoes else None


def termos_broll() -> dict[str, str]:
    """termo normalizado → texto de exibição. Menções de produto/mecanismo."""
    return {
        "kit": "Kit Empresa Completa", "mentoria": "Mentoria 1:1", "curso": "O Curso",
        "llc": "LLC", "google": "Google", "site": "Site", "website": "Website",
        "dashboard": "Dashboard", "jobber": "Jobber", "plataforma": "A Plataforma",
        "orcamento": "Orçamento", "orcamentos": "Orçamentos", "estimate": "Estimate",
        "invoice": "Invoice", "empresa": "Empresa de verdade",
    }


def planejar_efeitos(palavras: list[dict], total: float, eh_inicio_de_bloco: bool = True,
                     com_broll: bool = True, virada: dict | None = None) -> dict:
    m = marca()
    destaque = {normalizar(x) for x in m.get("palavras_destaque", [])}
    zooms, textos, sfx, brolls = [], [], [], []
    n_sfx = 0

    # zoom punch-in: no início de cada frase e, se a frase for longa, a cada ~3s
    grupos = frases(palavras, pausa=0.35)
    nivel = 0
    ultimo_zoom = -10.0
    for gi, g in enumerate(grupos):
        alvo_tempos = [g[0]["ini"]]
        t = g[0]["ini"] + 3.0
        while t < g[-1]["fim"] - 1.0:
            # encaixa na palavra mais próxima
            alvo_tempos.append(min(g, key=lambda p: abs(p["ini"] - t))["ini"])
            t += 3.0
        for at in alvo_tempos:
            if eh_inicio_de_bloco and at < 1.0:
                continue
            if at - ultimo_zoom < 2.0:
                continue
            nivel = (nivel + 1) % 3
            zooms.append({"t": round(max(0, at - 0.03), 3), "escala": [1.0, 1.12, 1.22][nivel]})
            ultimo_zoom = at
    if eh_inicio_de_bloco:
        zooms.insert(0, {"t": 0.0, "escala": 1.0})
        arq = escolher_sfx("whoosh", n_sfx)
        if arq:
            sfx.append({"t": 0.0, "arquivo": arq, "volume": 0.35})
            n_sfx += 1

    # texto animado + destaque na legenda
    ultimo_texto = -10.0
    for p in palavras:
        nw = normalizar(p["w"])
        eh_num = bool(re.search(r"\d", p["w"])) or nw in {"us", "us$"}
        if nw in destaque or eh_num:
            p["destaque"] = True
            if p["ini"] - ultimo_texto >= 3.5 and p["ini"] > 0.8 and p["ini"] < total - 1.2:
                txt = re.sub(r"[,.;:!?]+$", "", p["w"])
                textos.append({"t": round(p["ini"], 3), "dur": 1.4, "texto": txt})
                arq = escolher_sfx("pop", n_sfx)
                if arq:
                    sfx.append({"t": round(p["ini"], 3), "arquivo": arq, "volume": 0.28})
                    n_sfx += 1
                ultimo_texto = p["ini"]

    # B-roll ~3s em menção de produto (no máx. 1 a cada 8s, nunca no 1º segundo e meio)
    if com_broll and virada and total > 6:
        # B-roll de virada de bloco (~2.5s logo na entrada do bloco)
        brolls.append({"t": 0.0, "dur": 2.5, "termo": virada["termo"], "legenda": virada.get("legenda"),
                       "chave": virada.get("chave", normalizar(virada["termo"])), "fonte": "grafico"})
    if com_broll:
        termos = termos_broll()
        ultimo = 2.5 - 8 if virada else -10.0
        for p in palavras:
            nw = normalizar(p["w"])
            if nw in termos and p["ini"] - ultimo >= 8 and p["ini"] > 1.5 and p["ini"] + 3.0 < total:
                brolls.append({"t": round(p["ini"], 3), "dur": 3.0, "termo": termos[nw], "chave": nw, "fonte": "grafico"})
                arq = escolher_sfx("whoosh", n_sfx)
                if arq:
                    sfx.append({"t": round(max(0, p["ini"] - 0.15), 3), "arquivo": arq, "volume": 0.25})
                    n_sfx += 1
                ultimo = p["ini"]
        # B-roll não pode coincidir com texto animado
        textos = [x for x in textos if not any(b["t"] - 0.2 <= x["t"] <= b["t"] + b["dur"] for b in brolls)]
    return {"zooms": zooms, "textos": textos, "sfx": sfx, "brolls": brolls}


# ---------------------------------------------------------------- Principal
def editar(bruto: Path, pasta: Path, formato: str, com_broll: bool = True, forcar: bool = False,
           virada: dict | None = None) -> dict:
    """Edita um bruto. Reaproveita o resultado se nada mudou (bruto, marca, formato)."""
    pasta.mkdir(parents=True, exist_ok=True)
    chave = hash_dados({"bruto": hash_arquivo(bruto), "formato": formato, "marca": marca(),
                        "sfx": indice_sfx(), "versao": VERSAO_EDITOR, "broll": com_broll,
                        "virada": virada})
    rel = pasta / "edicao.json"
    anterior = ler_json(rel, {})
    if not forcar and anterior.get("chave") == chave and (pasta / "cortado.mp4").exists():
        anterior["reaproveitado"] = True
        return anterior

    total = duracao(bruto)
    diga(f"   • transcrevendo {bruto.name} ({total:.1f}s)…")
    sil = silencios(bruto)
    grupos_fala = transcrever_por_trecho(bruto, pasta, sil, total)
    if not grupos_fala:
        raise RuntimeError(f"Não ouvi fala em {bruto.name}. Confere o áudio da gravação.")
    # dentro de cada trecho, ainda separa frases por pontuação/pausa
    grupos_iniciais = [f for g in grupos_fala for f in frases(g)]
    grupos, removidas = remover_erros(grupos_iniciais)
    trechos = trechos_para_manter(grupos, sil, total)
    diga(f"   • cortando silêncios/erros: {len(trechos)} trechos mantidos, {len(removidas)} erro(s) removido(s)")
    cortado = pasta / "cortado.mp4"
    cortar(bruto, trechos, cortado, formato)
    novo_total = duracao(cortado)
    diga("   • legenda palavra por palavra (Whisper no vídeo cortado)…")
    palavras = transcrever(cortado, pasta)
    efeitos = planejar_efeitos(palavras, novo_total, com_broll=com_broll, virada=virada)
    resultado = {
        "chave": chave,
        "bruto": str(bruto),
        "duracao_bruto": round(total, 2),
        "duracao_cortado": round(novo_total, 2),
        "trechos": trechos,
        "erros_removidos": removidas,
        "texto": " ".join(p["w"] for p in palavras),
        "reaproveitado": False,
    }
    gravar_json(pasta / "legenda.json", palavras)
    gravar_json(pasta / "efeitos.json", efeitos)
    gravar_json(rel, resultado)
    return resultado


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("bruto", type=Path)
    ap.add_argument("saida", type=Path)
    ap.add_argument("--formato", default="9:16", choices=list(FORMATOS))
    a = ap.parse_args()
    r = editar(a.bruto, a.saida, a.formato)
    print(json.dumps({k: v for k, v in r.items() if k != "texto"}, ensure_ascii=False, indent=2))
