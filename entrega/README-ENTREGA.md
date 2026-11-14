# Entrega — Consolidador de reservas Onfly

## Defeitos corrigidos

| Defeito | Causa raiz |
|---|---|
| O relatório considerava no máximo 200 reservas. | O repositório interrompia a leitura do CSV quando a lista chegava a 200 linhas. |
| Algumas estadias produziam noites negativas ou incorretas na virada de mês/ano. | O cálculo subtraía apenas o número do dia, sem calcular a diferença entre as datas completas. |
| Reservas `NO_SHOW` entravam nos totais financeiros e de noites. | A política considerava faturável todo status diferente de `CANCELLED`, em vez de somente `CONFIRMED`. |
| Valores convertidos para BRL divergiam do esperado e podiam perder precisão. | A conversão dividia o valor pela taxa e convertia `Decimal` para `float`, em vez de multiplicar usando `Decimal`. |
| O ranking de hotéis aparecia em ordem crescente. | A ordenação usava o total em ordem crescente, sem inverter a chave do valor. |

## Validações e consistência de dados

Além dos defeitos de cálculo, foram adicionadas validações para:

- exigir datas no formato `YYYY-MM-DD`, rejeitar datas inexistentes e checkout anterior ao check-in;
- rejeitar quartos iguais a zero ou negativos e campos essenciais vazios (`reservation_id`, `hotel_id`, `hotel_name`, `status` e `currency`);
- rejeitar status desconhecidos, valores/taxas não finitos, moedas sem taxa e taxas duplicadas;
- rejeitar nomes divergentes para o mesmo `hotel_id`, inclusive em reservas não faturáveis;
- classificar arquivos com codificação UTF-8 inválida como entrada inválida;
- impedir que o arquivo de saída sobrescreva o CSV de reservas ou a tabela de câmbio;
- serializar `generated_at` sempre com offset `-03:00`.

Decisões de comportamento tomadas durante a revisão: um CSV de reservas com cabeçalho e sem registros gera um relatório zerado; check-in e checkout na mesma data são aceitos como estadia de zero noites; taxas duplicadas e nomes divergentes para o mesmo hotel são rejeitados.

## Investigação e abordagem

O trabalho começou pelo mapeamento do fluxo __main__ → CLI → repositórios/parser → serviços → ReportBuilder → JSON e pela leitura do README como contrato funcional. A primeira execução exigiu configurar PYTHONPATH=src; depois disso, o relatório original foi comparado com as regras e com o CSV completo. Essa comparação mostrou 200 reservas processadas de 300, -1.393 noites, 193218.53 BRL e média 0.00, contra 300 reservas, 1.347 noites, 396170.00 BRL e média 294.11 esperados.

As correções dos defeitos originais foram feitas e conferidas por etapas. A leitura integral revelou que ainda havia erros de cálculo; o ajuste das datas revelou o filtro incorreto de NO_SHOW; corrigir o status deixou isolados o câmbio e a ordenação. Depois de cada alteração, foram gerados relatórios separados e/ou executados os testes relevantes. A sessão detalha as hipóteses, as perguntas, os resultados intermediários e quem conduziu cada mudança.

Para os pontos de robustez, o processo passou a ser explicitamente test-first: adicionar um teste que reproduzisse a falha, observar a implementação atual, corrigir e rodar novamente a suíte. Esse fluxo foi aplicado às validações de linha e de data e aos casos de valores não finitos, taxa ausente ou duplicada, status desconhecido, codificação inválida, conflito de nome por hotel_id, fuso horário e proteção dos arquivos de entrada. Nos quatro comportamentos sem regra definida pelo README, a implementação só foi fechada depois das decisões da pessoa autora: relatório zerado para CSV sem registros, aceitar zero noites, rejeitar taxa duplicada e rejeitar nomes divergentes para o mesmo hotel.

Os testes fornecidos permaneceram inalterados. Foram adicionados tests/test_reservation_validation.py e tests/test_remaining_validation.py.

## Como validar

Com Python 3.11 ou superior, pytest e Ruff instalados:

```powershell
python -m pytest -q
python -m ruff check .
$env:PYTHONPATH = "src"
python -m onfly_report --input data/exemplo-validacao.csv --rates data/taxas_cambio.csv --output output/exemplo.json
python -m onfly_report --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv --output output/report.json
```

Resultado da validação final: **36 testes passaram** e `ruff check .` terminou com `All checks passed!`.

## Resultados

### Amostra de validação do README

| Métrica | Resultado |
|---|---:|
| Reservas totais | 12 |
| Confirmadas / canceladas / no-show | 9 / 2 / 1 |
| Noites de quarto | 28 |
| Total BRL | `7566.00` |
| Média por noite | `270.21` |

| Mês | Reservas confirmadas | Noites | Total BRL |
|---|---:|---:|---:|
| 2025-01 | 8 | 25 | `6684.00` |
| 2025-02 | 1 | 3 | `882.00` |

Top hotéis da amostra, na ordem: H01 (`1200.00`), H02 (`1084.00`), H12 (`1000.00`), H10 (`900.00`) e H09 (`882.00`). Os resultados conferem com a tabela do README.

### Dataset completo `data/reservas_hoteis.csv`

| Métrica | Resultado |
|---|---:|
| Reservas totais | 300 |
| Confirmadas / canceladas / no-show | 235 / 31 / 34 |
| Noites de quarto confirmadas | 1.347 |
| Total BRL confirmado | `396170.00` |
| Média por noite | `294.11` |

| Mês do check-in | Reservas confirmadas | Noites | Total BRL |
|---|---:|---:|---:|
| 2024-12 | 35 | 174 | `61335.80` |
| 2025-01 | 37 | 235 | `64662.89` |
| 2025-02 | 26 | 138 | `45991.09` |
| 2025-03 | 39 | 215 | `65984.99` |
| 2025-04 | 21 | 146 | `31335.97` |
| 2025-05 | 39 | 196 | `63507.98` |
| 2025-06 | 38 | 243 | `63351.29` |

Top cinco hotéis: H06 (`45165.46`), H10 (`45041.69`), H12 (`41647.69`), H07 (`39920.52`) e H11 (`37455.69`).

## Registro de uso de IA

A declaração está em entrega/uso-de-ia/declaracao.md. O diretório também contém sessao.md, uma reconstrução cronológica do processo, e sessao.jsonl, uma transcrição JSON Lines filtrada da sessão local do Codex, com mensagens visíveis e horários. O JSONL não é o arquivo interno integral de execução; instruções internas, raciocínio e detalhes de ferramentas foram excluídos. O documento Markdown organiza os marcos do JSONL por investigação, decisão, correção e validação, sem se apresentar como transcrição literal.
