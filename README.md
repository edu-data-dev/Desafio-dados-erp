# Desafio de Engenharia de Dados

Este repositório contém a solução para o desafio de Engenharia de Dados proposto por um Laboratório de Tecnologia bastante conhecido no mercado.

## Descrição do Projeto

O projeto está dividido em duas partes principais:
1.  **Desafio 1:** Modelagem de dados de um JSON de ERP para um esquema relacional SQL, com a devida justificativa.
2.  **Desafio 2:** Proposta de arquitetura para ingestão e armazenamento de dados em um Data Lake, abordando estrutura, governança e resiliência a mudanças de esquema.

## Como Executar o Projeto

*(Esta seção será preenchida ao final, com instruções claras para o avaliador)*

1. Clone o repositório: `git clone ...`
2. ...

## Estrutura do Repositório

- **/data**: Contém os dados brutos de entrada (ex: `ERP.json`).
- **/sql**: Contém os scripts de DDL (Data Definition Language) para criar o schema no banco de dados.
- **/src**: Contém os scripts Python para processamento e simulação.
- **README.md**: Este documento.

## Solução do Desafio

*(Aqui você vai colocar ou linkar suas respostas detalhadas)*

### Desafio 1

#### 1. Esquema do JSON

O arquivo `ERP.json` representa a resposta de um endpoint de ERP para um pedido específico. Sua estrutura hierárquica é a seguinte:

- **Objeto Raiz**:
  - `curUTC` (string): Timestamp atual em UTC.
  - `locRef` (string): Identificador da loja/local.
  - `guestChecks` (array): Lista contendo os pedidos. No exemplo, há apenas um.
    - **Objeto `guestCheck`**:
      - `guestCheckId` (number): ID único do pedido.
      - `chkNum` (number): Número do pedido.
      - `opnBusDt`, `clsdBusDt` (string): Datas de negócio de abertura e fechamento.
      - `opnUTC`, `clsdUTC` (string): Timestamps de abertura e fechamento em UTC.
      - `clsdFlag` (boolean): Indica se a conta está fechada.
      - `gstCnt` (number): Número de clientes.
      - `subTtl`, `chkTtl`, `dscTtl`, `payTtl` (number): Valores monetários totais.
      - `tblNum`, `empNum` (number): IDs da mesa e do funcionário.
      - `taxes` (array): Lista dos impostos aplicados ao pedido.
        - **Objeto `tax`**:
          - `taxNum` (number): ID do imposto.
          - `txblSlsTtl` (number): Valor sobre o qual o imposto incide.
          - `taxCollTtl` (number): Valor do imposto coletado.
          - `taxRate` (number): Alíquota do imposto.
      - `detailLines` (array): Lista de itens/linhas que compõem o pedido.
        - **Objeto `detailLine`**:
          - `guestCheckLineItemId` (number): ID único da linha do item.
          - `dspTtl`, `aggTtl` (number): Valor do item.
          - `dspQty`, `aggQty` (number): Quantidade do item.
          - `menuItem` (objeto): Detalhes do item do cardápio.
            - **Objeto `menuItem`**:
              - `miNum` (number): ID do item no cardápio.
              - `modFlag` (boolean): Indica se é uma modificação de um item.
              - `inclTax` (number): Valor do imposto incluso no preço.
...

### Desafio 2

[cite_start]Esta seção aborda a arquitetura de um Data Lake para armazenar e processar dados de múltiplos endpoints da API de restaurantes[cite: 34, 35, 40].

#### [cite_start]1. Por que armazenar as respostas das APIs? [cite: 41]

Armazenar as respostas brutas das APIs (JSONs) em uma camada inicial do Data Lake, conhecida como **Raw Zone** ou **Landing Zone**, é uma prática fundamental na engenharia de dados moderna. As principais razões para isso são:

- **Fonte da Verdade (Source of Truth)**: Os dados brutos são uma cópia fiel e imutável dos dados na origem. Eles servem como uma garantia permanente, permitindo auditorias e a reconstrução de qualquer camada de dados processada a partir deles.
- **Reprocessamento (Replayability)**: Regras de negócio, correções de bugs ou novas necessidades de análise inevitavelmente surgirão. Com os dados brutos guardados, podemos "reprocessar" o histórico com a nova lógica a qualquer momento, sem a necessidade de consultar as APIs de origem novamente, o que poderia ser custoso ou até impossível.
- **Flexibilidade e Futuros Casos de Uso**: Os dados brutos contêm a totalidade das informações. Isso permite que equipes de Business Intelligence, Analytics e Ciência de Dados explorem os dados para novos insights que não foram previstos no momento da ingestão. O modelo é de **Schema-on-Read** (o esquema é aplicado na leitura), e não na escrita.
- **Desacoplamento de Sistemas**: A pipeline é dividida em estágios. O processo de ingestão (salvar o JSON) é simples e robusto, separado do processo de transformação, que é mais complexo e sujeito a falhas. Se a transformação falhar, a coleta de dados não é interrompida, evitando perda de dados.

#### 2. Como você armazenaria os dados? (Estrutura de Pastas) [cite_start][cite: 42]

Para armazenar as respostas da API de forma a permitir manipulação, buscas e pesquisas rápidas, a melhor abordagem é uma **estrutura de pastas hierárquica e particionada**. O particionamento é a chave para a performance em um Data Lake.

A estrutura proposta seria: 
    /datalake/raw/{source_name}/{api_endpoint}/year={YYYY}/month={MM}/day={DD}/{store_id}/data.json

**Exemplo Prático:**

