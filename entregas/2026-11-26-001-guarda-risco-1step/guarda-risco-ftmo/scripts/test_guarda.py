#!/usr/bin/env python3
"""Testes da guarda. Rodar da raiz do repo: python3 entregas/2026-11-26-001-guarda-risco-1step/guarda-risco-ftmo/scripts/test_guarda.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import guarda as g  # noqa: E402

BASE = {"saldo_00h": 200_000, "maior_fechamento": 200_000, "posicoes_abertas": 0}
falhas = 0


def caso(nome, plano, esperado, contem):
    global falhas
    r = g.avaliar({**BASE, **plano})
    motivos = " | ".join(r["vetos"] + r["pendencias"])
    ok = r["veredito"] == esperado and contem in motivos
    falhas += not ok
    print(f"[{'OK' if ok else 'FALHOU'}] {nome}\n   esperado: {esperado} ({contem})\n   obtido:   {r['veredito']} — {motivos or '-'}")
    return r


# (a) ouro na Conta 2
caso("(a) ouro na Conta 2", {"conta": 2, "ativo": "XAU/USD", "familia": "A",
     "entrada": 2650, "stop": 2640, "tp1": 2665}, "VETO", "Ativo errado")

# (b) Família A com 1:1,3
caso("(b) Família A 1:1,3", {"conta": 1, "ativo": "XAU/USD", "familia": "A",
     "entrada": 2650, "stop": 2640, "tp1": 2663}, "VETO", "Portão")

# (c) BTC Família B 1:2 válido, conta -3.500 no dia
r = caso("(c) BTC B 1:2 com -US$ 3.500 no dia", {"conta": 2, "ativo": "BTC/USD", "familia": "B",
         "entrada": 95_000, "stop": 94_000, "tp1": 97_000, "tp2": 98_000,
         "btc_usd_por_ponto_por_lote": 1, "resultado_dia": -3_500}, "VETO", "Stop pessoal")
assert len(r["vetos"]) == 1, f"(c) deveria vetar SÓ pelo stop pessoal, vetou: {r['vetos']}"
assert r["paredes"]["daily_casa"]["folga_usd"] == 2_500

# Extras
caso("(d) mesmo plano (c) com dia zerado → aprova", {"conta": 2, "ativo": "BTC/USD", "familia": "B",
     "entrada": 95_000, "stop": 94_000, "tp1": 97_000, "btc_usd_por_ponto_por_lote": 1}, "APROVADO", "")
caso("(e) BTC sem contrato confirmado → pendente", {"conta": 2, "ativo": "BTC/USD", "familia": "B",
     "entrada": 95_000, "stop": 94_000, "tp1": 97_000}, "PENDENTE", "contrato BTC")
caso("(f) Família C no BTC → veto", {"conta": 2, "ativo": "BTC/USD", "familia": "C",
     "entrada": 95_000, "stop": 94_000, "tp1": 97_000, "btc_usd_por_ponto_por_lote": 1}, "VETO", "só ouro")
caso("(g) drawdown 5,5% → pausa", {"conta": 1, "ativo": "XAU/USD", "familia": "A", "maior_fechamento": 211_000,
     "entrada": 2650, "stop": 2640, "tp1": 2665}, "VETO", "PAUSA")
r = caso("(h) drawdown 4% → meio risco e aprova", {"conta": 1, "ativo": "XAU/USD", "familia": "A",
         "maior_fechamento": 208_000, "entrada": 2650, "stop": 2640, "tp1": 2665}, "APROVADO", "")
assert r["risco_alvo_usd"] == 1_000 and r["lote"] == 1.0, r
caso("(i) posição já aberta → veto", {"conta": 1, "ativo": "XAU/USD", "familia": "B", "posicoes_abertas": 1,
     "entrada": 2650, "stop": 2640, "tp1": 2670}, "VETO", "posição aberta")
caso("(j) Família D → pendente", {"conta": 1, "ativo": "XAU/USD", "familia": "D",
     "entrada": 2650, "stop": 2640, "tp1": 2670}, "PENDENTE", "Família D")

# Constantes x canonico/risk.yaml
raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
yml = os.path.join(raiz, "canonico", "risk.yaml")
if os.path.exists(yml):
    import yaml
    c = yaml.safe_load(open(yml))
    pares = [
        (g.R_USD, c["risco"]["r_usd"]), (-g.STOP_PESSOAL_USD, c["risco"]["stop_pessoal_diario_usd"]),
        (g.POSICOES_MAX, c["risco"]["posicoes_abertas_por_conta"]),
        (g.DAILY_CASA_USD, c["max_daily_loss_casa_pct"] / 100 * g.TAMANHO_CONTA),
        (g.MAX_LOSS_USD, c["max_loss_pct"] / 100 * g.TAMANHO_CONTA),
        (g.META_USD, c["meta_fase_unica_pct"] / 100 * g.TAMANHO_CONTA),
        (g.CONSISTENCY * 100, c["consistency_pct"]),
        *[(g.PORTAO_RR[f], c["familias"][f]["portao_rr"]) for f in "ABC"],
        *[(g.ATIVO_POR_CONTA[x["id"]], x["ativo"]) for x in c["contas"]],
    ]
    dif = [(a, b) for a, b in pares if a != b]
    print(f"[{'OK' if not dif else 'FALHOU'}] constantes = canonico/risk.yaml {dif or ''}")
    falhas += bool(dif)

print("\nTUDO OK" if not falhas else f"\n{falhas} FALHA(S)")
sys.exit(1 if falhas else 0)
