# RESULTADO — Tarefa 001: guarda-risco-ftmo no FTMO 1-Step canônico

**Status:** entregue como rascunho para conferência do Muse. Nada foi instalado nem publicado.

## O que foi feito
- `guarda-risco-ftmo/SKILL.md` — skill reescrita do zero a partir de `canonico/risk.yaml`
  (2 contas de US$ 200.000, Conta 1 XAU/USD, Conta 2 BTC/USD, R = US$ 2.000, portões A 1:1,5 ·
  B 1:2 · C 1:1,5 até C1 · D pendente, tiers de drawdown, stop pessoal antes da daily da casa,
  Max Loss trailing, consistency como portão, 1 posição por conta, sem limite de trades/dia).
- `guarda-risco-ftmo/scripts/guarda.py` — calculadora de referência (JSON → APROVADO/VETO/PENDENTE + números).
- `guarda-risco-ftmo/scripts/test_guarda.py` — 10 cenários + checagem automática de que as
  constantes do script batem com `canonico/risk.yaml`.
- `canonico/` não foi tocado.

## Testes (critérios de aceite)
Rodado: `python3 entregas/2026-11-26-001-guarda-risco-1step/guarda-risco-ftmo/scripts/test_guarda.py` → **TUDO OK**.
Base: saldo 00:00 = US$ 200.000, maior fechamento = US$ 200.000, sem posição aberta.

| Cenário | Plano | Esperado | Obtido |
|---|---|---|---|
| (a) | Ouro (XAU/USD) na Conta 2, Família A | VETO por ativo | **VETO** — "Conta 2 só opera BTC/USD, plano é XAU/USD" |
| (b) | Conta 1 ouro, Família A, entrada 2650 · stop 2640 · TP1 2663 (1:1,3) | VETO por portão | **VETO** — "Família A exige 1:1,5 até TP1, plano dá 1:1,30" |
| (c) | Conta 2 BTC, Família B, 95.000 · stop 94.000 · TP1 97.000 (1:2), dia em −US$ 3.500 | VETO pelo stop pessoal, antes da parede da casa | **VETO** — "−3.500 + risco 2.000 passaria de −4.000 (folga só US$ 500)". Único veto; a daily da casa ainda tinha US$ 2.500 de folga |

Extras que também passaram: mesmo plano (c) com o dia zerado → APROVADO · BTC sem contrato
confirmado → PENDENTE · Família C no BTC → VETO · drawdown 5,5% → VETO (pausa) · drawdown 4% →
APROVADO com meio risco (US$ 1.000, 1,00 lote) · posição já aberta → VETO · Família D → PENDENTE ·
constantes = canônico.

Busca no texto da skill por "Instant", "50K"/"50.000" e "2-Step": **zero ocorrências**.

## O que ficou aberto (para o Rafael decidir — não mexi no canônico)
1. **Portão da Família D:** o canônico diz "só estudo, meio risco", mas não dá R:R mínimo. A guarda
   devolve PENDENTE para D até isso ser definido.
2. **Base do % de drawdown do pico:** usei (maior fechamento − equity) ÷ US$ 200.000. Se a intenção
   for % sobre o próprio pico, os tiers mudam um pouco.
3. **Reduzir lote para caber na folga:** no cenário (c) a guarda veta em vez de sugerir um lote
   menor (US$ 500 de folga). O canônico não autoriza o ajuste, então mantive VETO. Se o Rafael quiser
   permitir "risco reduzido até a folga", é regra nova.
4. **Regras da skill antiga que saíram por não estarem no canônico:** "2 perdas = fim do dia"
   (contradiz "sem limite de trades/dia"), proibição de virada de mão e veto por entrada na Zona
   Neutra / atrasada. Se alguma deve continuar, precisa entrar no `risk.yaml`.
5. **Contrato do BTC/USD na FTMO:** valor por ponto por lote não está no canônico. A guarda pede
   a confirmação a cada uso; vale registrar no `risk.yaml`.
6. **Instalação:** a skill ativa na conta do Rafael ainda é a antiga. Substituir exige aprovação dele.
   Também vale corrigir as anotações antigas que falam em 2-Step.
