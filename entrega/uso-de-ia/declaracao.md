# Declaração de uso de IA

**Ferramenta e modelo:** Codex, assistente de programação da OpenAI, baseado em GPT-6.

## Minha participação

- Comecei entendendo a arquitetura, a ordem de execução e as regras de negócio antes de procurar os defeitos.
- Comparei o relatório original com o README e investiguei as diferenças nos totais.
- Apliquei as correções principais: removi o limite de 200 reservas, mudei o cálculo de noites para usar a diferença entre as datas completas vezes os quartos, ajustei o filtro para considerar apenas CONFIRMED, corrigi a conversão para multiplicar usando Decimal e propus a ordenação decrescente por valor com hotel_id crescente nos empates.
- Depois de cada mudança, pedi uma nova execução ou os testes para conferir o resultado e entender o que ainda precisava ser corrigido.
- Pedi que as inconsistências adicionais fossem reproduzidas por testes antes da implementação e que a regra fosse discutida comigo quando o README não desse a resposta.
- Decidi aceitar um relatório zerado quando o CSV tem cabeçalho mas nenhuma reserva, aceitar estadia de zero noites, rejeitar taxas duplicadas e rejeitar nomes diferentes para o mesmo hotel_id.
- Pedi a revisão final do código, dos testes, do Ruff e dos documentos de entrega.

## Apoio do Codex

- Mapeou comigo o fluxo do CLI, dos repositórios, do parser e dos serviços, e comparou os resultados do programa com o README.
- Ajudou a localizar as causas dos erros e sugeriu as alterações para as correções iniciais. Também executou o programa e os testes depois das mudanças que fiz, mostrando os resultados intermediários.
- Criou testes para as validações do parser e para os demais casos de robustez. Primeiro executou os testes contra o comportamento existente; depois implementou as validações e correções acordadas.
- Corrigiu, entre outros pontos, validações de datas, campos e quartos; valores não finitos; moeda sem taxa; status inválido; taxa duplicada; nomes conflitantes por hotel_id; proteção contra sobrescrita dos CSVs e normalização de generated_at.
- Executou pytest e Ruff, comparou a amostra e o dataset completo e ajudou a preparar a documentação técnica.

As decisões de regra de negócio foram minhas. O trabalho foi colaborativo: conduzi a investigação, apliquei as correções principais e escolhi os comportamentos que o README não definia; o Codex ajudou na análise, nos testes, nas correções adicionais e nas verificações.

O histórico da conversa está registrado em sessao-original.md, único arquivo de sessão incluído na entrega. Mantive esse registro original sem alterações.
