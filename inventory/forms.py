from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Product, Category, StockMovement, Supplier
import re


class CustomAuthenticationForm(AuthenticationForm):
    """自定义登录表单"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入用户名'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入密码'
        })


class ProductForm(forms.ModelForm):
    """商品表单 - 修复版本"""

    class Meta:
        model = Product
        # 明确指定所有字段，避免动态添加导致的问题
        fields = [
            'name', 'sku', 'quantity', 'price', 'category',
            'description', 'cost_price', 'low_stock_threshold', 'is_active'
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入商品名称',
                'required': True
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入商品编码，如：PRD-001',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '请输入库存数量',
                'required': True
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '请输入销售价格',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入商品描述（可选）'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '请输入成本价格（可选）'
            }),
            'low_stock_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '10'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

        labels = {
            'name': '商品名称',
            'sku': '商品编码',
            'quantity': '库存数量',
            'price': '销售价格',
            'category': '商品分类',
            'description': '商品描述',
            'cost_price': '成本价格',
            'low_stock_threshold': '库存预警值',
            'is_active': '启用状态',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置字段为可选（除了必填字段）
        self.fields['category'].required = False
        self.fields['category'].empty_label = '请选择分类'
        self.fields['description'].required = False
        self.fields['cost_price'].required = False
        self.fields['low_stock_threshold'].required = False
        self.fields['is_active'].required = False

        # 设置初始值
        if not self.instance.pk:  # 新建时设置默认值
            self.fields['low_stock_threshold'].initial = 10
            self.fields['is_active'].initial = True

    def clean_sku(self):
        """验证SKU格式和唯一性"""
        sku = self.cleaned_data.get('sku')
        if sku:
            # 转为大写并去除空格
            sku = sku.upper().strip()

            # SKU格式验证
            if not re.match(r'^[A-Za-z0-9\-_]+$', sku):
                raise ValidationError('商品编码只能包含字母、数字、连字符和下划线')

            # 检查唯一性（排除自己）
            existing_product = Product.objects.filter(sku=sku).exclude(
                pk=self.instance.pk if self.instance.pk else None)
            if existing_product.exists():
                raise ValidationError(f'商品编码 "{sku}" 已存在，请使用其他编码')

        return sku

    def clean_price(self):
        """验证价格"""
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise ValidationError('销售价格必须大于0')
        return price

    def clean_cost_price(self):
        """验证成本价格"""
        cost_price = self.cleaned_data.get('cost_price')
        if cost_price is not None and cost_price < 0:
            raise ValidationError('成本价格不能为负数')
        return cost_price

    def clean_quantity(self):
        """验证库存数量"""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise ValidationError('库存数量不能为负数')
        return quantity

    def clean_low_stock_threshold(self):
        """验证库存预警值"""
        threshold = self.cleaned_data.get('low_stock_threshold')
        if threshold is not None and threshold < 1:
            raise ValidationError('库存预警值必须大于0')
        return threshold

    def clean(self):
        """表单整体验证"""
        cleaned_data = super().clean()
        cost_price = cleaned_data.get('cost_price')
        price = cleaned_data.get('price')

        # 如果同时填写了成本价和销售价，检查销售价是否高于成本价
        if cost_price is not None and price is not None:
            if price <= cost_price:
                raise ValidationError('销售价格应该高于成本价格')

        return cleaned_data

    def save(self, commit=True):
        """保存时设置默认值"""
        instance = super().save(commit=False)

        # 确保必要字段有值
        if not instance.low_stock_threshold:
            instance.low_stock_threshold = 10

        if instance.is_active is None:
            instance.is_active = True

        if commit:
            instance.save()
        return instance


class CategoryForm(forms.ModelForm):
    """分类表单"""

    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入分类名称',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入分类描述（可选）'
            }),
        }
        labels = {
            'name': '分类名称',
            'description': '分类描述',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False

    def clean_name(self):
        """验证分类名称唯一性"""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            existing_category = Category.objects.filter(name=name).exclude(
                pk=self.instance.pk if self.instance.pk else None)
            if existing_category.exists():
                raise ValidationError(f'分类名称 "{name}" 已存在，请使用其他名称')
        return name


class StockAdjustmentForm(forms.Form):
    """库存调整表单"""
    ADJUSTMENT_TYPES = [
        ('add', '增加库存'),
        ('reduce', '减少库存'),
        ('set', '设置库存'),
    ]

    adjustment_type = forms.ChoiceField(
        label='调整类型',
        choices=ADJUSTMENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity = forms.IntegerField(
        label='数量',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入数量'
        })
    )
    reason = forms.CharField(
        label='调整原因',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入调整原因（可选）'
        })
    )
    reference_no = forms.CharField(
        label='参考单号',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入参考单号（可选）'
        })
    )

    def clean_quantity(self):
        """验证调整数量"""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise ValidationError('调整数量不能为负数')
        return quantity


class ProductSearchForm(forms.Form):
    """商品搜索表单"""
    SEARCH_FIELDS = [
        ('all', '全部字段'),
        ('name', '商品名称'),
        ('sku', '商品编码'),
        ('category', '商品分类'),
    ]

    STOCK_STATUS = [
        ('all', '全部状态'),
        ('in_stock', '有库存'),
        ('low_stock', '库存不足'),
        ('out_of_stock', '缺货'),
    ]

    q = forms.CharField(
        label='搜索关键词',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入搜索关键词'
        })
    )
    search_field = forms.ChoiceField(
        label='搜索字段',
        choices=SEARCH_FIELDS,
        required=False,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    stock_status = forms.ChoiceField(
        label='库存状态',
        choices=STOCK_STATUS,
        required=False,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    price_min = forms.DecimalField(
        label='最低价格',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '最低价格'
        })
    )
    price_max = forms.DecimalField(
        label='最高价格',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '最高价格'
        })
    )
    category = forms.ModelChoiceField(
        label='商品分类',
        queryset=Category.objects.all(),
        required=False,
        empty_label='全部分类',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean(self):
        """验证价格范围"""
        cleaned_data = super().clean()
        price_min = cleaned_data.get('price_min')
        price_max = cleaned_data.get('price_max')

        if price_min is not None and price_max is not None:
            if price_min > price_max:
                raise ValidationError('最低价格不能大于最高价格')

        return cleaned_data


class SupplierForm(forms.ModelForm):
    """供应商表单"""

    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入供应商名称',
                'required': True
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入联系人姓名'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入联系电话'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入邮箱地址'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入地址'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': '供应商名称',
            'contact_person': '联系人',
            'phone': '联系电话',
            'email': '邮箱地址',
            'address': '地址',
            'is_active': '启用状态',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置可选字段
        self.fields['contact_person'].required = False
        self.fields['phone'].required = False
        self.fields['email'].required = False
        self.fields['address'].required = False
        self.fields['is_active'].required = False

        # 设置默认值
        if not self.instance.pk:
            self.fields['is_active'].initial = True

    def clean_name(self):
        """验证供应商名称唯一性"""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            existing_supplier = Supplier.objects.filter(name=name).exclude(
                pk=self.instance.pk if self.instance.pk else None)
            if existing_supplier.exists():
                raise ValidationError(f'供应商名称 "{name}" 已存在，请使用其他名称')
        return name

    def clean_email(self):
        """验证邮箱格式"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
        return email

    def clean_phone(self):
        """验证电话号码格式"""
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = phone.strip()
            # 简单的电话号码验证
            if not re.match(r'^[0-9\-\+\(\)\s]+$', phone):
                raise ValidationError('请输入有效的电话号码')
        return phone