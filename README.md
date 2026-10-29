# Como executar o exemplo de controle de parada

Este guia acompanha o arquivo `controle_parada_reflection.py`, versão 1.1. O programa demonstra quando um ciclo de revisão deve continuar, encerrar por satisfação dos critérios ou interromper pelo limite de segurança.

O exemplo usa uma solicitação fictícia de atendimento interno e respostas previamente definidas. A avaliação e as decisões de parada são executadas pelo código. As etapas de geração e refinamento são representadas por um dublê didático: um componente simples que devolve as respostas preparadas para cada cenário.

## 1. O que você precisa

- Python 3.10 ou superior instalado.
- O arquivo `controle_parada_reflection.py` salvo no computador.
- Um terminal aberto na pasta desse arquivo.

O programa utiliza apenas a biblioteca padrão do Python. Não é necessário instalar pacotes com `pip`, criar arquivo `.env`, obter chave de API ou pagar por chamadas a um modelo.

Os comandos deste guia usam `python3`, comum no Linux e no macOS. No Windows, você pode usar `py` no lugar de `python3`. Se o comando disponível no seu computador for `python`, substitua por ele em todos os exemplos. Use um interpretador cuja versão seja 3.10 ou superior.

## 2. Prepare a pasta

1. Crie uma pasta chamada `reflection_demo` no seu computador.
2. Salve nela o arquivo `controle_parada_reflection.py`. Você também pode guardar este `README.md` na mesma pasta.
3. Abra um terminal nessa pasta.

Se o terminal estiver em outra pasta, use `cd` seguido do caminho de `reflection_demo`. Coloque o caminho entre aspas se ele contiver espaços.

## 3. Confira se o Python está disponível

Execute:

```bash
python3 --version
```

O terminal deverá mostrar uma versão, por exemplo `Python 3.12.14`. O exemplo foi verificado nessa versão.

Para conferir se o terminal está encontrando o script, execute:

```bash
python3 controle_parada_reflection.py --help
```

Deve aparecer uma explicação dos argumentos `--cenario`, `--saida` e `--verificar`.

## 4. Execute a verificação inicial

```bash
python3 controle_parada_reflection.py --verificar
```

O programa verifica os comportamentos previstos e mostra os resultados no terminal. Se todas as verificações passarem, a última linha será:

```text
VERIFICACAO_OK
```

Esse comando não gera um arquivo de registros. Ele serve para conferir o funcionamento dos cenários. Se aparecer `VERIFICACAO_FALHOU`, pelo menos uma condição esperada não foi atendida.

## 5. Execute o caso que encerra por satisfação dos critérios

```bash
python3 controle_parada_reflection.py --cenario criterio --saida criterio.json
```

O resultado aparece no terminal e também é salvo em `criterio.json`, na pasta em que o comando foi executado.

O que acontece:

1. A resposta inicial contém somente o resumo do problema.
2. O avaliador identifica dois campos ausentes.
3. O refinador preenche esses campos usando o diagnóstico.
4. A segunda avaliação verifica que os três campos estão preenchidos.
5. O ciclo encerra antes de atingir o limite de três avaliações.

No último item da lista `registros`, confira:

| Campo | Valor esperado |
|---|---|
| `iteracao` | `2` |
| `decisao` | `"parar"` |
| `motivo` | `"criterios_satisfeitos"` |
| `aprovado` | `true` |

Neste exemplo, aprovação significa que os três campos foram preenchidos. Isso não comprova a correção factual de qualquer texto inserido neles.

## 6. Execute o caso que interrompe pelo limite

```bash
python3 controle_parada_reflection.py --cenario limite --saida limite.json
```

Neste cenário, o refinador mantém a resposta incompleta de propósito. A avaliação continua encontrando os mesmos campos ausentes.

Após três avaliações, o programa interrompe o ciclo e preserva as pendências. No último registro, confira:

| Campo | Valor esperado |
|---|---|
| `iteracao` | `3` |
| `decisao` | `"parar"` |
| `motivo` | `"limite_seguranca"` |
| `aprovado` | `false` |
| `problemas` | `proximo_passo` e `informacoes_ausentes` |

