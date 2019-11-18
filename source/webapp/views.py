from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from webapp.forms import ManualOrderForm, OrderProductForm
from webapp.models import Product, OrderProduct, Order
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib import messages

from webapp.mixins import StatisticsMixin


class IndexView(StatisticsMixin, ListView):
    model = Product
    template_name = 'index.html'

    def get_queryset(self):
        return Product.objects.filter(in_order=True)
    #
    # def get(self, request, *args, **kwargs):
    #     messages.set_level(request, messages.DEBUG)
    #     messages.success(request, 'test')
    #     messages.debug(request, 'test')
    #     messages.info(request, 'test')
    #     messages.error(request, 'test')
    #     messages.warning(request, 'test')
    #     messages.add_message(request, 60, 'test')
    #     return super().get(request, *args, **kwargs)


class ProductView(StatisticsMixin, DetailView):
    model = Product
    template_name = 'product/detail.html'


class ProductCreateView(PermissionRequiredMixin, StatisticsMixin, CreateView):
    model = Product
    template_name = 'product/create.html'
    fields = ('name', 'category', 'price', 'photo', 'in_order')
    success_url = reverse_lazy('webapp:index')
    permission_required = 'webapp.add_product'
    permission_denied_message = '403 Доступ запрещен'

    # def dispatch(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return redirect('accounts:login')
    #     if request.user.has_perm('webapp.add_product'):
    #         return super().dispatch(request, *args, **kwargs)
    #     raise PermissionDenied('403 Permission denied')


