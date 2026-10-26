# Acervo — Catálogo de documentos

**Projeto de demonstração · Python · PySide6 · CSV**

Ferramenta para pesquisar e exportar metadados de documentos fictícios. Um núcleo em Python sem dependências atende ao CLI; uma interface PySide6 opcional utiliza as mesmas regras.

> Todos os registros são inventados. Os títulos, páginas e status são exemplos: não representam PDFs reais. O programa não abre arquivos de clientes, não consulta sistemas externos e não reaproveita código privado.

## Linha de comando

Requisito: Python 3.10 ou superior.

```sh
python app.py
python app.py --query relatorio
python app.py --category Guias --export catalogo-demo.csv
```

A saída é JSON; o CSV usa UTF-8 com BOM para facilitar a abertura em planilhas. Os filtros são combinados e a busca ignora acentos. O programa encontra `documents.json` em relação ao próprio arquivo, independentemente da pasta atual do terminal.

## Interface desktop opcional

```sh
python -m pip install -r requirements.txt
python app.py --gui
```

A janela oferece busca, categoria, quantidade de resultados, tabela e exportação da seleção. O botão de exportação abre um diálogo para escolher o destino. Sem PySide6 instalado, o CLI continua funcionando e `--gui` explica como instalar.

## Testes

```sh
python -m unittest -v
```

Cobrem busca sem acentos, filtros combinados, exportação, proteção contra fórmulas de planilha, identificadores duplicados e páginas inválidas. Não acessam internet ou dados reais.

## Decisões técnicas

- Validação de esquema antes de apresentar os registros.
- Regras de seleção e exportação independentes da interface.
- Campos de CSV que poderiam ser interpretados como fórmula recebem prefixo seguro.
- CLI retorna código `2` para erro de arquivo ou conteúdo inválido.
- Metadados locais e somente leitura, sem banco ou credenciais.

## Limites

É um catálogo de metadados: não realiza OCR, leitura de PDF, downloads ou sincronização. A interface requer ambiente gráfico e instalação opcional de PySide6. Não há alegação de uso em produção.

Demonstração para o portfólio de [Nycolas França](https://github.com/Scorpped).
