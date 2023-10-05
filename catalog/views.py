from django.shortcuts import render
from .models import Links, User
from catalog.forms import EnterURLForm
from .scraper import Spider
from .scraper import Crawler, create_async_crawler
import asyncio
import httpx

# Create your views here.
def home(request):

    TAM = 10
    retrieved_urls = []
    # retrieved_externals = []
    u_id = request.session.get('u_id', -1)
    user = User()
    if u_id == -1:
        user = User.objects.create()
        u_id = user.uid
        request.session['u_id'] = u_id
    else:
        user = User.objects.get(uid=u_id)

    if request.method == 'POST':

        form = EnterURLForm(request.POST)

        if form.is_valid():
            crawl = Spider(form.cleaned_data['url'])
            crawl.crawler()
            link = Links(url=form.cleaned_data['url'], user=u_id)
            link.save()
            TAM = int(form.cleaned_data['pag'])
            retrieved_urls = crawl.tfidf_vectorize(tam=TAM)
    else:

        form = EnterURLForm(initial={'url': 'https://www.campograndenews.com.br/cidades/capital/pai-de-maniaco-entrega-arma-do-filho-a-policia'})


    links_list = Links.objects.filter(user__exact=u_id)
    message = """O processo pode levar alguns segundos ou até minutos
dependendo da quantidade de links encontrados nas páginas, desse modo, a página permanecerá
irresposiva durante esse período. Peço que tenha paciência e adianto que
estou trabalhando para tornar o processo mais rápido."""

    context = {
        'links_list': links_list,
        'form': form,
        'retrieved_urls': retrieved_urls,
        'total_pages': TAM,
        'attention_message': message,
    }

    return render(request, 'home.html', context=context)

def history(request):

    u_id = request.session.get('u_id', -1)
    user = User()
    if u_id == -1:
        user = User.objects.create()
        u_id = user.uid
        request.session['u_id'] = u_id
    else:
        user = User.objects.get(uid=u_id)

    links_list = Links.objects.filter(user__exact=u_id)
    context = {
        'links_list': links_list,
    }

    return render(request, 'history.html', context=context)

def beta(request):

    TAM = 10
    retrieved_urls = []
    # retrieved_externals = []
    u_id = request.session.get('u_id', -1)
    user = User()
    if u_id == -1:
        user = User.objects.create()
        u_id = user.uid
        request.session['u_id'] = u_id
    else:
        user = User.objects.get(uid=u_id)

    if request.method == 'POST':

        form = EnterURLForm(request.POST)

        if form.is_valid():
            crawler = asyncio.run(create_async_crawler(form.cleaned_data['url']))
            link = Links(url=form.cleaned_data['url'], user=u_id)
            link.save()
            TAM = int(form.cleaned_data['pag'])
            retrieved_urls = crawler.tfidf_vectorize(tam=TAM)
    else:

        form = EnterURLForm(initial={'url': 'https://www.campograndenews.com.br/cidades/capital/pai-de-maniaco-entrega-arma-do-filho-a-policia'})


    links_list = Links.objects.filter(user__exact=u_id)
    message = """Essa é uma versão de testes para desenvolvimento de um crawler
mais rápido e eficiente. Por enquanto ela ainda está demorando mais tempo, mas
seus resultados podem ser mais precisos."""

    context = {
        'links_list': links_list,
        'form': form,
        'retrieved_urls': retrieved_urls,
        'total_pages': TAM,
        'attention_message': message,
    }

    return render(request, 'home.html', context=context)
