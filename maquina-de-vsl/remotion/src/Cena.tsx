import React from "react";
import { AbsoluteFill, Audio, Sequence, useVideoConfig } from "remotion";
import type { PropsCena } from "./tipos";
import { fundoVerde } from "./estilo";
import { Legenda } from "./componentes/Legenda";
import { Pip, TalkingHead } from "./componentes/TalkingHead";
import { Brolls, Efeitos, LowerThird, Textos } from "./componentes/Sobreposicoes";
import { BotaoCta, SeloGarantia, TelaCheia } from "./telas/Telas";

/**
 * Uma cena da VSL. Cada bloco do roteiro vira uma cena renderizada separadamente
 * (é isso que permite refazer "só o que mudou").
 *  - modo "fala":   talking-head do Rafael + zooms + texto animado + B-roll + legenda
 *  - modo "cartao": talking-head + selo/botão por cima (garantia, CTA)
 *  - modo "tela":   tela de motion (oferta, prova, ecossistema...) + Rafael em PiP + legenda
 */
export const Cena: React.FC<PropsCena> = (p) => {
  const { fps } = useVideoConfig();
  const tela = p.tela;
  return (
    <AbsoluteFill style={{ background: fundoVerde(p.cores) }}>
      {p.modo === "tela" ? (
        <>
          <TelaCheia tela={tela} cores={p.cores} />
          {p.video ? <Pip src={p.video} borda={p.cores.dourado} /> : null}
        </>
      ) : p.video ? (
        <>
          <TalkingHead src={p.video} zooms={p.zooms} />
          <Brolls brolls={p.brolls} cores={p.cores} />
          <Textos textos={p.textos} cores={p.cores} />
        </>
      ) : null}

      {p.modo === "cartao" && tela.tipo === "garantia" ? <SeloGarantia dias={tela.dias} texto={tela.texto} cores={p.cores} /> : null}
      {p.modo === "cartao" && tela.tipo === "cta" ? <BotaoCta botao={tela.botao} sub={tela.sub} cores={p.cores} /> : null}

      {p.lowerThird ? (
        <Sequence from={Math.round(0.4 * fps)} durationInFrames={Math.round(3.6 * fps)}>
          <LowerThird nome={p.lowerThird.nome} cargo={p.lowerThird.cargo} cores={p.cores} />
        </Sequence>
      ) : null}

      <Legenda palavras={p.palavras} cores={p.cores} porTela={p.palavrasPorTela} />
      <Efeitos sfx={p.sfx} />
      {p.musica ? <Audio src={p.musica} volume={0.06} loop /> : null}
    </AbsoluteFill>
  );
};