O programa encerrou corretamente a tentativa, mas a resposta continua incompleta. O limite de segurança não concede aprovação.

**Como contar:** a resposta inicial já corresponde à primeira avaliação. Com limite de três avaliações, há no máximo duas revisões entre elas.

## 7. Veja o caso em que a resposta já começa completa

```bash
python3 controle_parada_reflection.py --cenario pronta --saida pronta.json
```

A primeira resposta já contém os três campos. O programa encerra na avaliação 1, com `criterios_satisfeitos` e `aprovado: true`. Isso demonstra que uma resposta adequada aos critérios do exemplo não precisa passar por uma revisão desnecessária.

## 8. Compare com a versão defeituosa

```bash
python3 controle_parada_reflection.py --cenario antes --saida antes.json
```

A versão defeituosa avalia a resposta, mas sempre decide continuar. A partir da avaliação 2, os critérios estão satisfeitos, porém a repetição prossegue.

Para o comando terminar, uma bancada externa observa somente seis avaliações. No final, acrescenta este registro:

```json
{
  "bancada": "observacao_encerrada_apos_6",
  "agente_parou": false
}
```

A lista contém seis registros de avaliação e um registro da bancada. O encerramento da observação não representa uma regra de parada implementada no ciclo defeituoso. O valor `max_iteracoes: 3` dos metadados informa a configuração do exemplo corrigido; essa proteção não é aplicada pela versão defeituosa.

## 9. Abra e entenda o arquivo JSON

Abra `criterio.json` em um editor de texto. O arquivo contém duas partes:

| Parte | O que guarda |
|---|---|
| `metadados` | Cenário, data em UTC, versão do Python, versão e hash do script, origem das respostas e configuração do limite. |
| `registros` | Uma lista com as avaliações e decisões da execução. |

Exemplo simplificado, com apenas alguns campos:

```json
{
  "metadados": {
    "cenario": "criterio",
    "versao_script": "1.1"
  },
  "registros": [
    {
      "iteracao": 1,
      "decisao": "continuar",
      "motivo": "criterios_pendentes",
      "aprovado": false
    },
    {
      "iteracao": 2,
      "decisao": "parar",
      "motivo": "criterios_satisfeitos",
      "aprovado": true
    }
  ]
}
```

Cada registro de avaliação inclui:

- `resposta`: o conteúdo avaliado.
- `criterios`: resultado de cada verificação.
- `problemas`: campos que ainda faltam.
- `orientacao`: indicação do que preencher na próxima revisão.
- `decisao` e `motivo`: o que o ciclo decidiu e por quê.
- `aprovado`: se aquela etapa encerrou por satisfação dos critérios.

Em JSON, `true` significa verdadeiro e `false` significa falso. No código Python, esses valores aparecem como `True` e `False`.

Você também pode conferir a validade e exibir o JSON pelo terminal:

```bash
python3 -m json.tool criterio.json
```

Ao repetir um comando com o mesmo nome em `--saida`, o arquivo anterior é sobrescrito. Para conservar duas execuções, escolha nomes diferentes.

## 10. Como o código funciona

### Dados iniciais

`CAMPOS` define os três campos exigidos: `resumo`, `proximo_passo` e `informacoes_ausentes`.

`INICIAL` contém somente o resumo. `COMPLETA` contém os três campos. A expressão `**INICIAL` copia os campos da resposta inicial para a resposta completa.

`MAX_ITERACOES = 3` define o limite padrão de avaliações do ciclo corrigido.

### Função avaliar

Percorre os três campos e devolve um dicionário com `True` ou `False` para cada um. Para os textos deste exemplo, o campo passa quando contém algo além de espaços.

Nesta expressão:

```python
bool(str(resposta.get(campo, "")).strip())
```

- `get` busca o campo; se ele não existir, usa texto vazio.
- `str` converte o valor em texto.
- `strip` remove espaços das extremidades.
- `bool` verifica se restou algum conteúdo.

