# 电商后端 API 项目（FastAPI）

![Coverage](https://img.shields.io/badge/coverage-80%25%2B-brightgreen)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

这是我主导开发的一个电商后端项目，目标是搭建可扩展的电商 API 基础能力，并形成可测试、可压测、可容器化部署的工程化后端。

## 一句话介绍

我负责从 0 到 1 完成电商后端核心模块开发，落地了用户认证、商品管理、订单管理、自动化测试、性能压测和 CI/CD 基础链路。

## 我在项目中的职责与产出

### 1. 后端架构与接口设计

- 使用 FastAPI 搭建 RESTful API，统一版本路由前缀 `/api/v1`。
- 设计并实现用户、商品、订单三大核心业务接口。
- 基于 SQLModel 设计电商核心实体模型（用户、订单、商品、购物车、支付、物流等）。

### 2. 安全与认证体系

- 实现用户注册与登录流程。
- 密码采用哈希存储（非明文）。
- 使用 OAuth2 + JWT 完成接口鉴权，并提供当前用户信息查询接口。

### 3. 测试与质量保障

- 编写 API 自动化测试，覆盖注册、登录、鉴权、商品、订单主流程。
- 使用 pytest 参数化测试覆盖正常与异常场景。
- 集成 Allure 报告，支持测试结果可视化追踪。
- 额外建立 UI 自动化测试目录（Playwright）用于端到端扩展。

### 4. 性能与工程化能力

- 编写 Locust 压测脚本，验证商品查询与订单创建接口的并发表现。
- 提供 Docker / docker-compose 配置，支持快速容器化运行。
- 配置 Jenkins 流水线，支持自动化构建与测试执行。

## 我是怎么开发和测试这个项目的

### 开发流程

1. 先定义模型和 Schema，明确请求/响应结构。
2. 再实现路由与业务逻辑，保证接口可用。
3. 引入 JWT 鉴权，完成登录态闭环。
4. 每个模块完成后补充自动化测试并回归验证。
5. 在稳定版本上进行 Locust 压测并观察接口表现。
6. 最后接入 Docker 与 Jenkins，保证部署和交付一致性。

### 测试策略

- 单接口功能验证：手动通过 Swagger 快速验证。
- 回归验证：pytest 执行 API 自动化用例。
- 报告追踪：allure 汇总结果，定位失败用例。
- 压力验证：locust 模拟用户访问行为，观察吞吐和响应。

## 项目已实现能力（当前代码）

### 用户与认证

- `POST /api/v1/auth/register`：用户注册
- `POST /api/v1/auth/token`：登录获取 JWT
- `GET /api/v1/auth/users/me`：获取当前登录用户
- `GET /api/v1/auth/`：用户列表查询

### 商品管理

- `GET /api/v1/products/`：商品列表
- `GET /api/v1/products/{product_id}`：商品详情
- `POST /api/v1/products/`：创建商品
- `PUT /api/v1/products/{product_id}`：更新商品信息

### 订单管理

- `GET /api/v1/orders/`：订单列表
- `GET /api/v1/orders/{id}`：订单详情
- `POST /api/v1/orders/`：创建订单
- `PUT /api/v1/orders/{id}`：更新订单状态/金额

## 技术栈

- 后端框架：FastAPI
- 数据建模与 ORM：SQLModel、SQLAlchemy
- 数据库：PostgreSQL
- 鉴权：OAuth2、JWT、Passlib
- 自动化测试：pytest、requests、allure
- UI 测试扩展：playwright
- 性能测试：locust
- 工程化：Docker、docker-compose、Jenkins

## 如何运行（面试演示可直接用）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env`（可参考 `.env.example`）：

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/ecommercedb
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. 启动服务

```bash
uvicorn app.main:app --reload
```

### 4. 查看接口文档

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 如何测试与压测

### 运行 API 自动化测试

```bash
pytest tests/api -v
```

### 生成 Allure 报告（如本地已安装 allure）

```bash
pytest tests/api --alluredir=allure-results
allure serve allure-results
```

### 运行 Locust 压测

```bash
locust -f performance/locustfile.py
```

打开 `http://localhost:8089` 发起压测任务。

## 项目文档导航

为了让面试官和协作者快速了解项目，我把核心文档入口整理如下：

- 接口在线文档（运行后）：`http://127.0.0.1:8000/docs`、`http://127.0.0.1:8000/redoc`
- 数据库设计文档（ER/结构图）：`Database_Schema-2025-02-09.png`
- 数据库建表脚本：`Database_Schema-2025-02-09.sql`
- 性能测试报告：`performance/report.md`
- 压测脚本：`performance/locustfile.py`
- API 自动化测试用例：`tests/api/`
- UI 自动化测试目录：`tests/ui/`
- 持续集成配置：`Jenkinsfile`
- 容器化部署配置：`Dockerfile`、`docker-compose.yml`
- 项目迭代计划与任务拆解：`plan.md`

### 文档使用建议（面试演示）

1. 先看本 README 的「我在项目中的职责与产出」，快速理解我负责的内容。
2. 再启动项目并打开 `/docs`，现场演示核心接口闭环（注册 -> 登录 -> 鉴权访问）。
3. 然后展示 `tests/api/` 与 `performance/`，说明我如何做质量保障和性能验证。
4. 最后结合 `Jenkinsfile` 与 Docker 配置，补充我的工程化落地能力。

## 我的优势

- 能独立完成后端核心链路从设计到交付，而不是只写单点接口。
- 具备安全意识，登录与密码处理符合常见后端安全实践。
- 强调质量保障，开发阶段同步落地自动化测试与可视化报告。
- 具备工程化思维，能将代码接入容器化与 CI 流水线。
- 有性能验证意识，能用压测数据支撑系统优化方向。
