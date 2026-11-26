# Tarefa 001 — Reescrever a skill guarda-risco-ftmo pro FTMO 1-Step canônico

**Origem:** divergência encontrada pelo próprio Claude Code na leitura do canônico
(a skill instalada ainda é da conta Instant US$ 50K; anotações antigas falam em 2-Step).
**Dono da execução:** Claude Code (fábrica). **Conferência:** Muse (operação).

## Objetivo
Substituir a skill `guarda-risco-ftmo` por uma versão que aplique EXATAMENTE as regras de
`canonico/risk.yaml` (FTMO Challenge 1-Step, 2 contas de US$ 200K), sem nenhum resíduo de
Instant 50K, 2-Step ou portão genérico 1:2.

## A skill precisa decidir, dado um plano de trade:
1. Conta e ativo corretos (Conta 1 só XAU/USD · Conta 2 só BTC/USD) — ativo errado = VETO.
2. Portão de R:R da família armada: A 1:1,5 · B 1:2 · C 1:1,5 até C1 (alvo 2 = C2) ·
   D só estudo com meio risco — abaixo do portão = VETO.
3. Tamanho: R = US$ 2.000 (1%); tiers de drawdown do pico (<3% risco cheio · 3–5% meio
   risco · ≥5% pausa + revisão · ≥7% stop total).
4. Paredes da casa, calculadas e mostradas em toda análise:
   - Daily: saldo das 00:00 CE(S)T − US$ 6.000 (medido por equity, pior momento do dia);
     stop pessoal do Rafael em −US$ 4.000 vem ANTES da parede.
   - Max Loss trailing de fim de dia: maior fechamento (00:00 CE(S)T) − US$ 20.000.
   - Consistency 50%: melhor dia ÷ lucro total fechado — é PORTÃO de passagem, não violação.
5. Sem limite de trades por dia; 1 posição aberta por conta.

## Critérios de aceite
- Nenhuma menção a Instant, 50K ou 2-Step no texto final da skill.
- 3 cenários de teste documentados no RESULTADO, com o veredito esperado × obtido:
  (a) plano de ouro na Conta 2 → VETO por ativo;
  (b) Família A com R:R 1:1,3 → VETO por portão;
  (c) plano válido de BTC Família B 1:2 com a conta a US$ 3.500 de perda no dia → VETO pelo
      stop pessoal (antes da parede de US$ 6.000 da casa).
- Entrega em `entregas/2026-11-26-001-guarda-risco-1step/` com a skill nova + `RESULTADO.md`.

## O que NÃO fazer
- Não mudar nenhuma regra dura (elas só mudam com a palavra do Rafael).
- Não mexer em `canonico/` — divergência se reporta no RESULTADO, não se corrige por cima.
