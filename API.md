
## Documentação da API

Essa API realiza _Crawling_ com múltiplas _threads_. Ela ainda está em processo de melhoria, por isso pode demorar mais do que o desejado para fazer o processo de _Crawling_ e _Scraping_.

#### - `scraper.Spider(seed_url)` - Cria uma instância do objeto Spider:

```python
  spider = scraper.Spider(seed_url)
```

| Parâmetro   | Tipo       | Descrição                           |
| :---------- | :--------- | :---------------------------------- |
| `seed_url` | `string` | **Obrigatório**. URL de onde se iniciará o crawling. |

#### - `scraper.Spider.crawler()` - Inicia o processo de Crawling

```python
  spider.crawler()
```

#### - `scraper.Spider.pages` - Retorna um dicionário com o conteúdo de todas as páginas encontradas

```python
  spider.pages

{'url': [],
'language': [],
'title': [],
'content': [] }
```

| Chave   | Tipo       | Descrição                                   |
| :---------- | :--------- | :------------------------------------------ |
| `url`      | `[str,]` | Retorna uma lista com todos os URLs encontrados durante o crawling, seguindo a sequência|
| `language`      | `[str,]` | Retorna uma lista com o conteúdo da tag `<lang>` de cada página, seguindo a sequência|
| `title`      | `[str,]` | Retorna uma lista com o conteúdo da tag `<title>` de cada página, seguindo a sequência|
| `content`      | `[str,]` | Retorna uma lista com o conteúdo de todas as tags `<p>` em uma única `string` encontradas de cada página, seguindo a sequência|

#### Retornar os dados para a mesma página

```python
  spider.pages['url'][<id>]
  spider.pages['language'][<id>]
  spider.pages['title'][<id>]
  spider.pages['content'][<id>]
```

| Parâmetro   | Tipo       | Descrição                                   |
| :---------- | :--------- | :------------------------------------------ |
| `id`      | `int` | **Obrigatório**. O índice do item desejado |

#### - `scraper.Spider.tfidf_vectorize(tam=10)`

Retorna uma lista de tuplas dos `tam` primeiros resultados contendo título da página, URL e conteúdo da página.

| Parâmetro   | Tipo       | Descrição                                   |
| :---------- | :--------- | :------------------------------------------ |
| `tam`      | `int` | `default=10`. Tamanho da lista a ser retornada (quantidade de ítens/resultados a ser exibido)|

```python
  tfidf_results = spider.tfidf_vectorize(tam=10)
```
O valor atribuído a `tfidf_results` é uma lista de `10` (`tam`) tuplas no formato `(title, url, content)`.

#### - `scraper.Spider.get_ranks()`

Calcula os valores de PageRanks para os links encontrados no Crawling. _**Não** se recomanda calcular o PageRank das páginas caso elas sejam muitas, pois o cálculo pode levar algum tempo, por enquanto._

#### - `scraper.Spider.ranks` - Dicionário com os valores calculados por `scraper.Spider.get_ranks()`

Calcula os valores de PageRanks para os links encontrados no Crawling.
```python
  spider.ranks

{'<page_url>': <rank_value>,
  }
```

| Variável   | Tipo       | Descrição                                   |
| :---------- | :--------- | :------------------------------------------ |
| `page_url`      | `string` | **Chave** do dicionário, representa o URL da página |
| `rank_value`      | `float` | **Valor** atribuído à chave: representa o valor final do _PageRank_ calculado |

#### - `scraper.Spider.sort(tam=10)`

Retorna uma lista de tuplas criada a partir do dicionário `scraper.Spider.ranks` e ordenada de forma decrescente por `rank_value` (valor do _PageRank_).

| Parâmetro   | Tipo       | Descrição                                   |
| :---------- | :--------- | :------------------------------------------ |
| `tam`      | `int` | `default=10`. Tamanho da lista a ser retornada (quantidade de ítens/resultados a ser exibido)|

```python
  sorted_pageranks = spider.sort(tam=10)
```
O valor atribuído a `sorted_pageranks` é uma lista de `10` (`tam=10`) tuplas no formato `('<page_url>', <rank_value>)`, sendo os `10` maiores valores de `rank_value`. Onde `page_url` é uma `string` que representa a URL da página e `rank_value` é um `float` que representa o valor de _PageRank_.
.
