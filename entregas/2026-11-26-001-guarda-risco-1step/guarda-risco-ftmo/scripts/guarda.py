#!/usr/bin/env python3
"""Guarda de risco — FTMO Challenge 1-Step, 2 contas de US$ 200K.

Espelha canonico/risk.yaml (Rafapg98/site-previews, versão 2026-11-26).
Se este arquivo divergir do canônico, vale o canônico: reporte, não corrija aqui por conta própria.

Uso:
  python3 guarda.py plano.json        (ou JSON via stdin)
Saída: JSON com veredito (APROVADO / VETO / PENDENTE), motivos e todos os números.
"""
import json
import math
import sys

# ---- Regras canônicas (canonico/risk.yaml) ----
TAMANHO_CONTA = 200_000
ATIVO_POR_CONTA = {1: "XAU/USD", 2: "BTC/USD"}
META_USD = 20_000                 # +10% fase única
DAILY_CASA_USD = 6_000            # 3%, piso = saldo 00:00 CE(S)T - 6.000, por equity
MAX_LOSS_USD = 20_000             # 10% trailing de fim de dia
CONSISTENCY = 0.50                # portão de passagem, não violação
R_USD = 2_000                     # 1% por trade
STOP_PESSOAL_USD = 4_000          # por conta, por dia (vem antes da parede da casa)
POSICOES_MAX = 1
PORTAO_RR = {"A": 1.5, "B": 2.0, "C": 1.5}   # C: medido até C1 (TP1); alvo 2 = C2
FAMILIA_C_SO_OURO = True
OZ_POR_LOTE_XAU = 100


def tier_drawdown(dd_pct):
    """Retorna (multiplicador de risco, ação) pelo drawdown do pico."""
    if dd_pct >= 7:
        return 0.0, "STOP TOTAL (drawdown >= 7%)"
    if dd_pct >= 5:
        return 0.0, "PAUSA até o fim da semana + revisão escrita (drawdown >= 5%)"
    if dd_pct >= 3:
        return 0.5, "meio risco (drawdown 3-5%)"
    return 1.0, "risco cheio (drawdown < 3%)"