class ProductUpdateView(PermissionRequiredMixin, StatisticsMixin, UpdateView):
    model = Product
    template_name = 'product/update.html'
    fields = ('name', 'category', 'price', 'photo', 'in_order')
    context_object_name = 'product'
    permission_required = 'webapp.change_product'
    permission_denied_message = '403 Доступ запрещен'

    def get_success_url(self):
        return reverse('webapp:product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(PermissionRequiredMixin, LoginRequiredMixin, StatisticsMixin, DeleteView):
    model = Product
    template_name = 'product/delete.html'
    success_url = reverse_lazy('webapp:index')
    context_object_name = 'product'
    permission_required = 'webapp.delete_product'
    permission_denied_message = '403 Доступ запрещен'

    def delete(self, request, *args, **kwargs):
        product = self.object = self.get_object()
        product.in_order = False
        product.save()
        return HttpResponseRedirect(self.get_success_url())


class BasketChangeView(StatisticsMixin, View):

    def get(self, request, *args, **kwargs):
        products = request.session.get('products', [])

        pk = request.GET.get('pk')
        action = request.GET.get('action')
        next_url = request.GET.get('next', reverse('webapp:index'))

        if action == 'add':
            product = get_object_or_404(Product, pk=pk)
            if product.in_order:
                products.append(pk)
        else:
            for product_pk in products:
                if product_pk == pk:
                    products.remove(product_pk)
                    break

        request.session['products'] = products
        request.session['products_count'] = len(products)

        return redirect(next_url)


class BasketView(StatisticsMixin, CreateView):
    model = Order
    fields = ('first_name', 'last_name', 'phone', 'email')
    template_name = 'product/basket.html'
    success_url = reverse_lazy('webapp:index')

    def get_context_data(self, **kwargs):
        basket, basket_total = self._prepare_basket()
        kwargs['basket'] = basket
        kwargs['basket_total'] = basket_total
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        if self._basket_empty():
            form.add_error(None, 'В корзине отсутствуют товары!')
            return self.form_invalid(form)
        response = super().form_valid(form)
        self._save_order_products()
        self._clean_basket()
        messages.add_message(self.request, messages.SUCCESS, 'Заказ оформлен!')
        return response

    def _prepare_basket(self):
        totals = self._get_totals()
        basket = []
        basket_total = 0
        for pk, qty in totals.items():
            product = Product.objects.get(pk=int(pk))
            total = product.price * qty
            basket_total += total
            basket.append({'product': product, 'qty': qty, 'total': total})
        return basket, basket_total

    def _get_totals(self):
        products = self.request.session.get('products', [])
        totals = {}
        for product_pk in products:
            if product_pk not in totals:
                totals[product_pk] = 0
            totals[product_pk] += 1
        return totals

    def _basket_empty(self):
        products = self.request.session.get('products', [])
        return len(products) == 0

    def _save_order_products(self):
        totals = self._get_totals()
        for pk, qty in totals.items():
            OrderProduct.objects.create(product_id=pk, order=self.object, amount=qty)

    def _clean_basket(self):
        if 'products' in self.request.session:
            self.request.session.pop('products')
        if 'products_count' in self.request.session:
            self.request.session.pop('products_count')


class OrderListView(ListView):
    template_name = 'order/list.html'

    def get_queryset(self):
        if self.request.user.has_perm('webapp.view_order'):
            return Order.objects.all().order_by('-created_at')
        return self.request.user.orders.all()


class OrderDetailView(PermissionRequiredMixin, DetailView):
    template_name = 'order/detail.html'
    permission_required = 'webapp.view_order'
    permission_denied_message = '403 Доступ запрещен'

    def get_queryset(self):
        if self.request.user.has_perm('webapp.view_order'):
            return Order.objects.all()
        return self.request.user.orders.all()


class OrderCreateView(PermissionRequiredMixin, CreateView):
    model = Order
    template_name = 'order/create.html'
    form_class = ManualOrderForm
    success_url = reverse_lazy('webapp:index')
    permission_required = 'webapp.add_order'
    permission_denied_message = '403 Доступ запрещен'


class OrderUpdateView(PermissionRequiredMixin, UpdateView):
    model = Order
    template_name = 'order/update.html'
    form_class = ManualOrderForm
    context_object_name = 'order'
    permission_required = 'webapp.change_order'
    permission_denied_message = '403 Доступ запрещен'

    def get_success_url(self):
        return reverse('webapp:order_detail', kwargs={'pk': self.object.pk})


class OrderDeliverView(View):
    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        order.status = 'delivered'
        order.save()
        return redirect(reverse('webapp:order_detail', kwargs={'pk': order.pk}))


class OrderCancelView(View):
    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        order.status = 'canceled'
        order.save()
        return redirect(reverse('webapp:order_detail', kwargs={'pk': order.pk}))


class OrderProductCreateView(PermissionRequiredMixin, CreateView):
    model = OrderProduct
    form_class = OrderProductForm
    template_name = 'order_product/create.html'
    permission_required = 'webapp.add_orderproduct'
    permission_denied_message = '403 Доступ запрещен'

    def form_valid(self, form):
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        name_of_product = form.cleaned_data.get('product')
        amount_of_product = form.cleaned_data.get('amount')
        self.object = form.save(commit=False)
        self.object.order = order
        self.object.product = name_of_product
        self.object.amount = amount_of_product
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('webapp:order_detail', kwargs={'pk': self.object.order.pk})


class OrderProductUpdateView(PermissionRequiredMixin, UpdateView):
    model = OrderProduct
    form_class = OrderProductForm
    template_name = 'order_product/update.html'
    permission_required = 'webapp.change_orderproduct'
    permission_denied_message = '403 Доступ запрещен'

    def get_initial(self):
        print(self.kwargs)
        initial = super().get_initial()
        return initial

    def get(self, request, *args, **kwargs):
        print('here')
        print(self.kwargs)
        print(kwargs)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('webapp:order_detail', kwargs={'pk': self.object.order.pk})


class OrderProductDeleteView(PermissionRequiredMixin, DeleteView):
    model = OrderProduct
    context_object_name = 'order_product'
    pk_kwargs_url = 'pk'
    permission_required = 'webapp.delete_orderproduct'
    permission_denied_message = '403 Доступ запрещен'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(reverse('webapp:order_detail', kwargs={'pk': self.object.order.pk}))

    # def get_queryset(self):
    #     return Product.objects.filter(in_order=True)




