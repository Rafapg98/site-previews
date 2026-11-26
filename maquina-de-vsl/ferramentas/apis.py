"""PORTÃO ÚNICO para APIs pagas (ElevenLabs, fal.ai, HeyGen).

Toda chamada externa paga da máquina passa por `chamar()`. As regras do dono são
aplicadas AQUI, não em cada script:

  * ElevenLabs e avatar (fal.ai/HeyGen) só rodam se o projeto estiver no Motor B
    E tiver a autorização explícita do Rafael gravada em projeto.json
    (campo motor_b.autorizacao, com a frase dele: "usa o motor B nesta VSL").
  * B-roll por IA (fal.ai) só roda se o projeto ligar broll_ia.ligado = true com
    autorização explícita — e o custo tem que estar aceito.
  * Sem custo aceito (custo.json → aceito: true), nada pago roda.
  * Cada tentativa (liberada ou bloqueada) vai para projetos/<slug>/chamadas_api.log.

Variável de ambiente MAQUINA_BLOQUEAR_APIS=1 transforma qualquer tentativa em erro
fatal (usada no teste de aceite 4).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

from comum import PROJETOS, carregar_chaves, ler_json

SERVICOS = {
    "elevenlabs": {"host": "api.elevenlabs.io", "exige": "motor_b"},
    "fal_avatar": {"host": "queue.fal.run", "exige": "motor_b"},
    "heygen": {"host": "api.heygen.com", "exige": "motor_b"},
    "fal_broll": {"host": "queue.fal.run", "exige": "broll_ia"},
}


class APIBloqueada(RuntimeError):
    pass


def _log(slug: str, linha: str) -> None:
    arq = PROJETOS / slug / "chamadas_api.log"
    arq.parent.mkdir(parents=True, exist_ok=True)
    with open(arq, "a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now().isoformat(timespec='seconds')} {linha}\n")


def liberado(slug: str, servico: str) -> tuple[bool, str]:
    proj = ler_json(PROJETOS / slug / "projeto.json", {})
    custo = ler_json(PROJETOS / slug / "custo.json", {})
    regra = SERVICOS[servico]["exige"]
    if regra == "motor_b":
        mb = proj.get("motor_b", {})
        if proj.get("motor") != "B" or not mb.get("ligado") or not mb.get("autorizacao"):
            return False, "Motor B desligado neste projeto (precisa do comando explícito do Rafael)."
    if regra == "broll_ia":
        bi = proj.get("broll_ia", {})
        if not bi.get("ligado") or not bi.get("autorizacao"):
            return False, "B-roll por IA desligado neste projeto."
    if not custo.get("aceito"):
        return False, "Custo de API ainda não foi mostrado e aceito."
    return True, "ok"


def chamar(slug: str, servico: str, url: str, corpo: dict | None = None,
           cabecalhos: dict | None = None, metodo: str = "POST", binario: bool = False):
    """Única função da máquina que fala com API paga."""
    if os.environ.get("MAQUINA_BLOQUEAR_APIS") == "1":
        _log(slug, f"BLOQUEADA(teste) {servico} {url}")
        raise APIBloqueada(f"Tentativa de chamar {servico} com APIs bloqueadas (teste).")
    ok, motivo = liberado(slug, servico)
    if not ok:
        _log(slug, f"BLOQUEADA {servico}: {motivo}")
        raise APIBloqueada(motivo)
    _log(slug, f"CHAMADA {servico} {metodo} {url}")
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(url, data=dados, method=metodo,
                                 headers={"Content-Type": "application/json", **(cabecalhos or {})})
    with urllib.request.urlopen(req, timeout=600) as r:
        conteudo = r.read()
    return conteudo if binario else json.loads(conteudo or b"{}")


def chave(nome: str) -> str:
    v = carregar_chaves().get(nome) or os.environ.get(nome)
    if not v:
        raise APIBloqueada(f"Chave {nome} não encontrada em config/chaves.env.")
    return v


def baixar(url: str, destino: Path) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=600) as r, open(destino, "wb") as f:
        f.write(r.read())
    return destino
