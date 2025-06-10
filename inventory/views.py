from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Product, Category
from .forms import ProductForm
import logging

logger = logging.getLogger(__name__)


@login_required
def product_create(request):
    """创建商品视图 - 修复重定向问题"""
    if request.method == 'POST':
        form = ProductForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    product = form.save(commit=False)
                    product.created_by = request.user
                    product.save()

                    messages.success(
                        request,
                        f'商品 "{product.name}" 创建成功！SKU: {product.sku}'
                    )

                    # 修复重定向 - 明确指定重定向到商品列表页
                    return redirect('inventory:product_list')

            except IntegrityError as e:
                logger.error(f"Product creation failed - IntegrityError: {e}")
                if 'sku' in str(e).lower():
                    form.add_error('sku', '该商品编码已存在，请使用其他编码')
                else:
                    form.add_error(None, '保存失败，请检查数据完整性')

            except ValidationError as e:
                logger.error(f"Product creation failed - ValidationError: {e}")
                form.add_error(None, f'数据验证失败: {e}')

            except Exception as e:
                logger.error(f"Product creation failed - Unexpected error: {e}")
                form.add_error(None, '系统错误，请稍后重试')
        else:
            # 表单验证失败，记录错误详情
            logger.warning(f"Product form validation failed: {form.errors}")

            # 为用户提供友好的错误提示
            error_messages = []
            for field, errors in form.errors.items():
                if field == '__all__':
                    for error in errors:
                        error_messages.append(f"表单验证错误: {error}")
                else:
                    field_label = form.fields.get(field, {}).label or field
                    for error in errors:
                        error_messages.append(f"{field_label}: {error}")

            if error_messages:
                for msg in error_messages:
                    messages.error(request, msg)
            else:
                messages.error(request, '表单填写有误，请检查后重试')
    else:
        form = ProductForm()

    context = {
        'form': form,
        'action': '添加商品',
        'categories': Category.objects.all()
    }
    return render(request, 'inventory/product_form.html', context)


@login_required
def product_edit(request, pk):
    """编辑商品视图 - 修复重定向问题"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            try:
                with transaction.atomic():
                    updated_product = form.save()

                    messages.success(
                        request,
                        f'商品 "{updated_product.name}" 更新成功！'
                    )

                    # 编辑成功后重定向到商品详情页
                    return redirect('inventory:product_detail', pk=updated_product.pk)

            except IntegrityError as e:
                logger.error(f"Product update failed - IntegrityError: {e}")
                if 'sku' in str(e).lower():
                    form.add_error('sku', '该商品编码已被其他商品使用')
                else:
                    form.add_error(None, '更新失败，请检查数据完整性')

            except ValidationError as e:
                logger.error(f"Product update failed - ValidationError: {e}")
                form.add_error(None, f'数据验证失败: {e}')

            except Exception as e:
                logger.error(f"Product update failed - Unexpected error: {e}")
                form.add_error(None, '系统错误，请稍后重试')
        else:
            # 表单验证失败处理
            logger.warning(f"Product update form validation failed: {form.errors}")

            error_messages = []
            for field, errors in form.errors.items():
                if field == '__all__':
                    for error in errors:
                        error_messages.append(f"表单验证错误: {error}")
                else:
                    field_label = form.fields.get(field, {}).label or field
                    for error in errors:
                        error_messages.append(f"{field_label}: {error}")

            if error_messages:
                for msg in error_messages:
                    messages.error(request, msg)
            else:
                messages.error(request, '表单填写有误，请检查后重试')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'action': '编辑商品',
        'categories': Category.objects.all()
    }
    return render(request, 'inventory/product_form.html', context)


@login_required
def product_detail(request, pk):
    """商品详情视图"""
    product = get_object_or_404(Product, pk=pk)

    context = {
        'product': product,
    }
    return render(request, 'inventory/product_detail.html', context)


@login_required
def product_list(request):
    """商品列表视图"""
    from django.db import models
    from django.core.paginator import Paginator

    products = Product.objects.all().order_by('-updated_at')

    # 搜索功能
    query = request.GET.get('q', '')
    stock_status = request.GET.get('stock_status', '')

    if query:
        products = products.filter(
            models.Q(name__icontains=query) |
            models.Q(sku__icontains=query)
        )

    # 库存状态过滤
    if stock_status == 'in_stock':
        products = products.filter(quantity__gt=models.F('low_stock_threshold'))
    elif stock_status == 'low_stock':
        products = products.filter(
            quantity__lte=models.F('low_stock_threshold'),
            quantity__gt=0
        )
    elif stock_status == 'out_of_stock':
        products = products.filter(quantity=0)

    # 分页
    paginator = Paginator(products, 20)  # 每页显示20个商品
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # 统计信息
    all_products = Product.objects.all()
    stats = {
        'total_products': all_products.count(),
        'low_stock_products': all_products.filter(
            quantity__lte=models.F('low_stock_threshold'),
            quantity__gt=0
        ).count(),
        'out_of_stock_products': all_products.filter(quantity=0).count(),
    }

    context = {
        'products': products_page,
        'query': query,
        'stats': stats,
        'current_filters': {
            'q': query,
            'stock_status': stock_status
        }
    }
    return render(request, 'inventory/product_list.html', context)


@login_required
def product_delete(request, pk):
    """删除商品视图"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product_name = product.name
        try:
            product.delete()
            messages.success(request, f'商品 "{product_name}" 已成功删除')

            # 删除后重定向到商品列表
            return redirect('inventory:product_list')

        except Exception as e:
            logger.error(f"Product deletion failed: {e}")
            messages.error(request, f'删除商品失败: {str(e)}')

            # 删除失败，重定向到商品详情页
            return redirect('inventory:product_detail', pk=pk)

    context = {
        'product': product,
    }
    return render(request, 'inventory/product_confirm_delete.html', context)


