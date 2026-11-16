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

## Arquivos e funções corrigidos

| Arquivo | Função/ponto de entrada | Responsabilidade corrigida |
|---|---|---|
| src/onfly_report/repositories/csv_reservation_repository.py | CsvReservationRepository.read() | Lê todas as linhas sem limite de 200 e transforma falhas de leitura, inclusive UTF-8 inválido, em erro de entrada. |
| src/onfly_report/services/row_parser.py | RowParser.parse() | Valida campos obrigatórios, status, quartos positivos, valor finito, formato/data e ordem de check-in e checkout; preserva a linha no erro. |
| src/onfly_report/repositories/csv_rate_repository.py | CsvRateRepository.read() | Valida taxas, finitude, duplicidade de moeda e tabela vazia. |
| src/onfly_report/services/stay_calculator.py | calculate_room_nights() | Calcula a diferença entre datas completas, multiplicada pelos quartos. |
| src/onfly_report/services/status_policy.py | is_billable() | Retorna verdadeiro apenas para CONFIRMED. |
| src/onfly_report/services/currency_converter.py | convert_to_brl() | Multiplica Decimal pelo câmbio e transforma moeda sem taxa em erro de entrada. |
| src/onfly_report/services/report_builder.py | ReportBuilder.build() e format_money() | Agrega apenas confirmadas, valida nomes por hotel_id em todos os status, ordena ranking e meses, calcula médias e serializa dinheiro/horário conforme o contrato. |
| src/onfly_report/cli.py | main() | Impede sobrescrita dos CSVs de entrada e preserva os códigos de saída para entrada inválida/erro inesperado. |

Os cinco testes fornecidos não foram alterados. Foram adicionados tests/test_reservation_validation.py e tests/test_remaining_validation.py.

## Investigação e abordagem

Comecei entendendo a estrutura do projeto e como o CLI, os repositórios e os serviços se conectam. Depois comparei a execução original com as regras do README. Na primeira tentativa, faltou configurar PYTHONPATH=src; com o caminho ajustado, vi que o relatório processava 200 das 300 reservas, tinha -1.393 noites, total de 193218.53 BRL e média 0.00. Usei essa diferença para investigar cada etapa, em vez de tentar corrigir o relatório de uma vez.

Minhas hipóteses foram sendo confirmadas pelos resultados intermediários: a leitura parava em 200; a conta de noites ignorava a virada do mês; a política incluía NO_SHOW; a conversão dividia e passava por float; e a ordenação do ranking era crescente. Apliquei as correções principais uma por vez e pedi novas execuções para conferir o efeito e identificar o que ainda estava errado.

Na revisão de robustez, pedi primeiro testes que reproduzissem cada inconsistência. O fluxo foi: observar o comportamento atual, confirmar a falha, corrigir quando o README definia a regra e rodar a suíte novamente. Quando o comportamento não estava especificado, decidi antes de implementar: aceitar CSV sem reservas e estadia de zero noites, rejeitar taxa duplicada e rejeitar nomes diferentes para o mesmo hotel_id.

O histórico da conversa está em entrega/uso-de-ia/sessao-original.md. Esse é o único registro de sessão incluído na entrega; mantive o arquivo sem alterações. A tabela acima relaciona cada alteração ao arquivo e à função correspondente.

## Como validar

Com Python 3.11 ou superior, pytest e Ruff instalados.

### Bash

    python -m pytest -q
    python -m ruff check .
    PYTHONPATH=src python -m onfly_report --input data/exemplo-validacao.csv --rates data/taxas_cambio.csv --output output/exemplo.json
    PYTHONPATH=src python -m onfly_report --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv --output output/report.json

### PowerShell

    python -m pytest -q
    python -m ruff check .
    $env:PYTHONPATH = "src"
    python -m onfly_report --input data/exemplo-validacao.csv --rates data/taxas_cambio.csv --output output/exemplo.json
    python -m onfly_report --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv --output output/report.json

### Saída observada na validação final

    python -m pytest -q
    ....................................                                     [100%]
    36 passed in 4.36s

    python -m ruff check .
    All checks passed!
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

A declaração está em entrega/uso-de-ia/declaracao.md. O arquivo entrega/uso-de-ia/sessao-original.md contém o histórico da conversa em Markdown e é o único registro de sessão incluído na entrega.
