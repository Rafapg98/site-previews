import React from "react";
import { Composition } from "remotion";
import { Cena } from "./Cena";
import type { PropsCena } from "./tipos";
import { CORES_PADRAO } from "./estilo";
import { Legenda } from "./componentes/Legenda";
import { LowerThird } from "./componentes/Sobreposicoes";
import { TelaCheia } from "./telas/Telas";

const base: PropsCena = {
  largura: 1920,
  altura: 1080,
  fps: 30,
  duracaoFrames: 240,
  modo: "tela",
  video: null,
  palavras: [
    { w: "Empresa", ini: 0.2, fim: 0.6 },
    { w: "de", ini: 0.6, fim: 0.75 },
    { w: "verdade,", ini: 0.75, fim: 1.3, destaque: true },
    { w: "sem", ini: 1.5, fim: 1.8 },
    { w: "guru.", ini: 1.8, fim: 2.4 },
  ],
  zooms: [],
  textos: [],
  sfx: [],
  brolls: [],
  tela: {
    tipo: "oferta",
    titulo: "O que você leva hoje",
    itens: [{ item: "Curso completo Da Diária ao Subcontractor", valorTexto: "US$ 297" }],
    somaTexto: "Total: US$ 297",
    deTexto: "De US$ 297",
    porTexto: "por US$ 97",
    bonus: ["1º mês do plano Starter grátis"],
    rodape: "Depois, US$ 9,90/mês se ficar. Garantia de 7 dias.",
  },
  cores: CORES_PADRAO,
  lowerThird: null,
  assinatura: "Empresa de verdade, sem guru.",
  palavrasPorTela: 3,
};

const metadados = ({ props }: { props: PropsCena }) => ({
  durationInFrames: Math.max(1, props.duracaoFrames),
  width: props.largura,
  height: props.altura,
  fps: props.fps,
});

export const Raiz: React.FC = () => (
  <>
    {/* Composições usadas pela máquina (as dimensões vêm das props). */}
    <Composition id="Cena169" component={Cena} defaultProps={base} calculateMetadata={metadados} width={1920} height={1080} fps={30} durationInFrames={240} />
    <Composition
      id="Cena916"
      component={Cena}
      defaultProps={{ ...base, largura: 1080, altura: 1920 }}
      calculateMetadata={metadados}
      width={1080}
      height={1920}
      fps={30}
      durationInFrames={240}
    />
    {/* Peças avulsas para conferir no Remotion Studio. */}
    <Composition
      id="Legenda"
      component={() => <Legenda palavras={base.palavras} cores={CORES_PADRAO} porTela={3} />}
      width={1080}
      height={1920}
      fps={30}
      durationInFrames={90}
    />
    <Composition
      id="LowerThird"
      component={() => <LowerThird nome="Rafael Porfirio" cargo="Dono da RP Renovations · Tampa Bay, FL" cores={CORES_PADRAO} />}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={120}
    />
    <Composition
      id="TelaOferta"
      component={() => <TelaCheia tela={base.tela} cores={CORES_PADRAO} />}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={240}
    />
  </>
);
