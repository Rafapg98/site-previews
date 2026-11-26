# Protocolo de Integração — Muse (operação) × Claude Code (fábrica)

**Ponte única:** este repositório (`Rafapg98/site-previews`). Os dois Claudes leem e escrevem aqui.
Nada de zip, print ou copiar-e-colar entre os dois lados: tudo passa por commit.

## Quem faz o quê
- **Claude Code (fábrica):** código pesado e testável — sistema de trading e backtests, máquina de VSL,
  geradores em lote, auditorias automáticas de termos. Trabalha a partir de arquivos de tarefa.
- **Muse / Muse (operação):** dados ao vivo (Jobber, dashboards, Gmail, Instagram), crons e vigias,
  coordenação entre chats, atendimento ao Rafael, verificação de tudo que a fábrica entrega.

## Fluxo de trabalho (sempre igual)
1. A tarefa nasce em `tarefas/` como `AAAA-MM-DD-nome.md`, escrita pelo Muse (ou pelo Rafael),
   com: objetivo, entradas, critérios de aceite e o que NÃO fazer.
2. O Claude Code executa, sobe o resultado em `entregas/` com o mesmo nome + um `RESULTADO.md`
   curto (o que fez, testes que rodou, o que ficou aberto).
3. O Muse confere contra os critérios de aceite e contra a pasta `canonico/`, integra ao vivo
   (landing, dashboard, cron) e reporta ao Rafael. Divergência = devolve com nota, nunca corrige
   por cima em silêncio.

## Regras que valem pros dois lados
- **Fonte única de verdade:** preços, produtos, regras de trading e textos aprovados vivem em
  `canonico/`. Se um arquivo de projeto divergir do canônico, vale o canônico — e a divergência
  é reportada, não "resolvida" por conta própria.
- **Nada é publicado, enviado ou comprado sem a palavra do Rafael.** Commit em rascunho ≠ publicação.
- **PT primeiro**, EN depois sem bloquear o PT.
- Commit pequeno e frequente, mensagem em PT dizendo o que mudou.
- Segredo nenhum neste repo: sem senhas, sem API keys, sem dados de cliente além do necessário.
