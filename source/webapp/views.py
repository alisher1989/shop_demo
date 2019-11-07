from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from webapp.models import Product


class IndexView(ListView):
    model = Product
    template_name = 'index.html'



class ProductView(DetailView):
    model = Product
    template_name = 'product/detail.html'


class ProductCreateView(CreateView):
    model = Product
    template_name = 'product/create.html'
    fields = ('name', 'category', 'price', 'photo')
    success_url = reverse_lazy('webapp:index')
