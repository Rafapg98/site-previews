"""Roteiro da VSL: rascunho na estrutura do método, versão legível (.md) e travas de copy.

O roteiro de máquina é projetos/<slug>/roteiro.json (blocos); o roteiro.md é gerado dele
para o Rafael ler e aprovar. As TELAS (oferta, prova, payback…) são montadas na hora da
produção a partir do config/produtos.json — por isso trocar um preço lá muda só a cena
que mostra aquele preço.
"""
from __future__ import annotations

import re

from comum import moeda, produtos

# ordem do método (metodo/estrutura-vsl.md). "ecossistema" entra logo após a oferta do curso.
ORDEM = ["hook", "historia", "mecanismo", "oferta", "ecossistema", "prova", "payback",
         "garantia", "qualificacao", "cta"]

CENA_PADRAO = {
    "hook": ("fala", "Talking-head close, energia alta. Lower-third com nome. Corte seco, sem vinheta."),
    "historia": ("fala", "Talking-head + B-roll (obras reais dele quando houver; senão B-roll gráfico). Zoom punch-in na virada."),
    "mecanismo": ("tela", "Tela de motion: itens entrando um a um. Rafael em círculo no canto."),
    "oferta": ("tela", "Stack: itens com valor, soma riscada, 'De/Por' grande. Ding no preço. Rafael em círculo."),
    "ecossistema": ("tela", "Dois cartões: Kit Empresa Completa e ecossistema contractors ↔ subs. Curiosidade, sem revelar método."),
    "prova": ("tela", "Números validados grandes + prints reais (assets/provas/) + nomes dos depoimentos."),
    "payback": ("tela", "A conta com a base declarada embaixo. Aviso: não é promessa de renda."),
    "garantia": ("cartao", "Talking-head + selo de 7 dias girando."),
    "qualificacao": ("tela", "Lista 'Não é pra você se…' com X vermelho."),
    "cta": ("cartao", "Talking-head close + botão pulsando. CTA único."),
}

TEMPO_PADRAO = {"hook": 10, "historia": 40, "mecanismo": 30, "oferta": 30, "ecossistema": 20,
                "prova": 25, "payback": 20, "garantia": 12, "qualificacao": 15, "cta": 12}

TITULOS = {"hook": "Hook", "historia": "História e inimigo nomeado", "mecanismo": "Mecanismo",
           "oferta": "Oferta com stack ancorado", "ecossistema": "Bloco ecossistema",
           "prova": "Prova nomeada", "payback": "Payback factual", "garantia": "Garantia",
           "qualificacao": "Qualificação reversa", "cta": "CTA único"}


_CAMPOS_MOEDA = {"preco_de", "preco_por", "depois", "ticket_medio", "lucro_medio_por_obra", "valor",
                 "mentoria_para_quem_tem_kit", "kit_para_quem_tem_mentoria"}


def renderizar(texto: str) -> str:
    """Troca {curso.preco_por}, {provas.google.avaliacoes}… pelos valores ATUAIS do produtos.json."""
    p = produtos()

    def troca(m):
        caminho = m.group(1).split(".")
        v = p
        for k in caminho:
            if not isinstance(v, dict) or k not in v:
                return m.group(0)  # desconhecido: fica visível e a trava acusa
            v = v[k]
        if isinstance(v, (int, float)) and caminho[-1] in _CAMPOS_MOEDA:
            return moeda(v)
        return str(v)
    return re.sub(r"\{([a-z_]+(?:\.[a-z_0-9]+)+)\}", troca, texto)


