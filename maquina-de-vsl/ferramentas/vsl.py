"""Orquestrador da Máquina de VSL — é o que o comando /vsl usa por baixo.

  python3 ferramentas/vsl.py novo <slug> --produto curso --formato 16:9
  python3 ferramentas/vsl.py rascunho <slug>              # roteiro na estrutura do método
  python3 ferramentas/vsl.py mostrar <slug>               # gera/mostra roteiro.md
  python3 ferramentas/vsl.py aprovar <slug> --frase "aprovado"
  python3 ferramentas/vsl.py custo <slug> [--aceitar]
  python3 ferramentas/vsl.py takes <slug>                 # quais gravações faltam
  python3 ferramentas/vsl.py take <slug> <bloco> <arquivo>   # troca o take de um bloco
  python3 ferramentas/vsl.py produzir <slug> [--final] [--escala 0.5] [--legenda en]
  python3 ferramentas/vsl.py frases <slug>                # exporta frases p/ tradução EN
  python3 ferramentas/vsl.py motor-b <slug> --autorizacao "usa o motor B nesta VSL"
  python3 ferramentas/vsl.py status <slug>
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import time
from pathlib import Path

import roteiro as R
from comum import (ASSETS, ENTRADA, FORMATOS, FPS, PROJETOS, diga, erro, gravar_json, hash_arquivo,
                   hash_dados, ler_json, marca, moeda, produtos)

EXT_VIDEO = (".mp4", ".mov", ".m4v", ".MP4", ".MOV")

# B-roll de "virada de bloco" (entra nos ~2.5s iniciais do bloco). "chave" casa com B-roll real
# em assets/broll-real/ (ex.: obra-cozinha.mp4). Um bloco pode trocar isso com "broll_virada" no roteiro.
VIRADAS = {
    "historia": {"termo": "Eu vivo da obra", "legenda": "Não de curso.", "chave": "obra"},
}


# ------------------------------------------------------------------ projeto
def pasta(slug: str) -> Path:
    return PROJETOS / slug


def carregar(slug: str) -> dict:
    proj = ler_json(pasta(slug) / "projeto.json")
    if not proj:
        erro(f"Projeto '{slug}' não existe. Crie com: vsl.py novo {slug} --produto curso")
    return proj


def salvar(proj: dict) -> None:
    gravar_json(pasta(proj["slug"]) / "projeto.json", proj)


def blocos(slug: str) -> list[dict]:
    return ler_json(pasta(slug) / "roteiro.json", [])


def hash_roteiro(bl: list[dict]) -> str:
    return hash_dados([{k: b.get(k) for k in ("id", "fala", "modo", "take", "motor_b")} for b in bl])


def agora() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def cmd_novo(a) -> None:
    if a.produto not in ("curso", "kit", "mentoria"):
        erro("Produto deve ser: curso, kit ou mentoria (ver config/produtos.json).")
    p = pasta(a.slug)
    if (p / "projeto.json").exists():
        erro(f"Já existe um projeto '{a.slug}'.")
    for sub in ("cenas", "audio", "broll", "preview", "final"):
        (p / sub).mkdir(parents=True, exist_ok=True)
    (ENTRADA / a.slug).mkdir(parents=True, exist_ok=True)
    proj = {"slug": a.slug, "produto": a.produto, "formato": a.formato, "motor": "A",
            "motor_b": {"ligado": False, "autorizacao": None},
            "broll_ia": {"ligado": False, "autorizacao": None},
            "versao": 0, "takes": {}, "historico": [], "criado_em": agora()}
    salvar(proj)
    diga(f"Projeto '{a.slug}' criado: {a.produto}, formato {a.formato}, Motor A (gravação real).")
    diga(f"Gravações deste projeto vão em: entrada/{a.slug}/")


def cmd_rascunho(a) -> None:
    proj = carregar(a.slug)
    arq = pasta(a.slug) / "roteiro.json"
    if arq.exists() and not a.sobrescrever:
        erro("Já existe roteiro. Use --sobrescrever para trocar pelo rascunho padrão.")
    gravar_json(arq, R.rascunho(proj["produto"]))
    cmd_mostrar(a)


def cmd_mostrar(a) -> None:
    proj = carregar(a.slug)
    bl = blocos(a.slug)
    apr = ler_json(pasta(a.slug) / "aprovacao.json")
    if apr and apr.get("hash") != hash_roteiro(bl):
        apr = None
    md = R.para_markdown(proj, bl, apr)
    (pasta(a.slug) / "roteiro.md").write_text(md + "\n", encoding="utf-8")
    diga(md)
    probs = R.checar_copy(bl)
    if probs:
        diga("\n⚠️  Travas de copy (precisa corrigir antes de aprovar):")
        for x in probs:
            diga("   - " + x)


def cmd_aprovar(a) -> None:
    bl = blocos(a.slug)
    if not bl:
        erro("Não há roteiro para aprovar.")
    probs = R.checar_copy(bl)
    if probs:
        erro("Não dá pra aprovar: o roteiro quebra uma regra.\n" + "\n".join("   - " + x for x in probs))
    if not a.frase or not a.frase.strip():
        erro("A aprovação precisa da palavra do Rafael (--frase).")
    gravar_json(pasta(a.slug) / "aprovacao.json",
                {"aprovado": True, "frase": a.frase, "quando": agora(), "hash": hash_roteiro(bl)})
    a.sobrescrever = False
    cmd_mostrar(a)
    diga("\n✅ Roteiro aprovado. Próximo passo: custo.")


# ------------------------------------------------------------------ custo
def estimar_custo(proj: dict, bl: list[dict]) -> dict:
    tabela = ler_json(Path(__file__).resolve().parent.parent / "config" / "custos.json", {})
    itens = []
    itens.append({"item": "Edição local (FFmpeg + Whisper + Remotion)", "usd": 0.0})
    if proj["motor"] == "B" and proj["motor_b"].get("ligado"):
        for b in bl:
            if b.get("motor_b") or not achar_take(proj, b):
                chars = len(R.renderizar(b["fala"]))
                seg = max(3, chars / 15)
                voz = chars / 1000 * tabela["elevenlabs"]["usd_por_1000_caracteres"]
                av = seg * tabela["fal_avatar_lipsync"]["usd_por_segundo"]
                itens.append({"item": f"Motor B · {b['id']}: voz ({chars} caracteres)", "usd": round(voz, 2)})
                itens.append({"item": f"Motor B · {b['id']}: avatar (~{seg:.0f}s)", "usd": round(av, 2)})
    if proj["broll_ia"].get("ligado"):
        mencoes = sum(len(re.findall(r"\b(kit|curso|llc|google|site|dashboard|jobber|plataforma)\b", b["fala"], re.I))
                      for b in bl if b["modo"] == "fala")
        clipes = min(mencoes, sum(b["tempo_estimado_s"] for b in bl if b["modo"] == "fala") // 8)
        itens.append({"item": f"B-roll por IA (~{clipes} clipes de 3–5s)",
                      "usd": round(clipes * tabela["fal_broll_ia"]["usd_por_clipe_5s"], 2)})
    total = round(sum(i["usd"] for i in itens), 2)
    base = {"motor": proj["motor"], "motor_b": proj["motor_b"].get("ligado"), "broll_ia": proj["broll_ia"].get("ligado"),
            "itens": itens, "total_usd": total}
    base["hash"] = hash_dados(base)
    return base


def mostrar_custo(c: dict) -> None:
    diga("💵 Custo de API estimado desta VSL (antes de gerar qualquer coisa):")
    for i in c["itens"]:
        diga(f"   - {i['item']}: US$ {i['usd']:.2f}")
    diga(f"   TOTAL: US$ {c['total_usd']:.2f}" + ("  (Motor A: custo de API zero)" if c["total_usd"] == 0 else ""))


def cmd_custo(a) -> None:
    proj = carregar(a.slug)
    c = estimar_custo(proj, blocos(a.slug))
    mostrar_custo(c)
    c["aceito"] = bool(a.aceitar)
    if a.aceitar:
        c["aceito_em"] = agora()
        diga("✅ Custo aceito.")
    gravar_json(pasta(a.slug) / "custo.json", c)


# ------------------------------------------------------------------ takes
def achar_take(proj: dict, b: dict) -> Path | None:
    nome = proj.get("takes", {}).get(b["id"]) or b["take"]
    base = ENTRADA / proj["slug"]
    cand = base / nome
    if cand.suffix and cand.exists():
        return cand
    for ext in EXT_VIDEO:
        c = base / f"{nome}{ext}"
        if c.exists():
            return c
    return None


def cmd_takes(a) -> None:
    proj = carregar(a.slug)
    faltam = 0
    for b in blocos(a.slug):
        t = achar_take(proj, b)
        diga(f"   {'✅' if t else '⬜'} {b['ordem']:02d}. {b['titulo']}: " + (t.name if t else f"falta gravar → entrada/{a.slug}/{b['take']}.mp4"))
        faltam += 0 if t else 1
    diga(f"\n{faltam} take(s) faltando." if faltam else "\nTodos os takes estão na pasta.")


def cmd_take(a) -> None:
    proj = carregar(a.slug)
    if a.bloco not in {b["id"] for b in blocos(a.slug)}:
        erro(f"Bloco '{a.bloco}' não existe no roteiro.")
    proj.setdefault("takes", {})[a.bloco] = a.arquivo
    salvar(proj)
    diga(f"Bloco '{a.bloco}' agora usa o take {a.arquivo}.")


# ------------------------------------------------------------------ telas (a partir do produtos.json)
def montar_tela(bloco_id: str, produto: str) -> dict:
    p = produtos()
    prod = p[produto]
    if bloco_id == "mecanismo":
        if produto == "kit":
            itens = [s["item"] for s in prod["stack"]]
        else:
            itens = ["Abrir a LLC do jeito certo", "Aparecer no Google", "Site que vende",
                     "Dashboard de orçamento e obra", "Caminho até os clientes"]
        return {"tipo": "lista", "titulo": "Empresa de verdade", "itens": itens, "estilo": "check"}
    if bloco_id == "oferta":
        if produto == "mentoria":
            itens = [{"item": prod["nome"], "valorTexto": moeda(prod["preco_por"])}]
            return {"tipo": "oferta", "titulo": "Mentoria 1:1", "itens": itens, "somaTexto": "",
                    "deTexto": "", "porTexto": moeda(prod["preco_por"]),
                    "bonus": [b["item"] for b in prod["bonus"]],
                    "rodape": f"Quem tem o Kit paga {moeda(p['desconto_cruzado']['mentoria_para_quem_tem_kit'])}. Garantia de {p['garantia']['dias']} dias."}
        itens = [{"item": s["item"], "valorTexto": moeda(s["valor"])} for s in prod["stack"]]
        soma = sum(s["valor"] for s in prod["stack"])
        bonus = [b["item"] for b in prod.get("bonus", [])]
        if produto == "curso":
            rodape = (f"Inclui {prod['inclusos_sem_valor'][0].split(' —')[0]}. Depois do 1º mês, "
                      f"{prod['assinatura']['depois_texto']}. Garantia de {p['garantia']['dias']} dias.")
        else:
            rodape = "O Kit é o SETUP: não inclui operar Google Ads nem o selo do Local Services (aprovação do Google)."
        return {"tipo": "oferta", "titulo": "O que você leva hoje", "itens": itens,
                "somaTexto": f"Total: {moeda(soma)}", "deTexto": f"De {moeda(prod['preco_de'])}",
                "porTexto": f"por {moeda(prod['preco_por'])}", "bonus": bonus, "rodape": rodape}
    if bloco_id == "ecossistema":
        kit = p["kit"]
        return {"tipo": "ecossistema", "titulo": "E dentro da plataforma tem mais",
                "cartoes": [
                    {"titulo": kit["nome"], "texto": "A sua empresa montada com a gente do lado.", "selo": f"Stack de {moeda(kit['preco_de'])}"},
                    {"titulo": "Contractors ↔ Subs", "texto": "O ecossistema de trabalho entre quem tem obra e quem executa.", "selo": "Ecossistema"},
                ],
                "rodape": "Quando você entrar, explora."}
    if bloco_id == "prova":
        pv = p["provas"]
        prints = sorted(str(x.relative_to(ASSETS.parent)) for x in (ASSETS / "provas").glob("*") if x.suffix.lower() in (".png", ".jpg", ".jpeg"))
        nomes = [d["nome"] + (f" ({d['cidade']})" if d.get("cidade") else "") for d in pv["depoimentos"]]
        return {"tipo": "prova", "titulo": "Não é teoria",
                "numeros": [{"valor": f"{pv['google']['nota']} ★", "texto": f"Google · {pv['google']['avaliacoes']} avaliações"},
                            {"valor": pv["obras_vendidas_2026"]["valor"], "texto": "em obras vendidas em 2026"},
                            {"valor": pv["orcamentos_fechados_2026"]["valor"], "texto": "orçamentos fechados em 2026"}],
                "nomes": nomes, "prints": prints}
    if bloco_id == "payback":
        pb = p["payback"]
        linhas = [{"rotulo": "Ticket médio por obra", "valor": moeda(pb["ticket_medio"])},
                  {"rotulo": "Lucro médio por obra", "valor": "≈ " + moeda(pb["lucro_medio_por_obra"])}]
        if produto == "kit":
            linhas.append({"rotulo": "Uma obra paga o Kit", "valor": pb["kit_vezes"]})
        if produto == "mentoria":
            linhas.append({"rotulo": "Uma obra paga a Mentoria", "valor": pb["mentoria_vezes"]})
        return {"tipo": "payback", "titulo": "A conta, com base real", "linhas": linhas, "base": pb["base"],
                "aviso": "Números da empresa do Rafael. Não é promessa de renda."}
    if bloco_id == "garantia":
        g = p["garantia"]
        return {"tipo": "garantia", "dias": g["dias"], "texto": f"{g['percentual']}% · sem perguntas"}
    if bloco_id == "qualificacao":
        return {"tipo": "lista", "titulo": "Não é pra você se…", "estilo": "x",
                "itens": ["Você quer apertar um botão e ver dinheiro cair", "Você ainda não tem nada pra vender",
                          "Você espera resultado sem trabalhar"]}
    if bloco_id == "cta":
        cta = prod["cta"]
        sub = (f"Checkout seguro · Garantia de {p['garantia']['dias']} dias" if cta["tipo"] == "checkout"
               else "A conversa vem antes da venda: aplicação + WhatsApp")
        return {"tipo": "cta", "botao": cta["texto"], "sub": sub}
    return {"tipo": "nenhuma"}


# ------------------------------------------------------------------ produção
def montar_props(proj: dict, b: dict, cena_dir: Path, ed: dict, idioma: str) -> dict:
    """Props com caminhos RELATIVOS (o hash não depende da porta do servidor)."""
    m = marca()
    f = FORMATOS[proj["formato"]]
    palavras = ler_json(cena_dir / "legenda.json", [])
    if idioma == "en":
        palavras = legenda_en(cena_dir, palavras)
    ef = ler_json(cena_dir / "efeitos.json", {})
    modo = b["modo"]
    tela = montar_tela(b["id"], proj["produto"])
    sfx = [{"t": s["t"], "src": s["arquivo"], "volume": s["volume"]} for s in ef.get("sfx", [])]
    if b["id"] == "oferta":
        # ding no momento em que o preço aparece (58% da cena, igual à tela)
        sfx.append({"t": round(0.58 * ed["duracao_cortado"], 2), "src": "assets/sfx/assinatura/ding_preco.wav", "volume": 0.45})
    if modo == "tela":
        sfx = [s for s in sfx if s["t"] < 0.5 or "ding" in s["src"]]  # em tela, só o whoosh de entrada e o ding
    return {
        "largura": f["largura"], "altura": f["altura"], "fps": FPS,
        "duracaoFrames": max(1, round(ed["duracao_cortado"] * FPS)),
        "modo": modo, "video": str(cena_dir / "cortado.mp4"),
        "palavras": palavras,
        "zooms": ef.get("zooms", []) if modo != "tela" else [],
        "textos": ef.get("textos", []) if modo == "fala" else [],
        "sfx": sfx,
        "brolls": ef.get("brolls", []) if modo == "fala" else [],
        "tela": tela, "cores": m["cores"],
        "lowerThird": m.get("lower_third") if b["ordem"] == 1 else None,
        "assinatura": m.get("assinatura", ""),
        "palavrasPorTela": m.get("legenda", {}).get("palavras_por_tela", 3),
        "musica": None,
    }


def legenda_en(cena_dir: Path, palavras_pt: list[dict]) -> list[dict]:
    """Legenda EN palavra por palavra sobre o MESMO vídeo (nunca dublagem).
    Usa cenas/<id>/legenda_en.json: [{ini, fim, en}] por frase (traduzido pelo Claude)."""
    frases = ler_json(cena_dir / "legenda_en.json")
    if not frases:
        raise FileNotFoundError(cena_dir / "legenda_en.json")
    out = []
    for fr in frases:
        ws = fr["en"].split()
        if not ws:
            continue
        passo = (fr["fim"] - fr["ini"]) / len(ws)
        for i, w in enumerate(ws):
            out.append({"w": w, "ini": round(fr["ini"] + i * passo, 3), "fim": round(fr["ini"] + (i + 1) * passo, 3)})
    return out


def para_urls(props: dict, srv) -> dict:
    p = dict(props)
    p["video"] = srv.url(p["video"]) if p.get("video") else None
    p["sfx"] = [{**s, "src": srv.url(ASSETS.parent / s["src"])} for s in p["sfx"]]
    p["brolls"] = [{**x, "src": srv.url(x["src"]) if x.get("src") else None} for x in p["brolls"]]
    tela = dict(p["tela"])
    if tela.get("tipo") == "prova":
        tela["prints"] = [srv.url(ASSETS.parent / x) for x in tela.get("prints", [])]
    p["tela"] = tela
    return p


def checar_portao(proj: dict, bl: list[dict]) -> dict:
    """Roteiro aprovado + custo mostrado (e aceito, se > 0). Senão, para."""
    apr = ler_json(pasta(proj["slug"]) / "aprovacao.json")
    if not apr or not apr.get("aprovado"):
        erro("O roteiro ainda não foi aprovado pelo Rafael. Mostre o roteiro (vsl.py mostrar) e espere o 'aprovado'.")
    if apr.get("hash") != hash_roteiro(bl):
        erro("O roteiro mudou depois da aprovação. Mostre de novo e peça um novo 'aprovado'.")
    probs = R.checar_copy(bl)
    if probs:
        erro("Roteiro quebra regra de copy:\n" + "\n".join(probs))
    c = estimar_custo(proj, bl)
    mostrar_custo(c)
    salvo = ler_json(pasta(proj["slug"]) / "custo.json", {})
    if c["total_usd"] > 0 and not (salvo.get("aceito") and salvo.get("hash") == c["hash"]):
        erro(f"Esta VSL tem custo de API (US$ {c['total_usd']:.2f}). Mostre ao Rafael e, com o OK dele: vsl.py custo {proj['slug']} --aceitar")
    if c["total_usd"] == 0 and not salvo:
        c["aceito"] = True
        c["aceito_em"] = agora()
        gravar_json(pasta(proj["slug"]) / "custo.json", c)
    return c


def avisos_de_fala(proj: dict, b: dict, ed: dict) -> list[str]:
    """Confere se a FALA gravada bate com o produtos.json (ex.: preço mudou e o take ainda diz o antigo)."""
    av = []
    if b["id"] in ("oferta", "cta") and proj["produto"] in ("curso", "kit"):
        preco = produtos()[proj["produto"]]["preco_por"]
        nums = R._numeros(ed.get("texto", ""))
        extenso = {97: "noventa e sete", 997: "novecentos e noventa e sete"}.get(int(preco), "")
        if float(preco) not in nums and (not extenso or extenso not in ed.get("texto", "").lower()):
            av.append(f"O take do bloco '{b['id']}' não fala '{moeda(preco)}'. Se o preço mudou, regrave só esse take "
                      f"(entrada/{proj['slug']}/{b['take']}.mp4) — a tela já mostra o preço novo.")
    return av


def cmd_produzir(a) -> None:
    import editar
    import render

    proj = carregar(a.slug)
    bl = blocos(a.slug)
    checar_portao(proj, bl)

    faltando = [b for b in bl if not achar_take(proj, b)]
    motor_b_ativo = proj["motor"] == "B" and proj["motor_b"].get("ligado") and proj["motor_b"].get("autorizacao")
    if faltando and not motor_b_ativo:
        erro("Faltam gravações (Motor A):\n" + "\n".join(f"   - entrada/{a.slug}/{b['take']}.mp4  ({b['titulo']})" for b in faltando))

    t0 = time.time()
    hash_bundle = render.garantir_bundle()
    composicao = FORMATOS[proj["formato"]]["composicao"]
    escala = 1.0 if a.final else a.escala
    rel = {"renderizadas": [], "reaproveitadas": [], "avisos": [], "erros_removidos": []}
    arquivos, hashes = [], []

    with render.ServidorLocal() as srv:
        for b in bl:
            cena_dir = pasta(a.slug) / "cenas" / f"{b['ordem']:02d}-{b['id']}"
            take = achar_take(proj, b)
            if (b.get("motor_b") or take is None) and motor_b_ativo:
                import motor_b
                take = motor_b.gerar_bruto(proj, b, cena_dir)
            diga(f"▶ {b['ordem']:02d}. {b['titulo']}")
            virada = b.get("broll_virada") or VIRADAS.get(b["id"])
            ed = editar.editar(take, cena_dir, proj["formato"], com_broll=(b["modo"] == "fala"),
                               virada=virada if b["modo"] == "fala" else None)
            if ed.get("erros_removidos") and not ed.get("reaproveitado"):
                rel["erros_removidos"] += [f"{b['id']}: {x}" for x in ed["erros_removidos"]]
            if b["modo"] == "fala":
                import broll_ia  # B-roll real da pasta assets/broll-real; IA só se ligado
                broll_ia.preencher(proj, cena_dir)
            rel["avisos"] += avisos_de_fala(proj, b, ed)
            try:
                props = montar_props(proj, b, cena_dir, ed, a.legenda)
            except FileNotFoundError as e:
                erro(f"Falta a tradução EN deste bloco: {e}. Rode 'vsl.py frases {a.slug}' e preencha o campo 'en'.")
            midias = {"video": hash_arquivo(cena_dir / "cortado.mp4")}
            h = hash_dados({"props": props, "midias": midias, "bundle": hash_bundle, "escala": escala, "comp": composicao})
            sufixo = "" if a.legenda == "pt" else f"-{a.legenda}"
            saida = cena_dir / f"render{sufixo}-{'final' if escala == 1.0 else 'preview'}.mp4"
            cache = ler_json(saida.with_suffix(".hash.json"), {})
            if cache.get("hash") == h and saida.exists():
                rel["reaproveitadas"].append(b["id"])
                diga("   • cena aprovada reaproveitada (nada mudou)")
            else:
                diga(f"   • renderizando cena ({ed['duracao_cortado']:.1f}s)…")
                render.renderizar_cena(para_urls(props, srv), composicao, saida, escala)
                gravar_json(saida.with_suffix(".hash.json"), {"hash": h, "quando": agora()})
                rel["renderizadas"].append(b["id"])
            arquivos.append(saida)
            hashes.append(h)

    musica = render.musica_de_fundo()
    versao_hash = hash_dados(hashes)
    sufixo_idioma = "" if a.legenda == "pt" else f"-{a.legenda.upper()}"
    if a.final:
        ultimo = proj["historico"][-1] if proj["historico"] else None
        if ultimo and ultimo.get("hash") == versao_hash and ultimo.get("idioma", "pt") == a.legenda:
            versao = ultimo["versao"]
        else:
            versao = proj["versao"] + (1 if a.legenda == "pt" or not proj["versao"] else 0)
        destino = pasta(a.slug) / "final" / f"{proj['produto']}-vsl-v{versao}{sufixo_idioma}.mp4"
    else:
        versao = proj["versao"] + 1
        destino = pasta(a.slug) / "preview" / f"{proj['produto']}-preview-v{versao}{sufixo_idioma}.mp4"
    diga("▶ montando o vídeo inteiro…")
    render.juntar_cenas(arquivos, destino, musica)
    from comum import duracao
    dur = duracao(destino)

    if a.final:
        if versao != proj["versao"]:
            proj["versao"] = versao
        proj["historico"].append({"versao": versao, "quando": agora(), "arquivo": str(destino.relative_to(pasta(a.slug))),
                                  "hash": versao_hash, "idioma": a.legenda,
                                  "renderizadas": rel["renderizadas"], "reaproveitadas": rel["reaproveitadas"]})
        salvar(proj)
    gravar_json(pasta(a.slug) / "ultima_producao.json", {**rel, "arquivo": str(destino), "duracao_s": round(dur, 1),
                                                          "tempo_s": round(time.time() - t0), "quando": agora()})
    diga("")
    diga(f"🎬 {'FINAL' if a.final else 'PREVIEW'} pronto: {destino.relative_to(PROJETOS.parent)}  ({dur:.0f}s)")
    diga(f"   Cenas refeitas: {', '.join(rel['renderizadas']) or 'nenhuma'}")
    diga(f"   Cenas reaproveitadas: {', '.join(rel['reaproveitadas']) or 'nenhuma'}")
    for x in rel["erros_removidos"]:
        diga(f"   ✂️  erro removido — {x}")
    for x in rel["avisos"]:
        diga(f"   ⚠️  {x}")
    if not musica:
        diga("   (sem música de fundo: coloque um .mp3 livre de direitos em assets/musica/ se quiser)")
    diga("   Nada foi publicado nem enviado. O arquivo é seu.")


def cmd_frases(a) -> None:
    import editar
    proj = carregar(a.slug)
    for b in blocos(a.slug):
        cena_dir = pasta(a.slug) / "cenas" / f"{b['ordem']:02d}-{b['id']}"
        pal = ler_json(cena_dir / "legenda.json")
        if not pal:
            continue
        arq = cena_dir / "legenda_en.json"
        if arq.exists():
            continue
        fr = [{"ini": g[0]["ini"], "fim": g[-1]["fim"], "pt": " ".join(x["w"] for x in g), "en": ""}
              for g in editar.frases(pal, pausa=0.35)]
        gravar_json(arq, fr)
        diga(f"   {arq.relative_to(PROJETOS.parent)}  ({len(fr)} frases para traduzir)")
    diga(f"Preencha o campo 'en' de cada frase e rode: vsl.py produzir {proj['slug']} --final --legenda en")


def cmd_motor_b(a) -> None:
    proj = carregar(a.slug)
    if a.desligar:
        proj["motor"] = "A"
        proj["motor_b"] = {"ligado": False, "autorizacao": None}
        salvar(proj)
        diga("Motor B desligado. Volta tudo para gravação real.")
        return
    if not a.autorizacao or "motor b" not in a.autorizacao.lower():
        erro('O Motor B só liga com o comando explícito do Rafael, ex.: --autorizacao "usa o motor B nesta VSL".')
    proj["motor"] = "B"
    proj["motor_b"] = {"ligado": True, "autorizacao": a.autorizacao, "quando": agora()}
    salvar(proj)
    diga("Motor B LIGADO só nesta VSL. Marque no roteiro os blocos com \"motor_b\": true (os demais seguem com gravação real).")
    diga("Antes de gerar, a máquina vai mostrar o custo e esperar o seu OK.")


def cmd_status(a) -> None:
    proj = carregar(a.slug)
    bl = blocos(a.slug)
    apr = ler_json(pasta(a.slug) / "aprovacao.json", {})
    custo = ler_json(pasta(a.slug) / "custo.json", {})
    diga(f"Projeto {proj['slug']} · {proj['produto']} · {proj['formato']} · Motor {proj['motor']} · versão final atual: v{proj['versao']}")
    diga(f"Roteiro: {len(bl)} blocos · " + ("aprovado" if apr.get("hash") == hash_roteiro(bl) and bl else "NÃO aprovado"))
    diga(f"Custo: " + (f"US$ {custo.get('total_usd', 0):.2f} ({'aceito' if custo.get('aceito') else 'não aceito'})" if custo else "ainda não mostrado"))
    cmd_takes(a)
    for h in proj["historico"]:
        diga(f"   v{h['versao']} · {h['quando']} · {h['arquivo']} · refeitas: {', '.join(h['renderizadas']) or '—'}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Máquina de VSL")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("novo"); s.add_argument("slug"); s.add_argument("--produto", default="curso"); s.add_argument("--formato", default="16:9", choices=list(FORMATOS)); s.set_defaults(f=cmd_novo)
    s = sub.add_parser("rascunho"); s.add_argument("slug"); s.add_argument("--sobrescrever", action="store_true"); s.set_defaults(f=cmd_rascunho)
    s = sub.add_parser("mostrar"); s.add_argument("slug"); s.set_defaults(f=cmd_mostrar, sobrescrever=False)
    s = sub.add_parser("aprovar"); s.add_argument("slug"); s.add_argument("--frase", required=True); s.set_defaults(f=cmd_aprovar)
    s = sub.add_parser("custo"); s.add_argument("slug"); s.add_argument("--aceitar", action="store_true"); s.set_defaults(f=cmd_custo)
    s = sub.add_parser("takes"); s.add_argument("slug"); s.set_defaults(f=cmd_takes)
    s = sub.add_parser("take"); s.add_argument("slug"); s.add_argument("bloco"); s.add_argument("arquivo"); s.set_defaults(f=cmd_take)
    s = sub.add_parser("produzir"); s.add_argument("slug"); s.add_argument("--final", action="store_true"); s.add_argument("--escala", type=float, default=0.5); s.add_argument("--legenda", default="pt", choices=["pt", "en"]); s.set_defaults(f=cmd_produzir)
    s = sub.add_parser("frases"); s.add_argument("slug"); s.set_defaults(f=cmd_frases)
    s = sub.add_parser("motor-b"); s.add_argument("slug"); s.add_argument("--autorizacao"); s.add_argument("--desligar", action="store_true"); s.set_defaults(f=cmd_motor_b)
    s = sub.add_parser("status"); s.add_argument("slug"); s.set_defaults(f=cmd_status)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
