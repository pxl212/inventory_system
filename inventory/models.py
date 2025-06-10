from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.urls import reverse


class Category(models.Model):
    """商品分类模型"""
    name = models.CharField('分类名称', max_length=50, unique=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """商品模型 - 向后兼容版本"""
    # 保持原有字段
    name = models.CharField('商品名称', max_length=100)
    sku = models.CharField('商品编码', max_length=30, unique=True)
    quantity = models.PositiveIntegerField('库存数量')
    price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    # 新增字段（设置默认值以保证兼容性）
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, blank=True, verbose_name='分类')
    description = models.TextField('商品描述', blank=True, default='')
    cost_price = models.DecimalField('成本价', max_digits=10, decimal_places=2,
                                     null=True, blank=True)
    low_stock_threshold = models.PositiveIntegerField('库存预警值', default=10)
    is_active = models.BooleanField('是否启用', default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True, null=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse('inventory:product_detail', kwargs={'pk': self.pk})

    @property
    def is_low_stock(self):
        """判断是否库存不足"""
        return self.quantity <= self.low_stock_threshold

    @property
    def stock_status(self):
        """获取库存状态"""
        if self.quantity == 0:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        return 'in_stock'

    @property
    def stock_value(self):
        """计算库存价值"""
        return self.quantity * self.price


class StockMovement(models.Model):
    """库存变动记录"""
    MOVEMENT_TYPES = [
        ('in', '入库'),
        ('out', '出库'),
        ('adjustment', '调整'),
        ('return', '退货'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name='商品', related_name='movements')
    movement_type = models.CharField('变动类型', max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField('变动数量')  # 正数为入库，负数为出库
    old_quantity = models.PositiveIntegerField('变动前数量')
    new_quantity = models.PositiveIntegerField('变动后数量')
    reason = models.CharField('变动原因', max_length=200, blank=True)
    reference_no = models.CharField('参考单号', max_length=50, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name='操作人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '库存变动记录'
        verbose_name_plural = '库存变动记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()}: {self.quantity}"


class Supplier(models.Model):
    """供应商模型"""
    name = models.CharField('供应商名称', max_length=100)
    contact_person = models.CharField('联系人', max_length=50, blank=True)
    phone = models.CharField('电话', max_length=20, blank=True)
    email = models.EmailField('邮箱', blank=True)
    address = models.TextField('地址', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = '供应商'
        ordering = ['name']

    def __str__(self):
        return self.name