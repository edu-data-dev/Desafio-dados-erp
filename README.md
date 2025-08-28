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