def _falas_curso(p: dict) -> dict:
    c = p["curso"]
    pv = p["provas"]
    pb = p["payback"]
    return {
        "hook": ("Você que trabalha com construção aqui nos Estados Unidos: dá pra sair da diária e ter a sua "
                 "própria empresa, montada do jeito certo — sem pagar agência que não entrega e sem cair em guru. "
                 "E você tem {garantia.dias} dias pra testar sem risco."),
        "historia": ("Eu passei anos trabalhando de sub, de segunda a segunda. Teve uma hora que eu quase voltei pro Brasil. "
                     "Hoje eu vivo da minha própria empresa, a RP Renovations, aqui em Tampa Bay. E o problema nunca foi "
                     "falta de trabalho: foi cair na mão de quem vive de vender pra contractor. Agência que cobra e não entrega. "
                     "Guru que vive de curso. Intermediário que fica com a sua margem. Eu não vivo de curso. Eu vivo da obra."),
        "mecanismo": ("No curso eu te mostro o passo a passo que eu usei pra montar a minha: como abrir a LLC, como aparecer "
                      "no Google, como ter um site que vende, como controlar orçamento e obra num dashboard e como chegar "
                      "nos clientes. É o mesmo sistema que roda na minha empresa todo dia."),
        "oferta": ("O {curso.nome} sai de {curso.preco_de} por {curso.preco_por}. Você ainda leva os 2 e-books "
                   "e o primeiro mês do plano {curso.assinatura.plano} grátis, com o cupom {curso.assinatura.cupom}. "
                   "Depois, se quiser ficar, são {curso.assinatura.depois} por mês."),
        "ecossistema": ("E isso é só a porta de entrada. Dentro da plataforma tem um mundo maior: o Kit Empresa Completa, "
                        "pra quem quer a empresa montada com a gente do lado, e o ecossistema de trabalho entre contractors "
                        "e subs. Quando você entrar, explora. Você vai ver."),
        "prova": ("Não é teoria. Minha empresa tem nota {provas.google.nota} no Google com {provas.google.avaliacoes} "
                  "avaliações. Em 2026 a gente já passou de 1 milhão de dólares em obras vendidas e de 160 orçamentos "
                  "fechados. E quem já passou por aqui fala por si: "
                  + ", ".join(d["nome"] for d in pv["depoimentos"]) + "."),
        "payback": ("Faz a conta comigo, com base real: nas 9 obras que eu tenho no Jobber, o ticket médio foi de "
                    "{payback.ticket_medio} e o lucro médio, uns {payback.lucro_medio_por_obra} por obra. "
                    "Isso não é promessa de quanto você vai ganhar. É o número da minha empresa, pra você ver o tamanho "
                    "do que dá pra construir."),
        "garantia": ("E o risco é meu: você tem {garantia.dias} dias de garantia. Se achar que não é pra você, "
                     "eu devolvo 100%, sem perguntas."),
        "qualificacao": ("Agora, isso não é pra todo mundo. Não é pra quem quer apertar um botão e ver dinheiro cair. "
                         "Não é pra quem ainda não tem nada pra vender. E não é pra quem espera resultado sem trabalhar."),
        "cta": ("Se você trabalha com construção aqui nos Estados Unidos e quer empresa de verdade, clica no botão "
                "e garante a sua vaga por {curso.preco_por}. Empresa de verdade, sem guru."),
    }


def _falas_kit_ou_mentoria(p: dict, chave: str) -> dict:
    base = _falas_curso(p)
    prod = p[chave]
    if chave == "kit":
        base["mecanismo"] = ("O Kit é o setup da sua empresa feito com a gente: LLC aberta com o Google Setup 1:1, dashboard, "
                             "site e folder, templates de invoice e estimate com cláusulas de proteção, QR codes e identidade "
                             "visual. Importante: o Kit é o setup. Ele não inclui operar Google Ads nem o selo verificado do "
                             "Local Services, que é aprovação do Google.")
        base["oferta"] = ("Somando tudo, são {kit.preco_de}. Hoje o Kit sai de {kit.preco_de} por "
                          "{kit.preco_por}. E de bônus do lote de lançamento: o Compliance Pack e 1 mês de Growth grátis.")
        base["payback"] += " Uma obra média paga o Kit {payback.kit_vezes}."
    else:
        base["mecanismo"] = ("Na Mentoria 1:1 eu olho a sua empresa com você, de perto: operação, preço, orçamento e obra.")
        base["oferta"] = ("A Mentoria 1:1 é {mentoria.preco_por}, com 3 meses de Growth grátis. Quem já tem o Kit "
                          "paga {desconto_cruzado.mentoria_para_quem_tem_kit}.")
        base["payback"] += " Uma obra média paga a Mentoria {payback.mentoria_vezes}."
    base["cta"] = ("Se fez sentido, aplica no botão e me chama no WhatsApp. A gente conversa antes, pra ver se é pra você. "
                   "Empresa de verdade, sem guru.")
    base.pop("ecossistema", None)
    return base


def rascunho(produto: str) -> list[dict]:
    p = produtos()
    falas = _falas_curso(p) if produto == "curso" else _falas_kit_ou_mentoria(p, produto)
    blocos, n = [], 0
    for sec in ORDEM:
        if sec not in falas:
            continue
        n += 1
        modo, direcao = CENA_PADRAO[sec]
        blocos.append({
            "id": sec, "ordem": n, "titulo": TITULOS[sec], "fala": falas[sec],
            "tempo_estimado_s": TEMPO_PADRAO[sec], "modo": modo, "direcao": direcao,
            "take": f"{n:02d}-{sec}", "motor_b": False,
        })
    return blocos


