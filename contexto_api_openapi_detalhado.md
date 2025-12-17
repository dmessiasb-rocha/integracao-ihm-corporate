# Contexto Detalhado para Documentação da API (OpenAPI)

Fonte: **RTP-426-AEF-001 - Interface Corporate REV 00** (lista de mensagens entre Corporate e SSL). Este contexto expande cada linha/mensagem da planilha com **campos**, **tipos**, **direção (origem→destino)** e **observações** para guiar a modelagem dos `paths` e `schemas` no OpenAPI. citeturn1search1

> Convenções:
> - Tipos mapeados para OpenAPI: Texto→`string`, Inteiro→`integer`, Decimal→`number`, DataHora→`string` (formato ISO 8601) — ainda que a planilha use exemplos `dd/MM/yyyy` e `HH:mm`.
> - Onde o ERP não possui dado, aceitar `null` e documentar como **opcional**.
> - Payloads binários serão Base64 (`string` com `format: byte`).

---

## ID 001 — Cadastros de **Clientes** (Corporate → SSL)
**Método:** POST/PUT `/clientes`
**Descrição:** Envio de cadastro e edição de clientes.
**Campos:**
- `IdCliente` (`string`, **obrigatório**) — Código do cliente no ERP (chave do registro). Limites: N/D.
- `NumCNPJ` (`string`, opcional) — Número do CNPJ.
- `NumCPF` (`string`, opcional) — Número do CPF.
- `RazaoSocial` (`string`, **obrigatório**) — Razão Social.
- `NomeFantasia` (`string`, opcional) — Nome Fantasia.
- Endereço:
  - `Rua` (`string`), `Numero` (`integer`, min: 0), `Complemento` (`string`), `Bairro` (`string`), `Cidade` (`string`), `Estado` (`string`), `Pais` (`string`), `Cep` (`string`).
- Contatos: `Telefone` (`string`), `Email` (`string`).
- `Tipo` (`string`, opcional) — Cliente/Fornecedor/Destinatario/Transportador.

## ID 002 — Cadastros de **Produtos** (Corporate → SSL)
**Método:** POST/PUT `/produtos`
**Campos:**
- `CodProduto` (`string`, **obrigatório**).
- `Descricao` (`string`, **obrigatório**).
- `UnidadeMedida` (`string`, **obrigatório**).

## ID 003 — Cadastros de **Veículos** (Corporate → SSL)
**Método:** POST/PUT `/veiculos`
**Campos:**
- `IdVeiculo` (`string`, **obrigatório**).
- `Placa` (`string`, **obrigatório**).
- `Uf` (`string`, **obrigatório**).
- `Ano` (`integer`, opcional/`null`) — informação não disponível no ERP.
- `QtdEixos` (`integer`, opcional/`null`).
- `Modelo` (`string`, opcional/`null`).
- `CpfProprietario` (`string`, opcional/`null`).
- `CnpjProprietario` (`string`, opcional/`null`).
- `IdTransportadora` (`string`, opcional/`null`).

## ID 004 — Cadastros de **Motoristas** (Corporate → SSL)
**Método:** POST/PUT `/motoristas`
**Campos mínimos:**
- `IdMotorista` (`string`, **obrigatório**).
- `Nome` (`string`, **obrigatório**).
- `NumCpf` (`string`, **obrigatório**).
- `NumCnh` (`string`, **obrigatório**).
- `DthValidadeCnh` (`string`, formato ISO 8601, **obrigatório**).
- `Celular` (`string`, opcional).



## ID 005 — **Programação de Navio** (Corporate → SSL)
**Método:** POST/PUT `/programacoes/navio`
**Campos:**
- `CodCliente` (`string`, **obrigatório**).
- `CodProduto` (`string`, **obrigatório**).
- `NomeNavio` (`string`, **obrigatório**).
- `IdNavio` (`string`, **obrigatório**) — vem da APPA Web.
- `Lote` (`string`, **obrigatório**).
- `Deposito` (`string`, **obrigatório**).
- `NumeroProgramacaoAppa` (`string`, **obrigatório**).
- `TipoDocumento` (`string`, **obrigatório**) — NF/ticketApp.

## ID 006 — **Confirmação de ações** (crachá/biometria) (Corporate → SSL)
**Método:** POST `/agendamentos/{id}/acoes/confirmacoes`
**Campos:**
- `IdAgendamento` (`string`, **obrigatório**).
- `Status` (`string`, **obrigatório**).
- `Acao` (`string`, **obrigatório**) — exemplo: "Crachá gravado", "Biometria".
- `IdCorporate` (`string`, **obrigatório**).