# 其他可能需要的占位符视图函数（根据你的urls.py）
@login_required
def stock_adjustment(request, pk):
    """库存调整视图 - 占位符"""
    product = get_object_or_404(Product, pk=pk)
    messages.info(request, '库存调整功能正在开发中')
    return redirect('inventory:product_detail', pk=pk)


@login_required
def category_list(request):
    """分类列表视图 - 占位符"""
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'inventory/category_list.html', context)


@login_required
def category_create(request):
    """创建分类视图 - 占位符"""
    messages.info(request, '分类创建功能正在开发中')
    return redirect('inventory:category_list')


@login_required
def category_edit(request, pk):
    """编辑分类视图 - 占位符"""
    messages.info(request, '分类编辑功能正在开发中')
    return redirect('inventory:category_list')


@login_required
def stock_report(request):
    """库存报告视图 - 占位符"""
    messages.info(request, '库存报告功能正在开发中')
    return redirect('inventory:product_list')


@login_required
def movement_history(request):
    """库存变动历史视图 - 占位符"""
    messages.info(request, '库存变动历史功能正在开发中')
    return redirect('inventory:product_list')


@login_required
def supplier_list(request):
    """供应商列表视图 - 占位符"""
    messages.info(request, '供应商管理功能正在开发中')
    return redirect('inventory:product_list')


@login_required
def supplier_create(request):
    """创建供应商视图 - 占位符"""
    messages.info(request, '供应商创建功能正在开发中')
    return redirect('inventory:supplier_list')


@login_required
def export_products_csv(request):
    """导出商品CSV - 占位符"""
    messages.info(request, 'CSV导出功能正在开发中')
    return redirect('inventory:product_list')


@login_required
def export_stock_movements_csv(request):
    """导出库存变动CSV - 占位符"""
    messages.info(request, '库存变动导出功能正在开发中')
    return redirect('inventory:product_list')


def api_product_search(request):
    """商品搜索API - 占位符"""
    from django.http import JsonResponse
    return JsonResponse({'message': 'API功能正在开发中'})


def api_quick_stock_update(request):
    """快速库存更新API - 占位符"""
    from django.http import JsonResponse
    return JsonResponse({'message': 'API功能正在开发中'})


# 登录登出视图
from django.contrib.auth import authenticate, login, logout
from .forms import CustomAuthenticationForm


def login_view(request):
    """登录视图"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'inventory:product_list')
                return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """登出视图"""
    logout(request)
    messages.success(request, '已成功退出登录')
    return redirect('inventory:login')