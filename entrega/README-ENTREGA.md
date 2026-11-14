# Entrega — Consolidador de reservas Onfly

## Resumo

O CLI tinha 5 defeitos, que geravam números errados (noites negativas, câmbio invertido, NO_SHOW faturado,
ranking invertido e reservas descartadas). Todos foram corrigidos, um commit por defeito. Também ajustei o
código de saída para moeda sem taxa e adicionei 13 casos de teste.

- `pytest -q`: **18 passed** (5 fornecidos, sem alteração, + 13 novos)
- Amostra `data/exemplo-validacao.csv`: bate com a tabela do README em todos os campos
- `ruff check src tests`: sem erros

## Defeitos corrigidos

| # | Arquivo | Antes | Depois | Causa raiz |
|-|-|-|-|-|
| 1 | `repositories/csv_reservation_repository.py` | `if len(rows) == 200: break` | removido | A leitura parava na linha 200 e descartava sem aviso as demais reservas (o arquivo tem 300). |
| 2 | `services/status_policy.py` | `status != "CANCELLED"` | `status == "CONFIRMED"` | A regra excluía só CANCELLED, então NO_SHOW entrava em noites, valores, `by_month` e `top_hotels`. |
| 3 | `services/stay_calculator.py` | `(checkout.day - checkin.day) * rooms` | `(checkout - checkin).days * rooms` | Subtraía o dia do mês em vez das datas, gerando noites negativas na virada de mês/ano. |
| 4 | `services/currency_converter.py` | `Decimal(str(float(amount) / float(rate)))` | `amount * rate` | Dividia pela taxa em vez de multiplicar e passava por `float`, perdendo exatidão no dinheiro. |
| 5 | `services/report_builder.py` | `sorted(key=(amount, hotel_id))` | `sorted` por `hotel_id`, depois `sort` por valor com `reverse=True` | A ordenação era crescente por valor, então o ranking mostrava os hotéis de menor valor. |

Ajuste de contrato (não é defeito de número):

| # | Arquivo | Mudança | Motivo |
|-|-|-|-|
| 6 | `services/currency_converter.py` | Moeda sem taxa levanta `InputFileError` | Antes dava `KeyError` e saída `1`; pelo contrato, entrada inválida deve sair com `2`. |

Sobre o defeito 5: os dois critérios vão em sentidos opostos (valor decrescente, `hotel_id` crescente). Usei
duas ordenações aproveitando que o sort do Python é estável: primeiro por `hotel_id`, depois por valor com
`reverse=True`; no empate de valor, a ordem por `hotel_id` é preservada. Considerei também negar o valor na
chave (`-amount`) e `cmp_to_key`. Escolhi as duas ordenações por legibilidade e por não depender de o campo
aceitar negação. `reverse=True` sobre a chave original não serve, porque inverteria também o desempate.

## Como investiguei

1. **Leitura do enunciado:** extraí as regras (status, noites, câmbio, exatidão, ordenação) e o contrato do CLI.
2. **Baseline:** rodei `pytest -q` (5 falhas) e o CLI na amostra de validação e no dataset completo. Sinais:
   `total_room_nights: -33` na amostra, total em BRL menor que o esperado, ranking começando pelo menor valor
   e o resumo do dataset completo mostrando 200 reservas.
3. **Leitura do código seguindo o fluxo** `ler → converter tipos → contar status → filtrar CONFIRMED → agregar`,
   confrontando cada etapa com a regra correspondente. Cada falha de teste levou direto a uma função pequena.
4. **Verificação dos dados:** perfilei o `reservas_hoteis.csv` (300 linhas) para confirmar que o problema
   estava no CLI e não nos dados: não há espaços extras, ids duplicados, datas invertidas, campos multilinha
   nem hotel com nomes diferentes. Os status são só CONFIRMED/CANCELLED/NO_SHOW e as moedas só BRL/USD/EUR.
   Isso também revelou o truncamento: 300 linhas no arquivo contra 200 no relatório. Nenhum teste fornecido
   cobria esse defeito.
