from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UserUpdateForm, ProfileUpdateForm
import os
from fpdf import FPDF
from django.http import HttpResponse
from datetime import datetime
from fpdf import FPDF
from django.http import HttpResponse
import os
from .models import Order, OrderItem, CartItem
from django.contrib.auth.decorators import login_required
from datetime import datetime


from .models import Game, CartItem
from .forms import RegisterForm, ContactForm

# Главная страница
def index(request):
    games = Game.objects.all().order_by('-id')[:8]
    return render(request, 'main/index.html', {'games': games})


# Магазин с фильтрацией по категориям
def shop(request):
    category = request.GET.get('category')
    if category:
        games = Game.objects.filter(category=category)
    else:
        games = Game.objects.all()
    return render(request, 'main/shop.html', {'games': games, 'selected_category': category})


# Детали игры
def product_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    return render(request, 'main/product_detail.html', {'game': game})


# Контактная форма
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'main/patralis/contact_success.html')
    else:
        form = ContactForm()
    return render(request, 'main/patralis/contact.html', {'form': form})


# Добавление в корзину

def add_to_cart(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, game=game)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')


# Просмотр корзины

def cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in items)
    return render(request, 'main/cart.html', {'items': items, 'total': total})


# Удаление из корзины

def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')


# Регистрация
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


# Вход
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            error = "Неправильный логин или пароль"
            return render(request, 'auth/login.html', {'error': error})
    return render(request, 'auth/login.html')

def profile_view(request):
    return render(request, 'auth/profile.html')
# Выход
def logout_view(request):
    logout(request)
    return redirect('home')



@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'auth/edit_profile.html', context)



def generate_pdf_receipt(request, order_id):
    # Пример: данные заказа (замени на свои данные из модели)
    from .models import Order  # импортируй свою модель заказа
    order = Order.objects.get(id=order_id)

    pdf = FPDF()
    pdf.add_page()

    # Путь к TTF-файлу
    font_path = os.path.join('static', 'fonts', 'DejaVuSans.ttf')
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.set_font('DejaVu', '', 12)

    pdf.cell(200, 10, txt="GameShop - Чек", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True)
    pdf.cell(200, 10, txt=f"Номер заказа: #{order.id}", ln=True)
    pdf.cell(200, 10, txt=f"Пользователь: {order.user.username}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(80, 10, "Игра", border=1)
    pdf.cell(40, 10, "Цена", border=1, ln=True)

    pdf.set_font("Arial", size=12)
    for item in order.items.all():
        pdf.cell(80, 10, item.game.title, border=1)
        pdf.cell(40, 10, f"{item.game.price} ₸", border=1, ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(80, 10, "Итого:", border=0)
    pdf.cell(40, 10, f"{order.total_price()} ₸", border=0, ln=True)

    response = HttpResponse(pdf.output(dest='S').encode('utf-8'), content_type='application/pdf')

    response['Content-Disposition'] = f'inline; filename=receipt_order_{order.id}.pdf'
    return response

@login_required
def checkout(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('cart')

        # Создаём заказ
        order = Order.objects.create(user=request.user)
        for item in cart_items:
            OrderItem.objects.create(order=order, game=item.game)
        cart_items.delete()

        # PDF
        pdf = FPDF()
        pdf.add_page()

        # Путь к шрифту
        font_path = os.path.join('static', 'fonts', 'DejaVuSans.ttf')
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.set_font('DejaVu', '', 12)

        pdf.cell(200, 10, txt="GameShop - Чек", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True)
        pdf.cell(200, 10, txt=f"Номер заказа: #{order.id}", ln=True)
        pdf.cell(200, 10, txt=f"Пользователь: {request.user.username}", ln=True)
        pdf.ln(10)

        pdf.set_font('DejaVu', '', 12)
        pdf.cell(80, 10, "Игра", border=1)
        pdf.cell(40, 10, "Цена", border=1, ln=True)

        total = 0
        for item in order.items.all():
            pdf.cell(80, 10, item.game.title, border=1)
            pdf.cell(40, 10, f"{item.game.new_price} ₸", border=1, ln=True)
            total += item.game.new_price

        pdf.ln(10)
        pdf.cell(80, 10, "Итого:", border=0)
        pdf.cell(40, 10, f"{total} ₸", border=0, ln=True)

        # Отдаём PDF напрямую без перекодировки
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=order_{order.id}_receipt.pdf'
        response.write(pdf.output(dest='S').encode('latin-1', 'ignore'))
        return response

    return redirect('cart')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'auth/order_history.html', {'orders': orders})

from django.db.models import Q

def search_view(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Game.objects.filter(
            Q(title__icontains=query) |
            Q(category__icontains=query)
        ).distinct()
    return render(request, 'main/search_results.html', {'results': results, 'query': query})



