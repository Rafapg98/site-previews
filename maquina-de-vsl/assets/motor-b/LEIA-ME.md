# Motor B — arquivos-base (ficam só no seu computador, fora do git)

- `foto-base.jpg` — foto do avatar (tirada da gravação-base, de frente, boca fechada)
- `voz-clone.wav` — áudio limpo (60–90s) para o clone instantâneo no ElevenLabs
- `analise/` — laudo dos vídeos analisados

Mesmo com tudo pronto, o Motor B só roda numa VSL quando você disser **"usa o motor B nesta VSL"**,
e só depois de ver e aprovar o custo.

## Laudo da VSL antiga (vsl-web.mp4), 2026-11-26 — NÃO SERVE
- **Voz:** existe uma trilha/ambiente contínuo por baixo da fala. Mesmo nas pausas entre palavras, o som nunca
  cai abaixo de cerca de −33 dB (gravação limpa fica abaixo de −50 dB), e no fim do vídeo a trilha aparece
  sozinha, com notas graves. Clonar com isso deixa ruído e "música" grudados na voz.
- **Vídeo:** a edição tem corte a cada 2–4 s. O maior trecho seguido com você de frente, sem legenda nem
  gráfico (recortando a legenda e os painéis), tem **23 s** (66,9 s → 90,0 s). Nenhum trecho chega a 30 s.
- **Qualidade:** 720p a ~400 kbps. Depois do recorte que tira a legenda e os painéis, o rosto fica com
  ~200 px de largura, pouco para um avatar nítido.
- Trecho de referência salvo em `analise/melhor-trecho-66s-90s.mp4`.
