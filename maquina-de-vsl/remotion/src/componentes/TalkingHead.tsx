import React from "react";
import { AbsoluteFill, OffthreadVideo, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import type { Zoom } from "../tipos";

/** Vídeo do Rafael com punch-in de zoom nos tempos do plano de efeitos. */
export const escalaNoTempo = (zooms: Zoom[], t: number, fps: number) => {
  let escala = 1;
  let anterior = 1;
  let inicio = -1;
  for (const z of zooms) {
    if (z.t <= t) {
      anterior = escala;
      escala = z.escala;
      inicio = z.t;
    }
  }
  if (inicio < 0) return 1;
  const dur = 5 / fps; // punch-in rápido (~5 frames)
  const p = interpolate(t - inicio, [0, dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return anterior + (escala - anterior) * p;
};

export const TalkingHead: React.FC<{ src: string; zooms: Zoom[]; mudo?: boolean }> = ({ src, zooms, mudo }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const escala = escalaNoTempo(zooms, frame / fps, fps);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <AbsoluteFill style={{ transform: `scale(${escala})`, transformOrigin: "50% 38%" }}>
        <OffthreadVideo src={src} muted={mudo} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Rafael em círculo no canto, usado por cima das telas (oferta, prova...). */
export const Pip: React.FC<{ src: string; borda: string }> = ({ src, borda }) => {
  const { width, height } = useVideoConfig();
  const vertical = height > width;
  const lado = vertical ? width * 0.3 : height * 0.3;
  return (
    <div
      style={{
        position: "absolute",
        right: vertical ? (width - lado) / 2 : width * 0.03,
        top: vertical ? height * 0.04 : undefined,
        bottom: vertical ? undefined : height * 0.05,
        width: lado,
        height: lado,
        borderRadius: "50%",
        overflow: "hidden",
        border: `${Math.round(lado * 0.025)}px solid ${borda}`,
        boxShadow: "0 10px 40px rgba(0,0,0,0.5)",
      }}
    >
      <OffthreadVideo src={src} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 25%" }} />
    </div>
  );
};
