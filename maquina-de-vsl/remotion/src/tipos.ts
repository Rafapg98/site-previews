export type Palavra = { w: string; ini: number; fim: number; destaque?: boolean };

export type Zoom = { t: number; escala: number };
export type TextoAnimado = { t: number; dur: number; texto: string };
export type Sfx = { t: number; src: string; volume: number };
export type Broll = {
  t: number;
  dur: number;
  termo: string;
  fonte: "grafico" | "real" | "ia";
  src?: string;
  legenda?: string;
};

export type Cores = {
  verde_profundo: string;
  verde: string;
  verde_claro: string;
  dourado: string;
  dourado_claro: string;
  dourado_escuro: string;
  branco: string;
  destaque_legenda: string;
  vermelho_risco: string;
};

export type ItemStack = { item: string; valor?: number; valorTexto?: string };

export type Tela =
  | { tipo: "nenhuma" }
  | {
      tipo: "oferta";
      titulo: string;
      itens: ItemStack[];
      somaTexto: string;
      deTexto: string;
      porTexto: string;
      bonus: string[];
      rodape: string;
    }
  | { tipo: "ecossistema"; titulo: string; cartoes: { titulo: string; texto: string; selo?: string }[]; rodape: string }
  | { tipo: "prova"; titulo: string; numeros: { valor: string; texto: string }[]; nomes: string[]; prints: string[] }
  | { tipo: "lista"; titulo: string; itens: string[]; estilo: "check" | "x" }
  | { tipo: "payback"; titulo: string; linhas: { rotulo: string; valor: string }[]; base: string; aviso: string }
  | { tipo: "garantia"; dias: number; texto: string }
  | { tipo: "cta"; botao: string; sub: string };

export type PropsCena = {
  largura: number;
  altura: number;
  fps: number;
  duracaoFrames: number;
  modo: "fala" | "tela" | "cartao";
  video: string | null;
  palavras: Palavra[];
  zooms: Zoom[];
  textos: TextoAnimado[];
  sfx: Sfx[];
  brolls: Broll[];
  tela: Tela;
  cores: Cores;
  lowerThird: { nome: string; cargo: string } | null;
  assinatura: string;
  palavrasPorTela: number;
  musica?: string | null;
};
