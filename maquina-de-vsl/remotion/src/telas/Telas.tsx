import React from "react";
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { Cores, Tela } from "../tipos";
import { FONTE, fundoVerde, ouro, textoOuro, unidade } from "../estilo";

const useTempo = () => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const u = unidade(width, height);
  const vertical = height > width;
  /** progresso 0..1 de um elemento que entra na fração `f` da cena */
  const entra = (f: number) => spring({ frame: frame - Math.round(f * durationInFrames), fps, config: { damping: 15, mass: 0.7 } });
  return { frame, fps, u, vertical, entra, durationInFrames, width, height };
};

const Moldura: React.FC<{ cores: Cores; children: React.ReactNode }> = ({ cores, children }) => {
  const { u, vertical } = useTempo();
  return (
    <AbsoluteFill style={{ background: fundoVerde(cores), fontFamily: FONTE, color: cores.branco }}>
      <div style={{ position: "absolute", inset: 2 * u, border: `${0.3 * u}px solid ${cores.dourado}55`, borderRadius: 2 * u }} />
      <AbsoluteFill
        style={{
          padding: vertical ? `${43 * u}px ${7 * u}px ${48 * u}px` : `${7 * u}px ${36 * u}px ${18 * u}px ${9 * u}px`,
          justifyContent: vertical ? "flex-start" : "center",
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Titulo: React.FC<{ texto: string; cores: Cores }> = ({ texto, cores }) => {
  const { u, entra, vertical } = useTempo();
  const p = entra(0);
  return (
    <div style={{ opacity: p, transform: `translateY(${(1 - p) * 3 * u}px)`, marginBottom: 3 * u }}>
      <div style={{ fontWeight: 900, fontSize: (vertical ? 6.4 : 5.4) * u, lineHeight: 1.05, ...textoOuro(cores) }}>{texto}</div>
      <div style={{ height: 0.5 * u, width: 12 * u, background: ouro(cores), marginTop: 1.4 * u }} />
    </div>
  );
};

const Oferta: React.FC<{ t: Extract<Tela, { tipo: "oferta" }>; cores: Cores }> = ({ t, cores }) => {
  const { u, entra, vertical, frame, durationInFrames } = useTempo();
  const n = Math.max(1, t.itens.length);
  const fs = (vertical ? 3.9 : 3.1) * u;
  const risco = interpolate(frame, [0.5 * durationInFrames, 0.5 * durationInFrames + 12], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const preco = entra(0.58);
  return (
    <Moldura cores={cores}>
      <Titulo texto={t.titulo} cores={cores} />
      {t.itens.map((it, i) => {
        const p = entra(0.08 + (i * 0.36) / n);
        return (
          <div
            key={i}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "baseline",
              gap: 2 * u,
              fontSize: fs,
              fontWeight: 600,
              padding: `${1.1 * u}px 0`,
              borderBottom: `1px solid ${cores.dourado}33`,
              opacity: p,
              transform: `translateX(${(1 - p) * -6 * u}px)`,
            }}
          >
            <span>✓ {it.item}</span>
            <span style={{ fontWeight: 800, color: cores.dourado_claro, whiteSpace: "nowrap" }}>{it.valorTexto}</span>
          </div>
        );
      })}
      {t.itens.length > 1 ? (
      <div style={{ marginTop: 2.4 * u, fontSize: fs * 1.1, fontWeight: 800, opacity: entra(0.46), position: "relative", alignSelf: "flex-start" }}>
        <span>{t.somaTexto}</span>
        <div
          style={{
            position: "absolute",
            left: 0,
            top: "52%",
            height: 0.55 * u,
            width: `${risco}%`,
            background: cores.vermelho_risco,
            transform: "rotate(-3deg)",
          }}
        />
      </div>
      ) : null}
      <div style={{ marginTop: 2.2 * u, opacity: preco, transform: `scale(${0.7 + 0.3 * preco})`, transformOrigin: "left center", alignSelf: "flex-start" }}>
        <div style={{ fontSize: fs * 1.05, fontWeight: 600 }}>
          <span style={{ textDecoration: "line-through", textDecorationColor: cores.vermelho_risco, opacity: 0.8 }}>{t.deTexto}</span>
        </div>
        <div style={{ fontSize: (vertical ? 13 : 10.5) * u, fontWeight: 900, lineHeight: 1, ...textoOuro(cores) }}>{t.porTexto}</div>
      </div>
      {t.bonus.map((b, i) => (
        <div key={i} style={{ marginTop: 1.4 * u, fontSize: fs * 0.92, fontWeight: 800, color: cores.destaque_legenda, opacity: entra(0.7 + i * 0.05) }}>
          + BÔNUS: {b}
        </div>
      ))}
      <div style={{ marginTop: 1.6 * u, fontSize: fs * 0.72, opacity: 0.8 * entra(0.78) }}>{t.rodape}</div>
    </Moldura>
  );
};

const Ecossistema: React.FC<{ t: Extract<Tela, { tipo: "ecossistema" }>; cores: Cores }> = ({ t, cores }) => {
  const { u, entra, vertical } = useTempo();
  return (
    <Moldura cores={cores}>
      <Titulo texto={t.titulo} cores={cores} />
      <div style={{ display: "flex", flexDirection: vertical ? "column" : "row", gap: 2.4 * u }}>
        {t.cartoes.map((c, i) => {
          const p = entra(0.15 + i * 0.2);
          return (
            <div
              key={i}
              style={{
                flex: 1,
                padding: 2.6 * u,
                borderRadius: 2 * u,
                background: "rgba(0,0,0,.28)",
                border: `${0.3 * u}px solid ${cores.dourado}`,
                opacity: p,
                transform: `translateY(${(1 - p) * 5 * u}px)`,
              }}
            >
              {c.selo ? (
                <div style={{ display: "inline-block", fontSize: 2.2 * u, fontWeight: 800, padding: `${0.4 * u}px ${1.2 * u}px`, borderRadius: u, background: ouro(cores), color: cores.verde_profundo, marginBottom: 1.4 * u }}>
                  {c.selo}
                </div>
              ) : null}
              <div style={{ fontSize: (vertical ? 5 : 4) * u, fontWeight: 900, ...textoOuro(cores) }}>{c.titulo}</div>
              <div style={{ fontSize: (vertical ? 3.4 : 2.7) * u, fontWeight: 600, marginTop: 1.2 * u, lineHeight: 1.3 }}>{c.texto}</div>
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 3 * u, fontSize: (vertical ? 3.4 : 2.8) * u, fontWeight: 800, color: cores.destaque_legenda, opacity: entra(0.6) }}>{t.rodape}</div>
    </Moldura>
  );
};

const Prova: React.FC<{ t: Extract<Tela, { tipo: "prova" }>; cores: Cores }> = ({ t, cores }) => {
  const { u, entra, vertical } = useTempo();
  return (
    <Moldura cores={cores}>
      <Titulo texto={t.titulo} cores={cores} />
      <div style={{ display: "flex", flexDirection: vertical ? "column" : "row", gap: 2 * u }}>
        {t.numeros.map((n, i) => {
          const p = entra(0.1 + i * 0.14);
          return (
            <div key={i} style={{ flex: 1, opacity: p, transform: `scale(${0.8 + 0.2 * p})`, padding: 2 * u, borderRadius: 1.6 * u, background: "rgba(0,0,0,.25)", border: `${0.25 * u}px solid ${cores.dourado}88` }}>
              <div style={{ fontSize: (vertical ? 9 : 7) * u, fontWeight: 900, lineHeight: 1, ...textoOuro(cores) }}>{n.valor}</div>
              <div style={{ fontSize: (vertical ? 3.2 : 2.4) * u, fontWeight: 600, marginTop: u }}>{n.texto}</div>
            </div>
          );
        })}
      </div>
      {t.prints.length ? (
        <div style={{ display: "flex", gap: 1.5 * u, marginTop: 2.5 * u, opacity: entra(0.5) }}>
          {t.prints.slice(0, 3).map((p, i) => (
            <Img key={i} src={p} style={{ height: (vertical ? 22 : 16) * u, borderRadius: u, border: `${0.2 * u}px solid ${cores.dourado}` }} />
          ))}
        </div>
      ) : null}
      {t.nomes.length ? (
        <div style={{ marginTop: 2.8 * u, fontSize: (vertical ? 3.4 : 2.7) * u, fontWeight: 700, opacity: entra(0.6) }}>
          Quem já passou por aqui: <span style={{ color: cores.dourado_claro }}>{t.nomes.join(" · ")}</span>
        </div>
      ) : null}
    </Moldura>
  );
};

const Lista: React.FC<{ t: Extract<Tela, { tipo: "lista" }>; cores: Cores }> = ({ t, cores }) => {
  const { u, entra, vertical } = useTempo();
  return (
    <Moldura cores={cores}>
      <Titulo texto={t.titulo} cores={cores} />
      {t.itens.map((it, i) => {
        const p = entra(0.1 + (i * 0.5) / Math.max(1, t.itens.length));
        return (
          <div key={i} style={{ display: "flex", gap: 1.6 * u, alignItems: "flex-start", fontSize: (vertical ? 4.2 : 3.3) * u, fontWeight: 700, margin: `${1.2 * u}px 0`, opacity: p, transform: `translateX(${(1 - p) * -5 * u}px)` }}>
            <span style={{ color: t.estilo === "x" ? cores.vermelho_risco : cores.dourado_claro, fontWeight: 900 }}>{t.estilo === "x" ? "✕" : "✓"}</span>
            <span>{it}</span>
          </div>
        );
      })}
    </Moldura>
  );
};

const Payback: React.FC<{ t: Extract<Tela, { tipo: "payback" }>; cores: Cores }> = ({ t, cores }) => {
  const { u, entra, vertical } = useTempo();
  return (
    <Moldura cores={cores}>
      <Titulo texto={t.titulo} cores={cores} />
      {t.linhas.map((l, i) => {
        const p = entra(0.1 + i * 0.13);
        return (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", fontSize: (vertical ? 4.2 : 3.4) * u, fontWeight: 700, padding: `${1.2 * u}px 0`, borderBottom: `1px solid ${cores.dourado}33`, opacity: p }}>
            <span>{l.rotulo}</span>
            <span style={{ fontWeight: 900, ...textoOuro(cores) }}>{l.valor}</span>
          </div>
        );
      })}
      <div style={{ marginTop: 2.4 * u, fontSize: (vertical ? 3 : 2.3) * u, opacity: 0.85 * entra(0.55) }}>Base: {t.base}</div>
      <div style={{ marginTop: u, fontSize: (vertical ? 3 : 2.3) * u, fontWeight: 800, color: cores.destaque_legenda, opacity: entra(0.62) }}>{t.aviso}</div>
    </Moldura>
  );
};

/** Selo de garantia por cima do talking-head. */
export const SeloGarantia: React.FC<{ dias: number; texto: string; cores: Cores }> = ({ dias, texto, cores }) => {
  const { u, entra, vertical, frame } = useTempo();
  const p = entra(0.05);
  const lado = (vertical ? 34 : 26) * u;
  return (
    <AbsoluteFill style={{ alignItems: vertical ? "center" : "flex-end", justifyContent: "flex-start", padding: vertical ? `${18 * u}px 0` : `${6 * u}px ${6 * u}px` }}>
      <div
        style={{
          width: lado,
          height: lado,
          borderRadius: "50%",
          background: ouro(cores),
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: FONTE,
          color: cores.verde_profundo,
          transform: `scale(${p}) rotate(${Math.sin(frame / 20) * 3}deg)`,
          boxShadow: "0 14px 50px rgba(0,0,0,.55)",
          border: `${0.8 * u}px solid ${cores.verde_profundo}`,
          textAlign: "center",
        }}
      >
        <div style={{ fontSize: lado * 0.36, fontWeight: 900, lineHeight: 1 }}>{dias}</div>
        <div style={{ fontSize: lado * 0.1, fontWeight: 900 }}>DIAS DE GARANTIA</div>
        <div style={{ fontSize: lado * 0.07, fontWeight: 700, marginTop: lado * 0.02, maxWidth: "80%" }}>{texto}</div>
      </div>
    </AbsoluteFill>
  );
};

/** Botão de CTA por cima do talking-head. */
export const BotaoCta: React.FC<{ botao: string; sub: string; cores: Cores }> = ({ botao, sub, cores }) => {
  const { u, entra, vertical, frame } = useTempo();
  const p = entra(0.25);
  const pulso = 1 + Math.sin(frame / 6) * 0.025;
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: vertical ? "18%" : "5%", fontFamily: FONTE }}>
      <div style={{ opacity: p, transform: `scale(${(0.7 + 0.3 * p) * pulso})`, textAlign: "center" }}>
        <div style={{ padding: `${2 * u}px ${5 * u}px`, borderRadius: 2 * u, background: ouro(cores), color: cores.verde_profundo, fontWeight: 900, fontSize: (vertical ? 5.6 : 4.4) * u, boxShadow: "0 14px 50px rgba(0,0,0,.55)" }}>
          {botao} →
        </div>
        <div style={{ marginTop: 1.4 * u, color: cores.branco, fontWeight: 700, fontSize: (vertical ? 3.2 : 2.4) * u, textShadow: "0 2px 10px rgba(0,0,0,.8)" }}>{sub}</div>
      </div>
    </AbsoluteFill>
  );
};

export const TelaCheia: React.FC<{ tela: Tela; cores: Cores }> = ({ tela, cores }) => {
  switch (tela.tipo) {
    case "oferta":
      return <Oferta t={tela} cores={cores} />;
    case "ecossistema":
      return <Ecossistema t={tela} cores={cores} />;
    case "prova":
      return <Prova t={tela} cores={cores} />;
    case "lista":
      return <Lista t={tela} cores={cores} />;
    case "payback":
      return <Payback t={tela} cores={cores} />;
    default:
      return null;
  }
};
