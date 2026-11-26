"""Testes de aceite da Máquina de VSL (seção 9 do briefing).

  python3 testes/aceite.py            # roda os 4 testes e imprime o relatório em português
  python3 testes/aceite.py --pular-render   # só confere o que já foi produzido (rápido)

Pré-requisitos (o próprio script prepara se faltar):
  - bruto da gravação-guia em entrada/teste-guia/   (testes/preparar_brutos.py guia)
  - takes do curso em entrada/teste-curso-97/        (testes/preparar_brutos.py curso)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FERR = RAIZ / "ferramentas"
sys.path.insert(0, str(FERR))

SLUG = "teste-curso-97"
PY = sys.executable
AMB = {**os.environ, "MAQUINA_BLOQUEAR_APIS": "1"}   # qualquer tentativa de API paga = erro fatal
resultados: list[tuple[str, bool, str]] = []


def rodar(*args, ok_codigos=(0,)) -> str:
    r = subprocess.run([PY, *args], cwd=FERR, capture_output=True, text=True, env=AMB)
    saida = r.stdout + r.stderr
    if r.returncode not in ok_codigos:
        raise RuntimeError(f"{' '.join(args)} falhou ({r.returncode}):\n{saida[-3000:]}")
    return saida


def registrar(nome: str, ok: bool, detalhe: str) -> None:
    resultados.append((nome, ok, detalhe))
    print(f"{'✅' if ok else '❌'} {nome}: {detalhe}", flush=True)


def ler(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


# ------------------------------------------------------------------ 1
def teste1(pular: bool) -> None:
    print("\n— Teste 1: /comecar —")
    amb = subprocess.run([PY, "ambiente.py"], cwd=FERR, capture_output=True, text=True)
    registrar("1a. Ambiente OK", amb.returncode == 0, "Node, FFmpeg, Python, Whisper+modelo, Remotion+navegador, SFX")
    marca = ler(RAIZ / "config" / "marca.json") or {}
    registrar("1b. Marca salva", bool(marca.get("cores") and marca.get("legenda") and marca.get("marca")),
              f"config/marca.json ({marca.get('marca')}); entrevista confirmada: {'sim' if marca.get('confirmado') else 'NÃO — pendente com o Rafael'}")
    if not pular:
        if not list((RAIZ / "entrada" / "teste-guia").glob("*.mp4")):
            subprocess.run([PY, str(RAIZ / "testes" / "preparar_brutos.py"), "guia"], check=True)
        shutil.rmtree(RAIZ / "projetos" / "_teste-guia", ignore_errors=True)
        rodar("teste_guia.py", ok_codigos=(0, 1))
    r = ler(RAIZ / "projetos" / "_teste-guia" / "resultado.json")
    if not r:
        registrar("1c. Vídeo-teste de 20s", False, "não encontrado")
        return
    c = r["checks"]
    from comum import duracao
    d = duracao(Path(r["final"]))
    ok = c["corte_de_silencio"] and c["legenda_palavra_por_palavra"] and c["zoom"] and c["sfx"] and 15 <= d <= 26
    registrar("1c. Vídeo-teste de 20s (Motor A)", ok,
              f"{r['duracao_bruto']:.1f}s bruto → {d:.1f}s editado; corte de silêncio {'✓' if c['corte_de_silencio'] else '✗'}, "
              f"{c['erros_removidos']} take errado removido, legenda palavra por palavra {'✓' if c['legenda_palavra_por_palavra'] else '✗'}, "
              f"zoom {'✓' if c['zoom'] else '✗'}, SFX {'✓' if c['sfx'] else '✗'}")


# ------------------------------------------------------------------ 2
def teste2(pular: bool) -> None:
    print("\n— Teste 2: /vsl com o curso de US$ 97 —")
    import roteiro as R
    pasta = RAIZ / "projetos" / SLUG
    if not pular:
        if len(list((RAIZ / "entrada" / SLUG).glob("*.mp4"))) < 10:
            subprocess.run([PY, str(RAIZ / "testes" / "preparar_brutos.py"), "curso"], check=True)
        shutil.rmtree(pasta, ignore_errors=True)
        rodar("vsl.py", "novo", SLUG, "--produto", "curso", "--formato", "9:16")
        rodar("vsl.py", "rascunho", SLUG)
        bloqueio = rodar("vsl.py", "produzir", SLUG, ok_codigos=(1,))
        registrar("2a. Sem aprovação não produz", "não foi aprovado" in bloqueio, "produzir antes do 'aprovado' foi bloqueado")
        rodar("vsl.py", "aprovar", SLUG, "--frase", "aprovado")
        custo = rodar("vsl.py", "custo", SLUG)
        registrar("2b. Custo mostrado antes de gerar", "TOTAL: US$ 0.00" in custo and not (pasta / "cenas" / "01-hook").exists(),
                  "estimativa US$ 0,00 (Motor A) exibida antes de qualquer cena existir")
        rodar("vsl.py", "produzir", SLUG)
        rodar("vsl.py", "produzir", SLUG, "--final")
    bl = ler(pasta / "roteiro.json") or []
    ids = [b["id"] for b in bl]
    estrutura_ok = ids == R.ORDEM and ids.index("ecossistema") == ids.index("oferta") + 1
    registrar("2c. Roteiro na estrutura do método", estrutura_ok and not R.checar_copy(bl),
              f"{len(ids)} blocos: {' → '.join(ids)}; ecossistema logo após a oferta; travas de copy sem alerta")
    apr = ler(pasta / "aprovacao.json") or {}
    registrar("2d. Aprovação registrada", bool(apr.get("aprovado")), f"frase: “{apr.get('frase')}” em {apr.get('quando')}")
    prev = sorted((pasta / "preview").glob("*.mp4"))
    fin = sorted((pasta / "final").glob("curso-vsl-v*.mp4"))
    from comum import duracao
    registrar("2e. Preview renderizado", bool(prev), ", ".join(f"{p.name} ({duracao(p):.0f}s)" for p in prev) or "nenhum")
    registrar("2f. Final em final/", bool(fin), ", ".join(f"{p.name} ({duracao(p):.0f}s)" for p in fin) or "nenhum")


# ------------------------------------------------------------------ 3
def teste3() -> None:
    print("\n— Teste 3: muda o preço → só a cena da oferta —")
    prod_arq = RAIZ / "config" / "produtos.json"
    original = prod_arq.read_text(encoding="utf-8")
    pasta = RAIZ / "projetos" / SLUG
    try:
        d = json.loads(original)
        d["curso"]["preco_por"] = 87
        prod_arq.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        saida = rodar("vsl.py", "produzir", SLUG, "--final")
        u = ler(pasta / "ultima_producao.json")
        so_oferta = u["renderizadas"] == ["oferta"]
        aviso = any("oferta" in a and "US$ 87" in a for a in u["avisos"])
        registrar("3a. Só a cena da oferta foi refeita", so_oferta,
                  f"refeitas: {u['renderizadas']}; reaproveitadas: {len(u['reaproveitadas'])} cenas")
        registrar("3b. Aviso de take com preço antigo", aviso,
                  "a máquina avisou que a FALA da oferta não diz US$ 87 (regravar só esse take)")
        props = ler(sorted((pasta / "cenas").glob("*-oferta"))[0] / "render-final.props.json")
        registrar("3c. Tela da oferta com o preço novo", props["tela"]["porTexto"] == "por US$ 87", props["tela"]["porTexto"])
        proj = ler(pasta / "projeto.json")
        registrar("3d. Nova versão do final", proj["versao"] >= 2, f"final/{proj['historico'][-1]['arquivo'].split('/')[-1]}")
    finally:
        prod_arq.write_text(original, encoding="utf-8")


# ------------------------------------------------------------------ 4
def teste4() -> None:
    print("\n— Teste 4: Motor B desligado → nenhuma chamada a ElevenLabs/fal.ai —")
    import apis
    pasta = RAIZ / "projetos" / SLUG
    proj = ler(pasta / "projeto.json")
    log = pasta / "chamadas_api.log"
    linhas = log.read_text().splitlines() if log.exists() else []
    registrar("4a. Produções sem nenhuma tentativa de API", proj["motor"] == "A" and not proj["motor_b"]["ligado"] and not linhas,
              f"motor {proj['motor']}, motor_b ligado={proj['motor_b']['ligado']}; rodadas com MAQUINA_BLOQUEAR_APIS=1; log de API: {len(linhas)} linhas")
    # portão: mesmo chamando direto, sem o comando do Rafael é bloqueado (sem tocar a rede)
    os.environ.pop("MAQUINA_BLOQUEAR_APIS", None)
    bloqueios = []
    for servico in ("elevenlabs", "fal_avatar", "fal_broll"):
        try:
            apis.chamar(SLUG, servico, "https://exemplo.invalido/nao-deve-sair")
            bloqueios.append(f"{servico}: LIBERADO (erro!)")
        except apis.APIBloqueada as e:
            bloqueios.append(f"{servico}: bloqueado ({e})")
    ok = all("bloqueado" in b for b in bloqueios)
    registrar("4b. Portão bloqueia chamada direta", ok, "; ".join(bloqueios))
    log.unlink(missing_ok=True)
    # varredura do código: só apis.py abre conexão
    fora = []
    for arq in FERR.glob("*.py"):
        txt = arq.read_text(encoding="utf-8")
        if arq.name != "apis.py" and re.search(r"urlopen|requests\.|http\.client|urllib\.request", txt):
            fora.append(arq.name)
    registrar("4c. Só apis.py fala com a internet", not fora, "nenhum outro módulo abre conexão" if not fora else f"encontrado em: {fora}")


if __name__ == "__main__":
    pular = "--pular-render" in sys.argv
    teste1(pular)
    teste2(pular)
    if not pular:
        teste3()
    teste4()
    ok = sum(1 for _, o, _ in resultados if o)
    print(f"\nResultado: {ok}/{len(resultados)} verificações OK")
    (RAIZ / "testes" / "relatorio-aceite.json").write_text(
        json.dumps([{"teste": n, "ok": o, "detalhe": d} for n, o, d in resultados], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    sys.exit(0 if ok == len(resultados) else 1)
