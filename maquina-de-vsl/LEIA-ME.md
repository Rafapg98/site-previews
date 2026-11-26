# Máquina de VSL — guia rápido do Rafael

Seu estúdio de VSL dentro do Claude Code. Você fala, ele edita.

## Como abrir
1. Abra o Claude Code **dentro desta pasta** (`maquina-de-vsl`).
2. Primeira vez: digite **`/comecar`** — ele confere o computador, instala o que faltar, confirma a sua marca
   e faz um teste de 20 segundos com uma gravação sua.
3. Para fazer uma VSL: digite **`/vsl`**.

## Como funciona uma VSL
1. Você diz o produto (curso, Kit ou Mentoria) e o formato (página 16:9 ou anúncio 9:16).
2. O Claude te mostra o **roteiro** inteiro, bloco a bloco. Nada anda sem o seu **"aprovado"**.
3. Ele mostra o **custo** antes de gastar qualquer coisa (gravando você mesmo = **US$ 0**).
4. Você grava cada bloco no celular e joga em `entrada/<nome-da-vsl>/` com o nome que ele passar
   (`01-hook.mp4`, `02-historia.mp4`…). Errou? Fala **"corta"** e repete a frase. Pausas podem ficar.
5. Ele monta o **preview** (`projetos/<nome>/preview/`). Você assiste e pede ajuste falando:
   "testa outro começo", "muda o preço", "legenda maior". Ele refaz **só o que mudou**.
6. **Final** em `projetos/<nome>/final/<produto>-vsl-v1.mp4`. Nada é publicado: você sobe onde quiser.

## As regras que a máquina segue sempre
- **Seu rosto e sua voz são reais.** Avatar/voz clonada (Motor B) só se você disser
  "usa o motor B nesta VSL" — e só naquela VSL.
- Preço, prova e números só do `config/produtos.json`. Nada de promessa de renda ou de lead garantido.
- Chaves (ElevenLabs/fal.ai) ficam só no arquivo `config/chaves.env` no seu computador — **nunca cole
  chave no chat**.
- PT primeiro; inglês entra como **legenda** no mesmo vídeo.

## Onde mexer, se quiser
- Preço/oferta/provas: `config/produtos.json`
- Cores, legenda, nome no lower-third: `config/marca.json`
- Música de fundo: um .mp3 livre de direitos em `assets/musica/`
- Vídeos reais das suas obras (B-roll): `assets/broll-real/` (ex.: `obra-cozinha.mp4`)
- Prints de avaliação: `assets/provas/`
