# Declaração de uso de IA

**Ferramenta e modelo:** Codex, assistente de programação da OpenAI baseado em GPT-6.

## Participação da pessoa autora

- Começou entendendo a arquitetura e as regras antes de procurar defeitos, pediu o mapeamento do fluxo de execução e dos arquivos responsáveis por cada regra.
- Comparou o relatório original com o README e identificou no código e nos resultados as falhas de leitura, noites, status, câmbio e ordenação.
- Aplicou no workspace as correções iniciais: remover o limite de 200 reservas, calcular noites pela diferença entre datas completas vezes quartos, considerar apenas CONFIRMED, multiplicar o valor pela taxa mantendo Decimal e ordenar os totais de forma decrescente com hotel_id crescente nos empates.
- Conferiu os resultados intermediários por meio de novas execuções e testes, apontando as divergências que persistiam após cada correção.
- Pediu que o fluxo para inconsistências adicionais começasse por testes que reproduzissem o problema antes da implementação.
- Tomou as decisões de regra de negócio não especificadas no README: aceitar relatório zerado para CSV sem registros, aceitar estadia de zero noites, rejeitar taxas duplicadas e rejeitar nomes diferentes associados ao mesmo hotel_id.
- Pediu revisão final das regras, qualidade, testes, Ruff e documentação de entrega.

## Auxílio da IA

- Explicou a arquitetura, a sequência de execução e o vínculo entre regras, serviços e repositórios; comparou a execução inicial com o README e calculou as referências do dataset completo.
- Sugeriu formas de corrigir os defeitos iniciais e executou o CLI e os testes após as mudanças feitas pela pessoa autora, apontando o que já coincidia com o esperado e o que ainda divergia.
- Criou testes para as validações do parser, formatos de data e demais casos de robustez; executou os testes antes das correções para registrar as falhas.
- Implementou, após o fluxo acordado, validações no parser e nos repositórios, tratamento de valores não finitos e moeda sem taxa, rejeição de status desconhecido, duplicidade de taxas e inconsistência de nomes por hotel_id, proteção contra sobrescrita dos CSVs e normalização de generated_at.
- Executou as verificações finais de pytest e Ruff, comparou a amostra e o dataset completo com os valores esperados e ajudou a organizar os documentos.

As decisões de negócio listadas acima foram tomadas pela pessoa autora. A implementação e as validações foram colaborativas: a pessoa autora conduziu a investigação, aplicou as correções iniciais, definiu os casos ambíguos e acompanhou os resultados; a IA analisou o código, propôs e implementou testes e correções posteriores e executou verificações. O histórico cronológico está em sessao.md; sessao.jsonl fornece uma transcrição estruturada e filtrada das mensagens visíveis, não uma cópia integral do registro interno de execução.
