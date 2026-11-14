# Declaração de uso de IA

## Ferramenta e modelo

- **Ferramenta:** Claude Code (app desktop, aba Code)
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Sessão:** `entrega/uso-de-ia/sessao.md`

## O que a IA fez

- Leu o enunciado, o código e os testes, e preparou o ambiente (`.venv`, dependências de `requirements-dev.txt`).
- Rodou o baseline (`pytest` e o CLI na amostra e no dataset completo) e perfilou o CSV de reservas.
- Identificou os 5 defeitos, explicou a causa de cada um e propôs as correções.
- Aplicou as correções e o ajuste do código de saída para moeda sem taxa.
- Escreveu os 13 casos de teste adicionais e confirmou que 9 deles falham no código original.

## O que eu fiz

- Conduzi a sessão: defini a ordem do trabalho (diagnóstico, explicação, correção, testes, repositório, entrega).
- Pedi a explicação de cada mudança (arquivo, linha e motivo) antes de autorizar a aplicação.
- Validei cada parte: correções, testes e documentos de entrega.
- Tirei dúvidas sobre o que a IA fez e sobre detalhes do Python usados na solução.
- Questionei a solução do ranking, comparei as alternativas e escolhi a abordagem final.
- Questionei a quantidade e a organização dos testes e pedi ajustes.