Esse avaliador foi feito para os dados didáticos. Ele não valida os tipos de um esquema: por exemplo, `None` seria convertido para o texto `"None"`. Uma integração com respostas reais exigiria validação adicional de tipos e conteúdo.

### Função refinar

Recebe a resposta e a lista de campos ausentes. Normalmente, preenche esses campos com os valores de `COMPLETA`. Com `sem_melhora=True`, devolve a resposta sem completar os campos, permitindo demonstrar o limite de segurança.

### Função registro

Monta o registro de uma avaliação. A aprovação exige duas condições ao mesmo tempo: decisão de parar e motivo `criterios_satisfeitos`.

### Função ciclo_sem_parada

Contém um `while True` sem decisão de encerramento. Avalia e refina, mas continua mesmo quando os critérios já foram satisfeitos.

### Função ciclo_corrigido

Executa até o limite permitido. Em cada avaliação:

1. Aplica os critérios.
2. Encerra com aprovação se todos passaram.
3. Caso contrário, interrompe sem aprovação se atingiu o limite.
4. Se ainda puder continuar, registra as pendências e refina.

Testar a satisfação antes do limite permite aprovar uma resposta válida obtida exatamente na última avaliação.

As funções dos ciclos usam `yield`: entregam um registro por vez e podem continuar quando o próximo registro é solicitado. `return` encerra o ciclo. A função `executar` recolhe os registros em uma lista.

### Função executar

Escolhe o cenário. Para `antes`, usa `islice` para observar somente seis avaliações. Para os outros cenários, chama o ciclo corrigido com a configuração correspondente.

### Função verificar

Confere seis comportamentos: persistência do defeito, satisfação na avaliação 2, interrupção na 3 sem aprovação, resposta inicialmente completa, satisfação na última tentativa e limite de apenas uma avaliação.

### Função main

Lê os argumentos do terminal, executa o cenário e organiza o resultado em `metadados` e `registros`. A chamada `json.dumps(..., ensure_ascii=False, indent=2)` transforma esse resultado em JSON legível, preservando os acentos.

Com `--saida`, cria o arquivo e eventuais pastas necessárias. Sem esse argumento, exibe o resultado somente no terminal. Com `--verificar`, executa a checagem e encerra sem produzir um arquivo de cenário.

O bloco `if __name__ == "__main__":` inicia `main` quando o arquivo é executado diretamente.

### Bibliotecas utilizadas

| Biblioteca | Uso no exemplo |
|---|---|
| `argparse` | Ler os argumentos do terminal. |
| `json` | Produzir o texto no formato JSON. |
| `pathlib` | Trabalhar com os caminhos dos arquivos. |
| `itertools` | Limitar a observação do ciclo defeituoso. |
| `datetime` | Registrar a data e a hora em UTC. |
| `platform` | Registrar a versão do Python. |
| `hashlib` | Calcular um hash que identifica o conteúdo do script executado. |

## 11. Dificuldades comuns

| Situação | O que fazer |
|---|---|
| O terminal não encontra `python3`. | Confira se Python está instalado e se o comando disponível é `python` ou `py`. Verifique a versão antes de executar. |
| Aparece que o arquivo não foi encontrado. | Abra o terminal na pasta onde salvou `controle_parada_reflection.py` ou informe o caminho completo do script. |
| O resultado aparece, mas não existe arquivo JSON. | Acrescente `--saida nome_do_arquivo.json` ao comando de cenário. |
| O cenário `limite` termina com `aprovado: false`. | Esse é o resultado esperado: a falha de refinamento foi preparada para testar a interrupção. |
| O cenário `antes` termina, mesmo com o ciclo defeituoso. | Quem encerrou a observação foi a bancada externa, após seis avaliações. |

O exemplo demonstra controle de parada em cenários preparados. Não mede a confiabilidade geral de um LLM nem verifica a verdade do texto. O limite de avaliações também não interrompe uma chamada externa travada; essa situação exigiria um timeout próprio.
