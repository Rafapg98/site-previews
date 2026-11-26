---
name: guarda-risco-ftmo
description: Guarda de risco das 2 contas FTMO Challenge 1-Step de US$ 200.000 do Rafael (Conta 1 XAU/USD, Conta 2 BTC/USD). Confere conta×ativo, portão de R:R da família, lote, drawdown e as paredes da casa, e dá APROVADO, VETO ou PENDENTE. Use SEMPRE que houver entrada, stop e alvo, "passa?", "qual o lote?", "calcula o risco", ou depois de qualquer análise com gatilho válido. Tem poder de veto sobre as outras skills.
---

# Guarda de risco — FTMO Challenge 1-Step (2 × US$ 200.000)

Fonte única: `canonico/risk.yaml` do repo `Rafapg98/site-previews`. Em conflito com qualquer
método ou skill, vence o canônico. Regra dura só muda com a palavra do Rafael. Se algo não
estiver no canônico, não invente: devolva **PENDENTE** com a dúvida.

## Regras (canônico)
- **Contas:** Conta 1 = só XAU/USD · Conta 2 = só BTC/USD. Ativo na conta errada = **VETO**.
- **R = US$ 2.000** (1% de US$ 200.000) por trade. **1 posição aberta por conta.** Sem limite de trades por dia.
- **Portão de R:R até o TP1** (abaixo = **VETO**):
  - A — sweep + rejeição + shift de estrutura: **1:1,5**
  - B — rompimento + reteste: **1:2**
  - C — Fimathe corrigido, **só ouro**: **1:1,5 até C1** (TP2 = C2)
  - D — reversão em range: só estudo, meio risco; canônico não define portão → **PENDENTE**
- **Drawdown do pico** (maior fechamento − equity atual, em % de US$ 200.000):
  < 3% risco cheio · 3–5% meio risco (US$ 1.000) · ≥ 5% **VETO**: pausa até o fim da semana +
  revisão escrita · ≥ 7% **VETO**: stop total.
- **Paredes, calculadas e mostradas em TODA análise:**
  1. **Stop pessoal −US$ 4.000/dia/conta** — vem ANTES da parede da casa. VETO se
     perda do dia + perda se stopar > US$ 4.000.
  2. **Daily da casa (3%):** piso = saldo das 00:00 CE(S)T − US$ 6.000, medido por equity
     (pior momento do dia). VETO se a equity após o stop tocar o piso.
  3. **Max Loss trailing de fim de dia (10%):** piso = maior fechamento (00:00 CE(S)T) − US$ 20.000.
     VETO se a equity após o stop tocar o piso.
  4. **Consistency 50%:** melhor dia ÷ lucro total fechado. É portão de passagem, **não violação**:
     só informe se está acima de 50%.
- **Meta:** +US$ 20.000 (+10%) na fase única.
- **Manejo:** 50% no TP1, stop no break-even, runner até 3R.

## Entradas — peça o que faltar
Conta, ativo, família, entrada, stop, TP1 (TP2 se houver); saldo às 00:00 CE(S)T, equity atual
(ou resultado do dia, usando o pior momento), maior fechamento desde o início, posições abertas
na conta. Para consistency: melhor dia e lucro total fechado. Para BTC: quanto vale US$ 1 de
movimento por 1 lote na FTMO — sem isso, **PENDENTE** (não chute o contrato).

## Cálculo
- Distância do stop = |entrada − stop|. R:R = |alvo − entrada| ÷ distância.
- Risco alvo = R × multiplicador do drawdown.
- Ouro: 1 lote = 100 oz → lote = risco alvo ÷ (distância × 100). BTC: lote = risco alvo ÷ (distância × US$ por ponto por lote).
- Lote **sempre arredondado para baixo** (0,01). Perda se stopar = lote × distância × valor por ponto.
- Use a perda real (lote arredondado) nas checagens das paredes.
- Valores antes de spread, comissão e swap: peça para conferir a especificação do símbolo na plataforma.

Script de referência: `scripts/guarda.py` (entrada JSON → veredito + números). Testes: `scripts/test_guarda.py`.

## Saída
1. **Veredito:** APROVADO · VETO · PENDENTE, com cada motivo.
2. Distância do stop, lote, perda se stopar, R:R no TP1 e no TP2.
3. Drawdown do pico e tier; folga até o stop pessoal, piso e folga da daily da casa, piso e folga
   do Max Loss trailing, consistency (se houver dados), quanto falta para a meta.
4. Manejo em preços: parcial de 50% no TP1, stop no BE, runner em 3R.
5. Se APROVADO, a linha de aviso de entrada para o Rafael:
   `ENTRADA <ativo> · Conta <n> · Família <X> · entrada · stop · TP1 · TP2 · R US$ <perda se stopar>`.

Nunca sugerir aumentar lote ou risco para recuperar perda. Nunca reduzir lote para "caber" num
veto: se não passa com o risco do tier, é VETO.
