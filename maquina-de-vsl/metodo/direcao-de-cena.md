# Direção de cena

Cada bloco do roteiro tem um `modo` de cena. A máquina monta a cena sozinha a partir do take dele.

| Modo | Como fica | Usado em |
|---|---|---|
| `fala` | Talking-head dele em tela cheia + zoom punch-in + texto animado nas palavras-chave + B-roll (~3s) nas menções de produto + legenda | hook, história |
| `tela` | Tela de motion (Remotion) em verde-escuro e dourado + **ele em círculo no canto** (a voz é a dele) + legenda | mecanismo, oferta, ecossistema, prova, payback, qualificação |
| `cartao` | Talking-head + elemento por cima (selo de 7 dias / botão de CTA pulsando) | garantia, CTA |

## Bloco a bloco
- **Hook e CTA:** talking-head, close, energia alta. Hook com lower-third (nome + "Dono da RP Renovations ·
  Tampa Bay, FL"). CTA com botão pulsando e o texto do CTA do `produtos.json`.
- **História:** talking-head + B-roll **real** das obras dele quando houver (`assets/broll-real/`). B-roll de IA
  só ilustrativo genérico, **nunca fingindo ser obra dele**. Sem B-roll real nem IA ligada → B-roll gráfico
  (cartão animado com o termo, custo zero).
- **Mecanismo e stack:** tela/motion — itens entrando um a um com preço, soma riscada, preço final grande
  ("De US$ 297 / por US$ 97"), ding no momento do preço.
- **Ecossistema:** dois cartões (Kit Empresa Completa · Contractors ↔ Subs), "Quando você entrar, explora."
- **Prova:** números validados grandes + prints reais (`assets/provas/*.png|jpg`) + nomes dos depoimentos
  (com cidade, quando o `produtos.json` tiver).
- **Payback:** a conta em linhas + "Base: …" + "Não é promessa de renda".
- **Qualificação:** lista "Não é pra você se…" com X vermelho.

## Ritmo (automático no Motor A)
- **Corte a cada 2–4s:** silêncio e erro saem; nas frases longas, a máquina alterna o zoom (1.0 → 1.12 →
  1.22) a cada ~3s, o que funciona como corte.
- **Zoom punch-in** rápido (5 frames) nas viradas de frase.
- **SFX discreto:** whoosh na entrada de cada bloco e de cada B-roll; pop no texto animado; ding no preço.
  Volume baixo (0.25–0.45). Kit em `assets/sfx/index.json`.
- **Música** baixa sob a fala (se houver arquivo em `assets/musica/`), com loudness final em -14 LUFS.
- **Legenda** palavra por palavra, branca com a palavra falada em amarelo, centralizada embaixo (3 palavras
  por tela). Números e palavras da marca ficam amarelos.

## Gravação (o que pedir pro Rafael)
- Celular na vertical (anúncio) ou horizontal (página), altura dos olhos, apoiado.
- Peito pra cima, camiseta preta, fundo limpo, luz de frente.
- Um arquivo por bloco, com o nome do roteiro (`01-hook.mp4`…).
- Errou → fala "corta", respira, repete a frase inteira. Pausas podem ficar: a máquina corta.
