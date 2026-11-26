---
description: Produzir uma VSL (briefing → roteiro aprovado → custo → preview → ajustes → final)
---

# /vsl — produzir uma VSL

Siga as etapas **na ordem, sem pular**. Fale em português simples. Rode os comandos você mesmo
(`python3 ferramentas/vsl.py ...`) e mostre ao Rafael só o que importa.

## 1. Briefing (uma pergunta por vez)

1. **Qual produto?** curso (US$ 97) · Kit Empresa Completa · Mentoria 1:1 — leia `config/produtos.json`.
2. **Qual formato?** 16:9 (página de vendas) ou 9:16 (anúncio/stories).
3. **Motor:** A (gravação real) é o padrão — não pergunte. Só use o B se ele disser explicitamente
   "usa o motor B nesta VSL" (aí: `vsl.py motor-b <slug> --autorizacao "<frase dele>"`).
4. **Trouxe roteiro?** (arquivo em `entrada/`, ou colado no chat).

Crie o projeto: `vsl.py novo <slug> --produto <curso|kit|mentoria> --formato <16:9|9:16>`
(slug curto, ex.: `curso-97-dez`).

## 2. Roteiro

- **Sem roteiro dele:** `vsl.py rascunho <slug>` gera o rascunho na estrutura do método
  (`metodo/estrutura-vsl.md`) com os termos do `produtos.json`. Leia, melhore com ele e edite
  `projetos/<slug>/roteiro.json` (campo `fala` de cada bloco).
- **Com roteiro dele:** adapte o texto dele aos blocos da estrutura (mesmos `id`), mantendo a voz dele.
- Regras: `metodo/copy-regras.md`. Curso de US$ 97 → **bloco ecossistema obrigatório** logo após a oferta.
- `vsl.py mostrar <slug>` → mostre o `roteiro.md` **inteiro** (tempos + direção de cena + nome do
  arquivo de cada take). Se aparecer "⚠️ Travas de copy", corrija antes de mostrar.
- **Só avance com o "aprovado" dele.** Então: `vsl.py aprovar <slug> --frase "<o que ele disse>"`.
  Se o roteiro mudar depois, precisa de novo "aprovado".

## 3. Custo antes de gerar

`vsl.py custo <slug>` → mostre a estimativa. Motor A = **US$ 0** (tudo local).
Se o total for > 0 (Motor B ou B-roll por IA ligado), espere o OK dele e rode `vsl.py custo <slug> --aceitar`.

## 4. Gravação e produção por cena

- `vsl.py takes <slug>` → lista o que falta gravar. Passe pra ele a lista de arquivos
  (`entrada/<slug>/01-hook.mp4`, `02-historia.mp4`…) e as dicas: peito pra cima, luz de frente,
  "corta" quando errar.
- Com os takes na pasta: `vsl.py produzir <slug>` → preview (meia resolução, rápido) em
  `projetos/<slug>/preview/`.
- Mostre o relatório: duração, erros cortados, cenas refeitas/reaproveitadas, avisos.

## 5. Ajustes ("refaz só o que mudou")

| Ele pede | Você faz |
|---|---|
| "muda o preço" | edita `config/produtos.json` → `vsl.py produzir` → só a cena da oferta é refeita. Se o aviso disser que o take ainda fala o preço antigo, peça pra regravar **só** aquele take. |
| "testa outro começo" | novo take `01-hook-b.mp4` → `vsl.py take <slug> hook 01-hook-b.mp4` → `produzir` |
| "troca a frase do bloco X" | edita o roteiro → mostra → novo "aprovado" → novo take do bloco X → `produzir` |
| "legenda maior / outra cor" | `config/marca.json` → `produzir` (todas as cenas mudam, é esperado) |

## 6. Final

`vsl.py produzir <slug> --final` → `projetos/<slug>/final/<produto>-vsl-v<versao>.mp4` (resolução cheia).
Versão EN: `vsl.py frases <slug>` → traduza cada `en` (natural, mesmo sentido, sem números novos) →
`vsl.py produzir <slug> --final --legenda en` → `...-vsl-v<versao>-EN.mp4` (mesmo vídeo, legenda EN).

**Nada é publicado ou enviado.** Diga onde está o arquivo e pronto — ele sobe onde quiser.
