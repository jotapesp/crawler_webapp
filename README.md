# Web Ranker

(PT-BR)
Esse é um Web Crawler escrito em Python, utilizando o framework Django. O _app_ faz o _scrape_ das páginas procurando por _links_ e acessando-os, repetindo o processo em até 5 níveis. O _scraping_ é feito por uma [API](https://github.com/jotapesp/crawler_webapp/blob/main/API.md) criada separadamente, que também _rankeia_ os resultados no final utilizando [TF-IDF](https://towardsdatascience.com/tf-idf-for-document-ranking-from-scratch-in-python-on-real-world-dataset-796d339a4089) simples utilizando a biblioteca [`Sklearn`](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html).

### Feito com

[![Python](https://img.shields.io/badge/Python-000?style=for-the-badge&logo=python)](https://docs.python.org/3.10/)
[![Django](https://img.shields.io/badge/Django-000?style=for-the-badge&logo=django)](https://docs.djangoproject.com/en/4.2/)

### Instalação

(PT-BR)
* Faça o download dos arquivos um por um em um mesmo diretório ou clone o repositório utilizando o comando:
  >`git clone https://github.com/jotapesp/pong-game.git`

* Faça a instalação das dependências listadas em [`requirements.txt`](https://github.com/jotapesp/crawler_webapp/blob/main/requirements.txt) manualmente ou utilize o comando:
  >`pip install -r requirements.txt`

* Para rodar o app, siga as instruções em Como Usar.

### Como usar

(PT-BR)
* O app foi feito utilizando o framework Django do Python, portanto, precisa-se seguir os seguintes passos para rodar o servidor local e a aplicação:
  * No terminal, vá até a pasta local do app onde está localizado um arquivo de nome `manage.py`
  * Na linha de comando do terminal, entre o comando:
    > `python3 manage.py runserver`

* Abra um navegador web de sua preferência e pela barra de endereços, acesse a URL: `http://127.0.0.1:8000/`.
* Na barra encontrada na homepage, entre o link pelo qual deseja iniciar o Web Crawling e clique em `Começar`.
* O processo de crawling se dará início e pode levar alguns minutos dependendo da quantidade de links encontrada.

### Web Crawling

* O processo de crawling e scraping é feito por uma API desenvolvida a parte localizada em `catalog/scraper.py`
* A documentação da API é encontrada [aqui](https://github.com/jotapesp/crawler_webapp/blob/main/API.md)
