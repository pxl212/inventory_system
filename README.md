# Django库存管理系统 - 项目打包部署指南

## 📦 项目打包步骤

### 1. 创建项目依赖文件

在项目根目录创建 `requirements.txt` 文件：

```bash
# 在虚拟环境中运行
pip freeze > requirements.txt
```

或者手动创建 `requirements.txt`：
```txt
Django>=5.0,<6.0
```

### 2. 创建环境配置文件

创建 `.env.example` 文件（不包含敏感信息）：
```env
# 数据库配置
DATABASE_URL=sqlite:///db.sqlite3

# 安全配置
SECRET_KEY=your-secret-key-here
DEBUG=True

# 其他配置
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. 创建 .gitignore 文件

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.ENV/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 环境变量
.env

# 系统文件
.DS_Store
Thumbs.db
```

### 4. 更新 settings.py（生产环境配置）

创建 `settings.py` 的生产版本：

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 从环境变量读取配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-default-key')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# 应用配置
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inventory',  # 你的应用
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventory_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'inventory_system.wsgi.application'

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 默认主键类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 登录重定向
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/products/'
LOGOUT_REDIRECT_URL = '/login/'
```

## 📋 创建项目说明文档

### 创建 README.md 文件

```markdown
# 库存管理系统

一个基于Django的简单库存管理系统，支持商品管理、库存跟踪和基本的CRUD操作。

## 功能特性

- ✅ 商品管理（增删改查）
- ✅ 库存跟踪
- ✅ 库存预警
- ✅ 用户认证
- ✅ 响应式界面（Bootstrap 5）
- 🚧 库存调整（开发中）
- 🚧 分类管理（开发中）
- 🚧 数据导出（开发中）

## 系统要求

- Python 3.8+
- Django 5.0+

## 快速开始

### 1. 下载项目
```bash
# 解压项目文件到本地目录
cd inventory_system
```

### 2. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 数据库初始化
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 创建管理员账户
```bash
python manage.py createsuperuser
```

### 6. 启动开发服务器
```bash
python manage.py runserver
```

### 7. 访问系统
- 主页：http://127.0.0.1:8000/
- 管理后台：http://127.0.0.1:8000/admin/

## 项目结构

```
inventory_system/
├── inventory_system/          # 项目配置
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/                 # 主应用
│   ├── migrations/
│   ├── templates/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── static/                    # 静态文件
├── requirements.txt           # 项目依赖
├── manage.py
└── README.md
```

## 使用说明

### 商品管理
1. 登录系统
2. 点击"添加商品"创建新商品
3. 填写商品信息（名称、编码、库存、价格等）
4. 保存后可在商品列表中查看

### 库存管理
- 绿色徽章：库存充足
- 黄色徽章：库存不足
- 红色徽章：缺货

## 技术栈

- **后端**：Django 5.0
- **前端**：Bootstrap 5 + JavaScript
- **数据库**：SQLite（可配置MySQL/PostgreSQL）
- **图标**：Bootstrap Icons

## 常见问题

### Q: 如何修改库存预警值？
A: 编辑商品时可以设置"库存预警值"字段。

### Q: 如何备份数据？
A: 复制 `db.sqlite3` 文件即可备份所有数据。

### Q: 忘记管理员密码怎么办？
A: 重新运行 `python manage.py createsuperuser` 创建新管理员。

## 开发说明

### 添加新功能
1. 在 `models.py` 中定义数据模型
2. 在 `forms.py` 中创建表单
3. 在 `views.py` 中编写视图逻辑
4. 在 `urls.py` 中配置路由
5. 创建相应的模板文件

### 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

## 许可证

MIT License

## 联系方式

如有问题，请联系开发者。
```

## 🚀 部署脚本

### 创建 setup.bat（Windows用户）

```batch
@echo off
echo 正在设置库存管理系统...
echo.

echo 1. 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo 错误: 无法创建虚拟环境，请确保已安装Python
    pause
    exit /b 1
)

echo 2. 激活虚拟环境...
call venv\Scripts\activate

echo 3. 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 无法安装依赖包
    pause
    exit /b 1
)

echo 4. 初始化数据库...
python manage.py makemigrations
python manage.py migrate

echo 5. 创建管理员账户...
python manage.py createsuperuser

echo.
echo 设置完成！
echo.
echo 启动服务器请运行: start.bat
echo.
pause
```

### 创建 setup.sh（macOS/Linux用户）

```bash
#!/bin/bash

echo "正在设置库存管理系统..."
echo

echo "1. 创建虚拟环境..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "错误: 无法创建虚拟环境，请确保已安装Python 3"
    exit 1
fi

echo "2. 激活虚拟环境..."
source venv/bin/activate

echo "3. 安装依赖包..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误: 无法安装依赖包"
    exit 1
fi

echo "4. 初始化数据库..."
python manage.py makemigrations
python manage.py migrate

echo "5. 创建管理员账户..."
python manage.py createsuperuser

echo
echo "设置完成！"
echo
echo "启动服务器请运行: ./start.sh"
echo

# 给脚本添加执行权限
chmod +x start.sh
```

### 创建 start.bat（Windows启动脚本）

```batch
@echo off
echo 启动库存管理系统...
call venv\Scripts\activate
python manage.py runserver
pause
```

### 创建 start.sh（macOS/Linux启动脚本）

```bash
#!/bin/bash
echo "启动库存管理系统..."
source venv/bin/activate
python manage.py runserver
```

## 📁 最终项目结构

```
inventory_system/
├── inventory_system/          # Django项目配置
├── inventory/                 # 主应用
├── static/                    # 静态文件（如果有）
├── requirements.txt           # 依赖包列表
├── .env.example              # 环境变量示例
├── .gitignore               # Git忽略文件
├── README.md                # 项目说明
├── setup.bat               # Windows安装脚本
├── setup.sh                # macOS/Linux安装脚本
├── start.bat               # Windows启动脚本
├── start.sh                # macOS/Linux启动脚本
└── manage.py               # Django管理脚本
```

## 📤 打包方法

### 方法1：ZIP压缩包
1. 排除不必要的文件（`__pycache__`、`.venv`、`db.sqlite3`等）
2. 压缩整个项目文件夹
3. 发送给对方

### 方法2：Git仓库
```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit"

# 推送到GitHub/GitLab等
git remote add origin <repository-url>
git push -u origin main
```

### 方法3：Docker部署
创建 `Dockerfile`：
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 💡 给接收者的说明

发送给别人时，包含以下内容：

1. **项目压缩包**
2. **README.md**（详细说明）
3. **安装脚本**（setup.bat/setup.sh）
4. **简单的使用说明**

**简单使用说明：**
```
1. 解压文件到任意文件夹
2. 确保电脑已安装Python 3.8+
3. 双击运行 setup.bat（Windows）或 ./setup.sh（Mac/Linux）
4. 按提示创建管理员账户
5. 运行 start.bat 启动系统
6. 浏览器访问 http://127.0.0.1:8000
```

这样打包后，接收者只需要按照README说明操作，就能快速运行你的库存管理系统了！
