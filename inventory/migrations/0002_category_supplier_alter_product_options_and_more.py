# Generated by Django 5.2.3 on 2025-06-10 12:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="分类名称"
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="描述")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
            ],
            options={
                "verbose_name": "商品分类",
                "verbose_name_plural": "商品分类",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Supplier",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="供应商名称")),
                (
                    "contact_person",
                    models.CharField(blank=True, max_length=50, verbose_name="联系人"),
                ),
                (
                    "phone",
                    models.CharField(blank=True, max_length=20, verbose_name="电话"),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, verbose_name="邮箱"),
                ),
                ("address", models.TextField(blank=True, verbose_name="地址")),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="是否启用"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
            ],
            options={
                "verbose_name": "供应商",
                "verbose_name_plural": "供应商",
                "ordering": ["name"],
            },
        ),
        migrations.AlterModelOptions(
            name="product",
            options={
                "ordering": ["-updated_at"],
                "verbose_name": "商品",
                "verbose_name_plural": "商品",
            },
        ),
        migrations.AddField(
            model_name="product",
            name="cost_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="成本价",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, null=True, verbose_name="创建时间"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="创建人",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="description",
            field=models.TextField(blank=True, default="", verbose_name="商品描述"),
        ),
        migrations.AddField(
            model_name="product",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="是否启用"),
        ),
        migrations.AddField(
            model_name="product",
            name="low_stock_threshold",
            field=models.PositiveIntegerField(default=10, verbose_name="库存预警值"),
        ),
        migrations.AlterField(
            model_name="product",
            name="name",
            field=models.CharField(max_length=100, verbose_name="商品名称"),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                decimal_places=2, max_digits=10, verbose_name="单价"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="quantity",
            field=models.PositiveIntegerField(verbose_name="库存数量"),
        ),
        migrations.AlterField(
            model_name="product",
            name="sku",
            field=models.CharField(max_length=30, unique=True, verbose_name="商品编码"),
        ),
        migrations.AlterField(
            model_name="product",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="更新时间"),
        ),
        migrations.AddField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="inventory.category",
                verbose_name="分类",
            ),
        ),
        migrations.CreateModel(
            name="StockMovement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "movement_type",
                    models.CharField(
                        choices=[
                            ("in", "入库"),
                            ("out", "出库"),
                            ("adjustment", "调整"),
                            ("return", "退货"),
                        ],
                        max_length=20,
                        verbose_name="变动类型",
                    ),
                ),
                ("quantity", models.IntegerField(verbose_name="变动数量")),
                (
                    "old_quantity",
                    models.PositiveIntegerField(verbose_name="变动前数量"),
                ),
                (
                    "new_quantity",
                    models.PositiveIntegerField(verbose_name="变动后数量"),
                ),
                (
                    "reason",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="变动原因"
                    ),
                ),
                (
                    "reference_no",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="参考单号"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="操作人",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="movements",
                        to="inventory.product",
                        verbose_name="商品",
                    ),
                ),
            ],
            options={
                "verbose_name": "库存变动记录",
                "verbose_name_plural": "库存变动记录",
                "ordering": ["-created_at"],
            },
        ),
    ]
