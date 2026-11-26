import React from "react";
import {
  AbsoluteFill,
  Audio,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { Broll, Cores, Sfx, TextoAnimado } from "../tipos";
import { FONTE, fundoVerde, ouro, textoOuro, unidade } from "../estilo";

/** Lower-third com nome e cargo. */
export const LowerThird: React.FC<{ nome: string; cargo: string; cores: Cores }> = ({ nome, cargo, cores }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const u = unidade(width, height);
  const vertical = height > width;
  const entra = spring({ frame, fps, config: { damping: 18 } });
  const sai = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], { extrapolateLeft: "clamp" });
  const x = interpolate(entra, [0, 1], [-60, 0]);
  return (
    <AbsoluteFill style={{ justifyContent: vertical ? "flex-start" : "flex-end", padding: vertical ? "16% 6%" : "0 4% 24%" }}>
      <div style={{ transform: `translateX(${x}%)`, opacity: sai, fontFamily: FONTE, display: "inline-block" }}>
        <div style={{ height: 0.6 * u, width: 14 * u, background: ouro(cores), marginBottom: 1.2 * u }} />
        <div style={{ fontWeight: 900, fontSize: (vertical ? 6 : 4.4) * u, color: cores.branco, textShadow: "0 3px 12px rgba(0,0,0,.6)" }}>
          {nome}
        </div>
        <div style={{ fontWeight: 600, fontSize: (vertical ? 3.4 : 2.4) * u, ...textoOuro(cores), marginTop: 0.4 * u }}>{cargo}</div>
      </div>
    </AbsoluteFill>
  );
};

/** Palavra-chave grande que "salta" na tela (texto animado). */
export const TextoPop: React.FC<{ texto: string; cores: Cores }> = ({ texto, cores }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const u = unidade(width, height);
  const vertical = height > width;
  const s = spring({ frame, fps, config: { damping: 9, mass: 0.6 } });
  const sai = interpolate(frame, [durationInFrames - 6, durationInFrames], [1, 0], { extrapolateLeft: "clamp" });
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: vertical ? "56%" : "7%" }}>
      <div
        style={{
          transform: `scale(${0.6 + 0.4 * s}) rotate(${(1 - s) * -4}deg)`,
          opacity: sai,
          fontFamily: FONTE,
          fontWeight: 900,
          fontSize: (vertical ? 10 : 8) * u,
          textTransform: "uppercase",
          padding: `${0.6 * u}px ${2.2 * u}px`,
          background: cores.verde_profundo + "E6",
          border: `${0.5 * u}px solid ${cores.dourado}`,
          borderRadius: 1.6 * u,
          boxShadow: "0 12px 40px rgba(0,0,0,.5)",
        }}
      >
        <span style={textoOuro(cores)}>{texto}</span>
      </div>
    </AbsoluteFill>
  );
};

/** B-roll gráfico (custo zero): cartão animado com o termo citado. */
export const BrollGrafico: React.FC<{ termo: string; legenda?: string; cores: Cores }> = ({ termo, legenda, cores }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const u = unidade(width, height);
  const entra = spring({ frame, fps, config: { damping: 16 } });
  const zoom = interpolate(frame, [0, durationInFrames], [1.08, 1]);
  const linhas = Array.from({ length: 9 });
  return (
    <AbsoluteFill style={{ background: fundoVerde(cores), transform: `scale(${zoom})` }}>
      {linhas.map((_, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: `${-20 + i * 16 + ((frame * 0.6) % 16)}%`,
            top: 0,
            bottom: 0,
            width: 2,
            background: cores.dourado + "22",
            transform: "skewX(-18deg)",
          }}
        />
      ))}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", fontFamily: FONTE, textAlign: "center" }}>
        <div style={{ transform: `translateY(${(1 - entra) * 8 * u}px)`, opacity: entra }}>
          <div style={{ fontWeight: 900, fontSize: 13 * u, letterSpacing: -1, ...textoOuro(cores) }}>{termo}</div>
          {legenda ? (
            <div style={{ fontWeight: 600, fontSize: 3.6 * u, color: cores.branco, opacity: 0.85, marginTop: 1.5 * u }}>{legenda}</div>
          ) : null}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Brolls: React.FC<{ brolls: Broll[]; cores: Cores }> = ({ brolls, cores }) => {
  const { fps } = useVideoConfig();
  return (
    <>
      {brolls.map((b, i) => (
        <Sequence key={i} from={Math.round(b.t * fps)} durationInFrames={Math.max(1, Math.round(b.dur * fps))}>
          {b.fonte !== "grafico" && b.src ? (
            <AbsoluteFill>
              <OffthreadVideo src={b.src} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            </AbsoluteFill>
          ) : (
            <BrollGrafico termo={b.termo} legenda={b.legenda} cores={cores} />
          )}
        </Sequence>
      ))}
    </>
  );
};

export const Textos: React.FC<{ textos: TextoAnimado[]; cores: Cores }> = ({ textos, cores }) => {
  const { fps } = useVideoConfig();
  return (
    <>
      {textos.map((x, i) => (
        <Sequence key={i} from={Math.round(x.t * fps)} durationInFrames={Math.max(1, Math.round(x.dur * fps))}>
          <TextoPop texto={x.texto} cores={cores} />
        </Sequence>
      ))}
    </>
  );
};

export const Efeitos: React.FC<{ sfx: Sfx[] }> = ({ sfx }) => {
  const { fps } = useVideoConfig();
  return (
    <>
      {sfx.map((s, i) => (
        <Sequence key={i} from={Math.max(0, Math.round(s.t * fps))}>
          <Audio src={s.src} volume={s.volume} />
        </Sequence>
      ))}
    </>
  );
};
