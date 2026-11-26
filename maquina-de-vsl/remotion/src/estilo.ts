import "@fontsource/montserrat/600.css";
import "@fontsource/montserrat/800.css";
import "@fontsource/montserrat/900.css";
import type { Cores } from "./tipos";

export const FONTE = "Montserrat, sans-serif";

export const ouro = (c: Cores) =>
  `linear-gradient(180deg, ${c.dourado_claro} 0%, ${c.dourado} 48%, ${c.dourado_escuro} 100%)`;

export const textoOuro = (c: Cores): React.CSSProperties => ({
  background: ouro(c),
  WebkitBackgroundClip: "text",
  backgroundClip: "text",
  color: "transparent",
});

export const fundoVerde = (c: Cores) =>
  `radial-gradient(ellipse at 50% 30%, ${c.verde_claro} 0%, ${c.verde} 45%, ${c.verde_profundo} 100%)`;

export const CORES_PADRAO: Cores = {
  verde_profundo: "#06180F",
  verde: "#0B2A1F",
  verde_claro: "#14432F",
  dourado: "#C9A24B",
  dourado_claro: "#F3D98B",
  dourado_escuro: "#8C6A22",
  branco: "#FFFFFF",
  destaque_legenda: "#FFD43B",
  vermelho_risco: "#E0483E",
};

/** Unidade relativa: 1u = 1% do menor lado do quadro. */
export const unidade = (largura: number, altura: number) => Math.min(largura, altura) / 100;