def avaliar(p):
    vetos, pendencias, avisos = [], [], []
    conta = int(p["conta"])
    ativo = p["ativo"].upper().replace("XAUUSD", "XAU/USD").replace("BTCUSD", "BTC/USD")
    familia = p["familia"].upper()
    entrada, stop = float(p["entrada"]), float(p["stop"])
    tp1 = float(p["tp1"])
    tp2 = float(p["tp2"]) if p.get("tp2") is not None else None

    saldo_00h = float(p["saldo_00h"])                    # saldo às 00:00 CE(S)T de hoje
    equity = float(p.get("equity_atual", saldo_00h + float(p.get("resultado_dia", 0))))
    resultado_dia = equity - saldo_00h                   # pior momento conta: passe a equity mais baixa
    maior_fech = float(p.get("maior_fechamento", max(saldo_00h, TAMANHO_CONTA)))
    posicoes_abertas = int(p.get("posicoes_abertas", 0))

    # 1. Conta x ativo
    if conta not in ATIVO_POR_CONTA:
        vetos.append(f"Conta {conta} não existe no canônico (só 1 e 2).")
    elif ATIVO_POR_CONTA[conta] != ativo:
        vetos.append(f"Ativo errado: Conta {conta} só opera {ATIVO_POR_CONTA[conta]}, plano é {ativo}.")

    # 5. Posições abertas
    if posicoes_abertas >= POSICOES_MAX:
        vetos.append(f"Já há {posicoes_abertas} posição aberta na Conta {conta} (máx. {POSICOES_MAX}).")

    # Geometria do trade
    dist = abs(entrada - stop)
    if dist == 0:
        vetos.append("Stop igual à entrada.")
        dist = float("nan")
    comprado = entrada > stop
    if (comprado and tp1 <= entrada) or (not comprado and tp1 >= entrada):
        vetos.append("TP1 do lado errado da entrada.")
    rr1 = abs(tp1 - entrada) / dist
    rr2 = abs(tp2 - entrada) / dist if tp2 is not None else None

    # 2. Portão da família
    if familia == "D":
        pendencias.append("Família D é só estudo com meio risco e o canônico não define portão de R:R: "
                          "sem veredito até o Rafael definir.")
    elif familia not in PORTAO_RR:
        vetos.append(f"Família {familia} não existe no canônico (A, B, C, D).")
    else:
        if familia == "C" and FAMILIA_C_SO_OURO and ativo != "XAU/USD":
            vetos.append("Família C (Fimathe) é só ouro.")
        portao = PORTAO_RR[familia]
        if rr1 + 1e-9 < portao:
            alvo = "C1" if familia == "C" else "TP1"
            vetos.append(f"Portão: Família {familia} exige 1:{portao:g} até {alvo}, plano dá 1:{rr1:.2f}.")

    # 3. Tamanho: drawdown do pico
    dd_usd = max(0.0, maior_fech - equity)
    dd_pct = dd_usd / TAMANHO_CONTA * 100
    mult, acao_dd = tier_drawdown(dd_pct)
    if familia == "D":
        mult = min(mult, 0.5)
    risco_alvo = R_USD * mult
    if mult == 0:
        vetos.append(f"Drawdown do pico {dd_pct:.2f}%: {acao_dd}.")

    # Lote
    if ativo == "XAU/USD":
        usd_por_ponto_lote = OZ_POR_LOTE_XAU
    else:
        usd_por_ponto_lote = p.get("btc_usd_por_ponto_por_lote")
        if usd_por_ponto_lote is None:
            pendencias.append("Especificação do contrato BTC/USD na FTMO não confirmada: informe quanto vale "
                              "US$ 1 de movimento por 1 lote para calcular o lote.")
    lote = perda_real = None
    if usd_por_ponto_lote and risco_alvo > 0 and not math.isnan(dist):
        lote = math.floor(risco_alvo / (dist * float(usd_por_ponto_lote)) * 100) / 100   # sempre para baixo
        perda_real = lote * dist * float(usd_por_ponto_lote)
        if lote <= 0:
            vetos.append("Stop largo demais: o lote mínimo (0,01) passaria do risco permitido.")
    risco_checagem = perda_real if perda_real else risco_alvo

    # 4. Paredes
    perda_dia = max(0.0, -resultado_dia)
    folga_pessoal = STOP_PESSOAL_USD - perda_dia
    piso_daily = saldo_00h - DAILY_CASA_USD
    piso_maxloss = maior_fech - MAX_LOSS_USD
    if folga_pessoal <= 0:
        vetos.append(f"Stop pessoal do dia já atingido (−US$ {perda_dia:,.0f}): fim do dia nesta conta.")
    elif risco_checagem > folga_pessoal + 1e-6:
        vetos.append(f"Stop pessoal: perda do dia −US$ {perda_dia:,.0f} + risco US$ {risco_checagem:,.0f} "
                     f"passaria de −US$ {STOP_PESSOAL_USD:,} (folga só US$ {folga_pessoal:,.0f}).")
    if equity - risco_checagem <= piso_daily:
        vetos.append(f"Parede daily da casa: equity após stop ficaria em US$ {equity - risco_checagem:,.0f}, "
                     f"piso US$ {piso_daily:,.0f}.")
    if equity - risco_checagem <= piso_maxloss:
        vetos.append(f"Parede Max Loss trailing: equity após stop ficaria em US$ {equity - risco_checagem:,.0f}, "
                     f"piso US$ {piso_maxloss:,.0f}.")

    # Consistency (informativo, portão de passagem)
    consist = None
    lucro_total = p.get("lucro_total_fechado")
    melhor_dia = p.get("melhor_dia")
    if lucro_total and melhor_dia is not None and float(lucro_total) > 0:
        consist = float(melhor_dia) / float(lucro_total)
        if consist > CONSISTENCY:
            avisos.append(f"Consistency {consist:.0%} > 50%: ainda não passa — não é violação, "
                          "precisa de mais dias de lucro.")

    # Manejo (canônico): 50% no TP1, stop no BE, runner até 3R
    runner_3r = entrada + 3 * dist if comprado else entrada - 3 * dist

    if vetos:
        veredito = "VETO"
    elif pendencias:
        veredito = "PENDENTE"
    else:
        veredito = "APROVADO"

    out = {
        "veredito": veredito,
        "vetos": vetos,
        "pendencias": pendencias,
        "avisos": avisos,
        "conta": conta, "ativo": ativo, "familia": familia,
        "direcao": "compra" if comprado else "venda",
        "distancia_stop": round(dist, 2),
        "rr_tp1": round(rr1, 2), "rr_tp2": round(rr2, 2) if rr2 is not None else None,
        "risco_alvo_usd": risco_alvo, "lote": lote,
        "perda_se_stopar_usd": round(perda_real, 2) if perda_real is not None else None,
        "drawdown_pico_pct": round(dd_pct, 2), "tier_drawdown": acao_dd,
        "paredes": {
            "stop_pessoal": {"perda_dia_usd": perda_dia, "folga_usd": folga_pessoal},
            "daily_casa": {"piso_usd": piso_daily, "folga_usd": equity - piso_daily},
            "max_loss_trailing": {"piso_usd": piso_maxloss, "folga_usd": equity - piso_maxloss},
            "consistency": None if consist is None else round(consist, 3),
            "meta_restante_usd": max(0.0, TAMANHO_CONTA + META_USD - equity),
        },
        "manejo": {"parcial_50pct": tp1, "depois": "stop no break-even", "runner_3R": round(runner_3r, 2)},
    }
    if veredito == "APROVADO":
        out["aviso_entrada"] = (f"ENTRADA {ativo} · Conta {conta} · Família {familia} · entrada {entrada:g} · "
                                f"stop {stop:g} · TP1 {tp1:g} · TP2 {tp2 if tp2 is not None else '-'} · "
                                f"R US$ {risco_checagem:,.0f}")
    return out


if __name__ == "__main__":
    src = open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin
    print(json.dumps(avaliar(json.load(src)), ensure_ascii=False, indent=2))