## ID 007 — **Confirmação de gravação de pesagem** (Corporate → SSL)
**Método:** POST `/pesagens/confirmacoes`
**Campos:**
- `IdAgendamento` (`string`, **obrigatório**).
- `Status` (`string`, **obrigatório**) — valores: "Liberar", "AjustarPeso" (libera cancela traseira), "LiberarVeiculoComErro" (finaliza no SSL).
- `MensagemErro` (`string`, opcional).
- `Doc` (`string`, `format: byte`, opcional) — Ticket gerado pelo ERP (Base64).

## ID 008 — **Confirmação de programação de carga** (Corporate → SSL)
**Método:** POST `/programacoes/carga/confirmacoes`
**Campos:**
- `IdProgramacaoSSL` (`string`, **obrigatório**).
- `Status` (`string`, **obrigatório**) — "Liberado"/"Recusado".
- `Observacao` (`string`, opcional).
- `QuantidadeLiberada` (`number`, opcional).
- `DataInicial` (`string`, ISO 8601, opcional) — período de liberação.
- `DataFinal` (`string`, ISO 8601, opcional).
- `IdProgramacaoCorporate` (`string`, **quando enviar agendamento**).

## ID 009 — **Solicitação de ações com crachá/biometria** (SSL → Corporate)
**Método:** POST `/agendamentos/{id}/acoes`
**Campos:**
- `IdAgendamento` (`string`, **obrigatório**).
- `Local` (`string`, **obrigatório**) — qual totem.
- `Acao` (`string`, **obrigatório**) — ex.: gravação de crachá, captura de biometria.

## ID 010 — **Pesagem** (SSL → Corporate)
**Método:** POST `/pesagens`
**Acionado:** após estabilização do peso.
**Campos:**
- `IdAgendamento` (`string`, **obrigatório**).
- `IdCorporate` (`string`, **obrigatório**) — SSL recebe após gravação de crachá.
- `Peso` (`number`, **obrigatório**).
- Diretórios de imagens OCR (`string`): `DiretorioImagemOcrCavalo`, `DiretorioImagemOcrCarreta01`, `DiretorioImagemOcrCarreta02` (opcionais).
- Placas OCR (`string`): `PlacaCavaloOCR`, `PlacaCarreta01OCR`, `PlacaCarreta02OCR` (opcionais).

## ID 011 — **Programação de Transferência** (SSL → Corporate)
**Método:** POST `/programacoes/transferencia`
**Campos:**
- `Armazem` (`string`, **obrigatório**).
- `Cliente` (`string`, **obrigatório**).
- `Produto` (`string`, **obrigatório**).
- `Quantidade` (`number`, **obrigatório**).
- `Lote` (`string`, **obrigatório**).
- `DataProgramada` (`string`, ISO 8601, **obrigatório**).
- `IdProgramacaoSSL` (`string`, opcional).
- `ObservacaoFiscal` (`string`, opcional).

## ID 012 — **Saldos por lote e depósito** (SSL → Corporate)
**Método:** GET `/saldos/lote-deposito`
**Parâmetros/Retorno:**
- `Lote` (`string`).
- `Deposito` (`string`).
- `NumDI` (`string`).
- `Origem` (`string`).
- `CodDest` (`string`).
- `Cliente` (`string`).
- `Material` (`string`).
- `Produto` (`string`).
- `Saldo` (`number`).

## ID 013 — **Programação de Carga** (SSL → Corporate)
**Método:** GET `/programacoes/carga`
**Retorno (por item):**
- `IdProgramacaoSSL` (`string`).
- `NumLote` (`string`).
- `Deposito` (`string`).
- `QuantidadeProgramada` (`number`).
- `Modal` (`string`) — fixo: "Rodoviario".
- `DataProgramacao` (`string`, ISO 8601).
- `ObsFiscal` (`string`).
- `Embalagem` (`string`).
- Destino: `UFDestino` (`string`), `RazaoSocialDestino` (`string`), `CNPJDestino` (`string`) — campos abertos no SSL.

