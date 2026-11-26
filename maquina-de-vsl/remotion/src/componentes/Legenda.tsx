import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from "remotion";
import type { Cores, Palavra } from "../tipos";
import { FONTE, unidade } from "../estilo";

type Bloco = { palavras: Palavra[]; ini: number; fim: number };

/** Agrupa palavras em telas de até N palavras, quebrando em pausa ou pontuação. */
export const agrupar = (palavras: Palavra[], n: number): Bloco[] => {
  const blocos: Bloco[] = [];
  let atual: Palavra[] = [];
  const fechar = () => {
    if (atual.length) {
      blocos.push({ palavras: atual, ini: atual[0].ini, fim: atual[atual.length - 1].fim });
      atual = [];
    }
  };
  palavras.forEach((p, i) => {
    const anterior = palavras[i - 1];
    if (anterior && (p.ini - anterior.fim > 0.4 || /[.!?…]$/.test(anterior.w))) fechar();
    atual.push(p);
    if (atual.length >= n) fechar();
  });
  fechar();
  // estica cada tela até a próxima (sem buraco curto), limitado a +0.5s
  blocos.forEach((b, i) => {
    const prox = blocos[i + 1];
    b.fim = prox ? Math.min(prox.ini, b.fim + 0.5) : b.fim + 0.5;
  });
  return blocos;
};

export const Legenda: React.FC<{ palavras: Palavra[]; cores: Cores; porTela: number; subir?: boolean }> = ({
  palavras,
  cores,
  porTela,
  subir,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const u = unidade(width, height);
  const vertical = height > width;
  const blocos = React.useMemo(() => agrupar(palavras, porTela), [palavras, porTela]);
  const bloco = blocos.find((b) => t >= b.ini && t < b.fim);
  if (!bloco) return null;

  const tamanho = vertical ? 7.4 * u : 5.6 * u;
  const baixo = vertical ? (subir ? 30 : 22) : subir ? 16 : 9;

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", pointerEvents: "none" }}>
      <div
        style={{
          marginBottom: `${baixo}%`,
          maxWidth: "86%",
          textAlign: "center",
          fontFamily: FONTE,
          fontWeight: 800,
          fontSize: tamanho,
          lineHeight: 1.15,
          letterSpacing: -0.5,
        }}
      >
        {bloco.palavras.map((p, i) => {
          const ativa = t >= p.ini && t < (bloco.palavras[i + 1]?.ini ?? bloco.fim);
          const entrou = spring({ frame: frame - Math.round(p.ini * fps), fps, config: { damping: 14, mass: 0.5 } });
          const cor = ativa || p.destaque ? cores.destaque_legenda : cores.branco;
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                margin: `0 ${0.18 * tamanho}px`,
                color: cor,
                transform: `scale(${ativa ? 1 + 0.08 * entrou : 1})`,
                WebkitTextStroke: `${Math.max(2, tamanho * 0.06)}px rgba(0,0,0,0.85)`,
                paintOrder: "stroke fill",
                textShadow: "0 4px 14px rgba(0,0,0,0.55)",
              }}
            >
              {p.w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