5. **Testes novos para os cenários fora dos testes fornecidos.** Confirmei que eles detectam os defeitos
   rodando-os contra o código original: 9 dos 13 falham. Os 4 que passam cobrem regras que o código original
   já respeitava e ficam como proteção contra regressão.
6. **Correções:** um commit por defeito, para facilitar a revisão (`git log --oneline`).

## Testes adicionados

Um arquivo por tema, como os testes fornecidos. Os nomes estão em inglês e as docstrings em português,
seguindo o padrão do projeto.

| Arquivo | O que cobre | Pega o defeito |
|-|-|-|
| `test_input_reading.py` | Mais de 200 linhas; dataset completo com 300 reservas e as chaves do schema | 1 |
| `test_status_breakdowns.py` | CANCELLED e NO_SHOW fora de `by_month` e `top_hotels`; só canceladas → média `"0.00"` e listas vazias | 2 |
| `test_year_boundary.py` | 30/12 a 02/01 = 3 noites, no mês do check-in | 3 |
| `test_rounding.py` | Half-up: `4.065 → "4.07"` (half-even daria `4.06`); soma exata: `1.355 + 1.355 → "2.71"` (por linha daria `2.72`) | 4 |
| `test_top_hotels_ranking.py` | Empate por `hotel_id` crescente; mesmo hotel somado e `--top` respeitado | 5 |
| `test_validation_sample.py` | Amostra de validação inteira contra as tabelas do README | todos |
| `test_exit_codes.py` | Saída `2` para arquivo ausente, `--top 0` e moeda sem taxa (parametrizado) | 6 |

`tests/cli_runner.py` é um helper para rodar o CLI sobre os arquivos de `data/` e testar códigos de erro. O
`run_cli` fornecido sempre gera um CSV sintético e exige saída `0`, e o `helpers.py` não pode ser alterado.

## Como validar

```bash
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

pytest -q

PYTHONPATH=src python -m onfly_report \
  --input data/exemplo-validacao.csv \
  --rates data/taxas_cambio.csv \
  --output output/exemplo.json

PYTHONPATH=src python -m onfly_report \
  --input data/reservas_hoteis.csv \
  --rates data/taxas_cambio.csv \
  --output output/report.json
```

## Resultado do `pytest`

```
$ pytest -q
..................                                                       [100%]
18 passed in 5.36s
```

Ambiente usado: Windows 11, pytest 8.3.4. Testes e CLI validados em Python 3.12.10 e 3.11.15 (18 passed nos dois).

## Resultado no dataset completo

```
Reservas: 300 | Confirmadas: 235 | Noites: 1347 | Total BRL: 396170.00
```

| Campo | Valor |
|-|-|
| `total_reservations` | 300 |
| `confirmed_reservations` | 235 |
| `cancelled_reservations` | 31 |
| `no_show_reservations` | 34 |
| `total_room_nights` | 1347 |
| `total_amount_brl` | 396170.00 |
| `average_nightly_rate_brl` | 294.11 |

| `month` | `reservations` | `room_nights` | `total_brl` |
|-|-|-|-|
| 2024-12 | 35 | 174 | 61335.80 |
| 2025-01 | 37 | 235 | 64662.89 |
| 2025-02 | 26 | 138 | 45991.09 |
| 2025-03 | 39 | 215 | 65984.99 |
| 2025-04 | 21 | 146 | 31335.97 |
| 2025-05 | 39 | 196 | 63507.98 |
| 2025-06 | 38 | 243 | 63351.29 |

| `hotel_id` | `hotel_name` | `room_nights` | `total_brl` |
|-|-|-|-|
| H06 | Hotel Salvador Centro | 160 | 45165.46 |
| H10 | Hotel Madrid, Gran Vía | 120 | 45041.69 |
| H12 | Hotel Miami Beach | 106 | 41647.69 |
| H07 | Hotel Brasília Tower | 148 | 39920.52 |
| H11 | Hotel Buenos Aires | 102 | 37455.69 |