## ID 014 — **Embalagens (catálogo)** (Corporate → SSL | também GET no SSL)
**Métodos:**
- POST/PUT `/embalagens` — quando Corporate envia catálogo.
- GET `/embalagens` — consulta no SSL.
**Campos:**
- `CodEmbalagem` (`string`, **obrigatório**).
- `Descricao` (`string`, **obrigatório`).

## ID 015 — **Agendamento** (SSL → Corporate)
**Método:** GET `/agendamentos`
**Retorno/Modelo:**
- `IdAgendamento` (`string`).
- `IdProgramacaoCorporate` (`string`) — referência: Programação Navio ou IdProgramacaoCarga ou IdProgramacaoTransferencia.
- `CodCliente` (`string`).
- `CodProduto` (`string`).
- Placas: `PlacaCavalo`, `PlacaCarreta01`, `PlacaCarreta02` (`string`).
- `TipoVeiculo` (`string`) — fixo para agendamento de descarga.
- `CodMotorista` (`string`) — dependerá do fluxo de motorista novo (Rocha).
- `CodTransportadora` (`string`).
- `HoraAgendamento` (`string`, ISO 8601 - DateTime).
- `Quantidade` (`number`) — kg.
- `CodClienteDestino` (`string`, opcional) — validar necessidade.
- `TipoAgendamento` (`string`) — carga/descarga porto/carga transferência/descarga transferência.
- `NumTicketAppa` (`string`) — quando descarga (via APPA Web).
- `NomeArmazem` (`string`).
- `IdAgendamentoCarga` (`string`) — caso de descarga de transferência.
- **Retorno adicional:** Situação (0=ok, 1=erro), Mensagem erro.

## ID 016 — **Tipo de Veículo** (Corporate → SSL | também GET no SSL)
**Métodos:**
- POST `/tipos-veiculo` — quando Corporate envia.
- GET `/tipos-veiculo` — consulta.
**Campos:**
- `CodVeiculo` (`string`).
- `Descricao` (`string`).

## ID 017 — **Checklist (processo de carga)** (SSL → Corporate)
**Método:** GET `/checklists/carga`
**Entrada:** `IdAgendamento` (`string`), `CodigoArmazem` (`string`).
**Retorno:**
- `Status` (`boolean`) — True/False.
- Dados fiscais: `ChaveNF` (`string`), `NumeroNF` (`string`), `SerieNF` (`string`), `DataEmissao` (`string`, ISO 8601), `PesoLiquido` (`number`), `ValorTotal` (`number`).
- `SolicitaCapturaBiometria` (`boolean`) — se será necessário solicitar biometria no totem.
- `Situacao` (`integer`) — 0=ok, 1=erro.
- `MensagemErro` (`string`).

## ID 018 — **Consulta/Recupera Imagem** (Corporate → SSL)
**Método:** GET `/imagens`
**Parâmetros:**
- `IdAgendamento` (`string`).
- `DiretorioImagem` (`string`).
**Retorno:** binário Base64 da imagem.

## ID 019 — **Consulta Saldo Cliente-Produto** (SSL → Corporate)
**Método:** GET `/saldos/cliente-produto`
**Parâmetros:** `Cliente` (`string`), `Armazem` (`string`), `Produto` (`string`).
**Retorno:** lista de itens contendo `Lote` (`string`) e `Saldo` (`number`).

## ID 020 — **Confirmação de programação de transferência** (Corporate → SSL)
**Método:** POST `/programacoes/transferencia/confirmacoes`
**Campos:**
- `IdProgramacaoSSL` (`string`, **obrigatório**).
- `Status` (`string`, **obrigatório**) — "Liberado"/"Recusado".
- `Observacao` (`string`, opcional).
- `QuantidadeLiberada` (`number`, opcional).
- `DataInicial` (`string`, ISO 8601, opcional).
- `DataFinal` (`string`, ISO 8601, opcional).
- `IdProgramacaoCorporate` (`string`, **quando enviar agendamento**).

## ID 021 — **Cadastro de Motorista (variação)** (ssl → Corporate)
**Método:** POST/PUT `/motoristas` (quando iniciado pelo SSL)
**Campos:** mesmos do **ID 004**, incluindo campos estendidos (foto, documentos, etc.).
- `Foto` (`string`, `format: byte`) — Base64.
- `IdAgendamento` (`string`).
- `OrgaoEmissor` (`string`), `RG` (`string`).
- `OrgaoEmissorCnh` (`string`).
- `Sexo` (`string`).
- `DataNascimento` (`string`, ISO 8601).
- `PaisNacionalidade` (`string`), `Estado` (`string`).
- `TipoDocumento` (`string`) — para estrangeiro.
- `NumeroDocumento` (`string`).
- `OrgaoEmissaoDocumento` (`string`).
- `ValidadeDocumento` (`string`, ISO 8601`).
**Retorno:** `IdMotoristaCorporate` (`string`).
**Adicionar também os campos do ID 004**

---

## Observações Gerais
- **Formatação de datas e horas**: apesar dos exemplos da planilha (`dd/MM/yyyy`, `HH:mm`), padronizar em OpenAPI com ISO 8601, indicando a aceitação dos formatos legados quando necessário.
- **Binários**: `Doc` (tickets) e `Foto` devem ser Base64.
- **Nullability**: onde o ERP não possui dados (e.g., veículo), permitir `null` e documentar como **opcional**.
- **Traçado de origem/destino**: manter claro o sentido *Corporate→SSL* vs *SSL→Corporate* em cada endpoint.

---

Este contexto detalhado deverá ser usado como blueprint para criar os `schemas` em `components/schemas` e os `paths` correspondentes no **OpenAPI** (`openapi.yaml`). cite	turn1search1