/datalake/raw/erp_api/getGuestChecks/year=2025/month=08/day=27/store_id=99_CB_CB/1661608800_response.json
/datalake/raw/erp_api/getFiscalInvoice/year=2025/month=08/day=27/store_id=101_BSB/1661608800_response.json

**Justificativa da Estrutura:**

- `raw`: Define a camada de dados (brutos, não processados).
- `{source_name}` (ex: `erp_api`): Agrupa os dados por sistema de origem.
- [cite_start]`{api_endpoint}` (ex: `getGuestChecks`): Isola os dados de cada endpoint, pois eles possuem esquemas diferentes[cite: 35].
- `year={YYYY}/month={MM}/day={DD}`: **Particionamento por data**. Esta é a otimização mais crítica. Ferramentas de consulta como Apache Spark, Presto ou Athena usam o "partition pruning" para ler apenas as pastas relevantes para uma consulta (ex: "vendas do último mês"), ignorando terabytes de outros dados e tornando as consultas ordens de magnitude mais rápidas. O formato `chave=valor` é um padrão de mercado.
- [cite_start]`{store_id}`: Particionar também pela loja [cite: 36] é extremamente útil, pois muitas análises de negócio são segmentadas por unidade.
- `data.json`: O arquivo em si, talvez com um timestamp ou UUID para garantir a unicidade.

#### [cite_start]3. Implicações da mudança de `guestChecks.taxes` para `guestChecks.taxation` [cite: 43]

Este cenário descreve um **Schema Drift** (desvio de esquema), um desafio comum em engenharia de dados. As implicações ocorreriam em cascata:

- **Na Camada de Ingestão (Raw Zone)**: **Nenhuma implicação.** O processo de ingestão simplesmente salvaria o novo arquivo JSON com o campo `taxation`. A beleza da Raw Zone é ser "schema-agnóstica". Nenhuma informação seria perdida.

- **Na Camada de Transformação (Processing Zone)**: **Falha Crítica.** É aqui que o problema se manifesta. [cite_start]O código (Spark, Python, etc.) que lê os JSONs para transformá-los em tabelas estruturadas (como as que criamos no Desafio 1) está programado para encontrar o campo `taxes`[cite: 44].
    - **Resultado 1 (Falha Explícita):** O job de transformação falharia com um erro do tipo `KeyError: 'taxes'`, paralisando a atualização dos dados a partir do momento da mudança.
    - **Resultado 2 (Falha Silenciosa):** Se o código for escrito de forma "defensiva" (ex: `guest_check.get('taxes', [])`), ele não quebraria, mas passaria a inserir dados de impostos nulos ou vazios, corrompendo silenciosamente as métricas de negócio.

- **Na Camada de Consumo (BI e Usuários Finais)**: Os dashboards, relatórios e análises que dependem dos dados de impostos começariam a exibir valores incorretos (zeros ou nulos), levando a decisões de negócio erradas e à perda de confiança nos dados.

**Como Mitigar:**
1.  **Código Resiliente:** A lógica de transformação deve ser adaptada para lidar com ambas as versões do esquema. Ex: `tax_data = guest_check.get('taxation', guest_check.get('taxes', []))`.
2.  **Monitoramento e Alertas:** Implementar um sistema que valide o esquema dos dados que chegam na Raw Zone e dispare alertas para a equipe de dados sempre que um desvio for detectado.
3.  **Schema Registry:** Em sistemas mais maduros, ferramentas como o Confluent Schema Registry podem ser usadas para gerenciar e versionar esquemas de dados, permitindo que os processos de transformação se adaptem dinamicamente.


#### 2. Transcrição para Tabelas SQL

O script para criação das tabelas se encontra em `sql/schema.sql`.


#### 3. Justificativa da Abordagem de Modelagem

A abordagem escolhida para transcrever o JSON para SQL foi a **normalização em um modelo relacional (3ª Forma Normal - 3NF)**. A principal motivação é criar um esquema que seja escalável, íntegro e otimizado para as operações de um restaurante.

- **Integridade e Redução de Redundância**:
  - Cada entidade lógica (pedidos, impostos, itens de linha) foi separada em sua própria tabela. A tabela `guest_checks` armazena informações do pedido uma única vez, evitando a repetição desses dados para cada item consumido.
  - O uso de chaves primárias (`PRIMARY KEY`) e estrangeiras (`REFERENCES`) garante a **integridade referencial**. Por exemplo, um registro em `detail_lines` não pode existir sem um `guest_check_id` correspondente na tabela `guest_checks`, prevenindo dados órfãos.

- **Escalabilidade**:
  - A estrutura foi pensada para abranger toda a cadeia de restaurantes. A inclusão do campo `location_ref` na tabela `guest_checks` permite que os dados de todas as lojas sejam armazenados no mesmo banco de dados, podendo ser facilmente filtrados ou agregados por unidade.
  - Consultas de BI, como "Qual o item mais vendido em todas as lojas no último mês?", tornam-se eficientes através de `JOINs` e agregações, o que seria computacionalmente caro de se fazer processando milhares de arquivos JSON.

- **Flexibilidade e Extensibilidade**:
  - O desafio menciona que o objeto `detailLines` pode conter diferentes tipos de informação (`menuItem`, `discount`, `serviceCharge`). Para lidar com isso, a tabela `detail_lines` foi projetada de forma **polimórfica**.
  - A coluna `line_type` identifica a natureza de cada registro (ex: 'MENU_ITEM'). Colunas de chave estrangeira como `menu_item_number` (e futuras como `discount_id`) seriam preenchidas condicionalmente. Isso permite que novas categorias de linhas de detalhe sejam adicionadas no futuro sem a necessidade de reestruturar as tabelas existentes, apenas adicionando novas colunas ou tabelas de referência.
...