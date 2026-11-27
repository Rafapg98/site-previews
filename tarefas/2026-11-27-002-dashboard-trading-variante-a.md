# Tarefa 002 — Alinhar o Dashboard Trading à estratégia oficial (Variante A)

**Origem:** Muse (operação), 2026-11-27. **Fonte canônica:** `canonico/risk.yaml` (atualizado em 2026-11-27) + skill `fimathe-market-analysis` (seção "ESTRATÉGIA OFICIAL NO AR").

## Contexto
O Programa Estratégia Décadas terminou e a estratégia nova entrou no ar. O Dashboard Trading ainda reflete o desenho antigo (núcleo intraday A/B/C como sistema principal, BTC a 1%). Alinhar os cartões e textos do dashboard ao desenho vigente:

## O que mudar
1. **Arquitetura por conta (cartões principais):**
   - Conta 1 · XAU/USD = ÂNCORA: trend diário (momentum-100d + Donchian 20/10 D1), risco 1% (R US$ 2.000 / reduzido US$ 1.000), expectancy histórica +0,33R.
   - Conta 2 · BTC/USD = MOTOR (Variante A): Donchian 20/10 H4 + bolso de Londres com a conta livre, risco **0,5% (R US$ 1.000 / reduzido US$ 500)**, meta exibida também em R: **+20R** (= US$ 20.000).
2. **Qualquer lugar que mostre BTC a R = US$ 2.000 está errado** — corrigir pra US$ 1.000/US$ 500.
3. **Famílias A/B/C:** rotular como "Programa de estudo — veredito 26/12/2026" (não são mais apresentadas como o sistema das contas). Família D: "aposentada".
4. **Bloco de payout (novo ou ajustar o existente de withdrawals/break-even):** regra = saque mensal só do lucro acima de (pico de fechamento − US$ 4.000); freio: DD ajustado > US$ 6.000 = não sacar; mostrar por conta: pico, saldo, sacável, líquido (90%), distância ao piso trailing. Manter o registro da taxa paga (US$ 919/conta) e o break-even combinado (US$ 1.838).
5. **Janela de scaling (novo, compacto):** meses desde funded/último scale-up, lucro líquido na janela de 4 meses (meta ≥10%), Rewards processados na janela (meta ≥2), saldo — com aviso quando a janela estiver fechando curta.
6. **Journal:** garantir os campos sessão, stop em US$ e em R, custo estimado em R por trade/veto, e a tag TRACK-T pros sinais dos motores de tendência (que agora são a estratégia oficial em estudo).

## Critérios de aceite
- Nenhum cartão mostra BTC com R = US$ 2.000 nem as famílias A/B/C como motor das contas.
- Conta 2 mostra meta +20R e risco 0,5%.
- Bloco de payout com a regra do pico − US$ 4.000 e o freio de US$ 6.000 visíveis.
- Entrega em `entregas/2026-11-27-002-dashboard-trading-variante-a/` com RESULTADO.md (o que mudou, prints ou descrição tela a tela).
