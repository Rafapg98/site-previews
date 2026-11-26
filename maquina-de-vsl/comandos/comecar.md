---
description: Instalação guiada da Máquina de VSL (em português, passo a passo)
---

# /comecar — instalação guiada

Você está instalando a Máquina de VSL para o Rafael. Fale em português simples, **um passo por vez**,
dizendo o que vai fazer antes de fazer. Ele não programa: rode tudo você mesmo.

## Passo 1 — Conferir o computador

Rode `python3 ferramentas/ambiente.py`. Se aparecer ❌, explique em uma frase o que falta e por quê
(ex.: "o FFmpeg é o cortador de vídeo") e rode `python3 ferramentas/ambiente.py --instalar`.
Se algo pedir senha do computador ou instalação manual (Node.js, Homebrew), explique o clique a clique.
Só siga quando aparecer **"Ambiente OK — o Motor A está pronto."**

## Passo 2 — Contas (só para o Motor B)

Diga: "O Motor A (gravação real) não precisa de nenhuma conta paga. ElevenLabs e fal.ai só entram se um dia
você mandar usar o Motor B numa VSL." Se ele quiser deixar pronto:
- copie `config/chaves.env.example` para `config/chaves.env`;
- abra o arquivo pra ele e peça que **ele mesmo** cole as chaves lá e salve;
- **nunca peça a chave no chat.** Se ele colar uma chave no chat, avise para gerar outra no site do serviço.
Confira só se o arquivo tem as linhas preenchidas (sem mostrar o valor).

## Passo 3 — Entrevista da marca (uma pergunta por vez)

`config/marca.json` já vem pré-preenchido com o briefing. Confirme com ele, **uma pergunta por mensagem**,
mostrando o que já está lá e perguntando "é isso ou quer mudar?":
1. Produto principal (hoje: o curso de US$ 97 — `config/produtos.json`).
2. Público (brasileiros que trabalham com construção nos EUA).
3. Tom de voz (direto, de obra, sem "fala galera").
4. Estilo visual (dourado metálico sobre verde-escuro; legenda amarela/branca embaixo, centralizada).
5. (Já respondido em 2026-11-26: depoimentos só com nome, curso sem stack itemizado, +160 orçamentos validado.)
Grave as respostas em `config/marca.json` (e `produtos.json` só para os dados que ele informar), troque
`"confirmado": true` e salve um resumo na memória do projeto (este CLAUDE.md, seção "Marca confirmada",
se ele mudar algo).

## Passo 4 — Gravação-guia + teste de 20 segundos (Motor A)

Explique como gravar:
- celular na **vertical** (ou horizontal, se a VSL for da página), na altura dos olhos, apoiado;
- **peito pra cima**, camiseta preta, **fundo limpo**, **luz de frente** (janela ou ring light na frente, nunca atrás);
- ambiente sem eco; microfone de lapela se tiver;
- errou? fala **"corta"**, respira, e repete a frase inteira — a máquina tira o erro sozinha;
- pode deixar pausas: a máquina corta os silêncios.

Peça uma gravação de ~25–30s falando qualquer coisa do dia a dia da obra, e que ele coloque o arquivo em
`entrada/teste-guia/`. Rode `python3 ferramentas/teste_guia.py` e mostre o resultado:
`projetos/_teste-guia/final/teste-20s-editado.mp4` + o relatório (✅ corte de silêncio, ✅ legenda palavra
por palavra, ✅ zoom, ✅ SFX). Pergunte o que ele achou da legenda (cor, tamanho, posição) e ajuste em
`config/marca.json` se ele pedir.

## Passo 5 — Motor B (só se ele pedir)

Só se ele disser que quer o Motor B pronto:
- **Gravação-base:** uma tomada contínua de 60–90s, sem música, de frente (roteiro e dicas em
  `assets/motor-b/ROTEIRO-GRAVACAO.md`) → `entrada/motor-b/gravacao-base.mp4`.
  Vídeo de VSL já editada NÃO serve (tem trilha por baixo e cortes; ver laudo em `assets/motor-b/LEIA-ME.md`).
- `python3 ferramentas/preparar_motor_b.py entrada/motor-b/gravacao-base.mp4` → confere e gera
  `assets/motor-b/voz-clone.wav` e `assets/motor-b/foto-base.jpg` (local, custo zero).
- **ElevenLabs** (plano Starter, inclui clone instantâneo): ele mesmo sobe o `voz-clone.wav` em
  Voices → Add a new voice → Instant Voice Clone, copia o **Voice ID** e cria uma **API key**
  (Profile/Developers → API Keys) → cola os dois em `config/chaves.env`.
- **fal.ai** (pré-pago, sem mensalidade): conta → Billing (adicionar crédito) → Keys → criar key →
  `FAL_KEY` em `config/chaves.env`. O avatar usa o modelo `veed/fabric-1.0` (foto + voz → vídeo).
- Mostre o custo da `config/custos.json` antes de qualquer geração.
- Lembre: mesmo pronto, o Motor B **só roda numa VSL quando ele mandar** "usa o motor B nesta VSL".

## Fim

Mostre um resumo: ambiente OK, marca salva, vídeo-teste pronto (com o caminho), e o próximo passo:
"Quando quiser fazer uma VSL, é só digitar **/vsl**."