def para_markdown(proj: dict, blocos: list[dict], aprovado: dict | None) -> str:
    total = sum(b["tempo_estimado_s"] for b in blocos)
    linhas = [f"# Roteiro — {proj['slug']}", "",
              f"- Produto: **{proj['produto']}** · Formato: **{proj['formato']}** · Motor: **{proj['motor']}**",
              f"- Duração estimada: **~{total // 60}min{total % 60:02d}s**",
              f"- Status: **{'APROVADO em ' + aprovado['quando'] if aprovado and aprovado.get('aprovado') else 'aguardando aprovação do Rafael'}**",
              "", "> Grave cada bloco num arquivo separado em `entrada/" + proj["slug"] + "/` com o nome indicado "
              "(ex.: `01-hook.mp4`). Errou? Fala **\"corta\"**, respira e repete a frase inteira — a máquina tira o erro.", ""]
    t = 0
    for b in blocos:
        linhas += [f"## {b['ordem']}. {b['titulo']}  ·  {t // 60}:{t % 60:02d}–{(t + b['tempo_estimado_s']) // 60}:{(t + b['tempo_estimado_s']) % 60:02d}",
                   "", f"**Fala:** {renderizar(b['fala'])}", "", f"**Cena:** `{b['modo']}` — {b['direcao']}", "",
                   f"**Arquivo do take:** `entrada/{proj['slug']}/{b['take']}.mp4`" + ("  · **Motor B**" if b.get("motor_b") else ""), ""]
        t += b["tempo_estimado_s"]
    return "\n".join(linhas)


# ------------------------------------------------------------------ travas de copy
PROMESSAS_PROIBIDAS = [
    r"garant\w* (que )?(você|vc) vai (faturar|ganhar|lucrar)", r"renda garantida", r"lucro garantido",
    r"leads? garantid", r"clientes? garantid", r"dinheiro garantido", r"fique rico", r"ficar rico",
    r"você vai (faturar|ganhar|lucrar)", r"resultado garantido",
]

_ALIASES = {"1 milhão": "1", "um milhão": "1", "1 milhao": "1"}


def _numeros(texto: str) -> set[float]:
    for k, v in _ALIASES.items():
        texto = texto.replace(k, v)
    texto = re.sub(r"(\d+)\s*mil\b", lambda m: str(int(m.group(1)) * 1000), texto)
    achados = set()
    for m in re.findall(r"\d[\d.,]*", texto):
        m = m.rstrip(".,")
        if re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", m):      # 14.021 / 1.750,00
            v = float(m.replace(".", "").replace(",", "."))
        elif re.fullmatch(r"\d+,\d+", m):                       # 9,90 / 34,5
            v = float(m.replace(",", "."))
        elif re.fullmatch(r"\d{1,3}(,\d{3})+(\.\d+)?", m):      # 14,021 (formato EUA)
            v = float(m.replace(",", ""))
        else:
            try:
                v = float(m)
            except ValueError:
                continue
        achados.add(round(v, 2))
    return achados


def numeros_permitidos() -> set[float]:
    import json
    texto = json.dumps(produtos(), ensure_ascii=False)
    return _numeros(texto) | {100.0}  # "100%" da garantia já está no produtos.json; mantido explícito


def checar_copy(blocos: list[dict]) -> list[str]:
    """Devolve a lista de problemas (vazia = ok)."""
    problemas = []
    permitidos = numeros_permitidos()
    for b in blocos:
        texto = renderizar(b["fala"])
        if re.search(r"\{[a-z_.0-9]+\}", texto):
            problemas.append(f"[{b['id']}] referência desconhecida ao produtos.json: {re.findall(r'[{][a-z_.0-9]+[}]', texto)}")
        # negação explícita ("não é promessa de quanto você vai ganhar") é permitida
        texto_promessa = re.sub(r"n[ãa]o (é|e) promessa[^.]*", "", texto, flags=re.I)
        fora = sorted(n for n in _numeros(texto) if n not in permitidos)
        if fora:
            problemas.append(f"[{b['id']}] número fora do produtos.json: {', '.join(str(x).rstrip('0').rstrip('.') for x in fora)}")
        for padrao in PROMESSAS_PROIBIDAS:
            achado = re.search(padrao, texto_promessa, flags=re.I)
            if achado:
                problemas.append(f"[{b['id']}] promessa proibida: “{achado.group(0)}”")
    return problemas
