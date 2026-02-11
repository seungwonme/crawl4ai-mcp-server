# MCP 서버 프로젝트 모범 구조 조사 리포트

**조사일**: 2025-12-17
**대상 프로젝트**: crawl4ai-mcp (FastMCP 기반 Python MCP 서버)

## Executive Summary

2025년 기준 MCP(Model Context Protocol) 서버 프로젝트는 단일 책임 원칙, 모듈화된 구조, 그리고 컨테이너화를 중심으로 표준화되고 있습니다. FastMCP 프레임워크는 Python MCP 서버 개발의 사실상 표준으로 자리잡았으며, `pyproject.toml` 중심의 설정 관리와 `tests/` 디렉토리 구조가 권장됩니다.

---

## 1. 2025년 MCP 서버 프로젝트 표준 구조

### 1.1 권장 디렉토리 구조

#### FastMCP 기반 Python 프로젝트 (공식 권장)[1][2][3]

```
my-mcp-server/
├── src/
│   └── my_mcp_server/
│       ├── __init__.py
│       ├── server.py          # MCP 서버 진입점
│       ├── tools/             # 도구 정의 모듈
│       │   ├── __init__.py
│       │   └── my_tools.py
│       └── resources/         # 리소스 핸들러
│           ├── __init__.py
│           └── my_resources.py
├── tests/                     # 테스트 디렉토리
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_server.py
│   └── test_tools.py
├── docs/                      # 문서 디렉토리
│   └── README.md
├── examples/                  # 예제 구현
│   └── example_usage.py
├── .python-version            # Python 버전 명시
├── pyproject.toml            # 프로젝트 설정 (통합)
├── uv.lock                   # 의존성 잠금
├── fastmcp.json              # FastMCP 설정 (선택)
├── .mcp.json                 # Claude Desktop/Code 설정
├── .gitignore
└── README.md
```

#### 모듈화된 대규모 프로젝트 구조[4]

```
enterprise-mcp-server/
├── client/                    # MCP 클라이언트 구현
│   ├── README.md
│   └── subclients/
├── server/                    # FastMCP 서버 구현
│   ├── README.md
│   ├── app/                  # 비즈니스 로직 모듈
│   │   ├── tools/
│   │   ├── resources/
│   │   └── prompts/
│   └── server.py
├── document/                  # 아키텍처 문서
│   ├── README.md
│   └── architecture.md
├── tests/                     # 통합 테스트 스위트
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── pyproject.toml
```

### 1.2 핵심 설계 원칙

#### Single Responsibility Principle (단일 책임 원칙)[5]

각 MCP 서버는 **하나의 명확하고 잘 정의된 목적**을 가져야 합니다.

```python
# ❌ 나쁜 예: 모든 것을 하는 서버
mcp = FastMCP("all-in-one-server")
@mcp.tool()
def database_query(): ...
@mcp.tool()
def send_email(): ...
@mcp.tool()
def image_processing(): ...

# ✅ 좋은 예: 단일 목적 서버
mcp = FastMCP("database-server")
@mcp.tool()
def query(): ...
@mcp.tool()
def insert(): ...
```

**장점**[5]:
- 유지보수 및 테스트 용이
- 독립적 스케일링 가능
- 장애 격리 (cascading failure 방지)
- 팀 소유권 명확화

#### Modular Structure (모듈화)[6]

**관심사 분리**를 통해 코드베이스를 논리적 모듈로 구성:

```
src/my_mcp_server/
├── context/          # 컨텍스트 관리
├── protocol/         # 프로토콜 핸들링
├── tools/            # 도구 구현
└── utils/            # 유틸리티 함수
```

#### Extensible Design (확장 가능한 설계)[6]

인터페이스와 추상화를 사용하여 미래 변경 및 통합을 용이하게 합니다:

```python
# 추상 베이스 클래스 사용
from abc import ABC, abstractmethod

class BaseToolHandler(ABC):
    @abstractmethod
    async def execute(self, **kwargs): ...
```

---

## 2. 테스트 파일 구조 및 위치

### 2.1 표준 `tests/` 디렉토리 구조[2][4]

FastMCP 공식 저장소는 **소스 코드 구조를 미러링**하는 테스트 구조를 권장합니다:

```
tests/
├── __init__.py
├── conftest.py              # Shared pytest fixtures
├── server/
│   ├── test_auth.py         # src/fastmcp/server/auth.py 테스트
│   └── test_lifecycle.py
├── tools/
│   ├── test_my_tool.py
│   └── test_integration.py
├── resources/
│   └── test_resources.py
└── fixtures/
    └── sample_data.json
```

**핵심 규칙**[2]:
- 테스트 구조가 `src/` 디렉토리 구조를 반영
- `src/fastmcp/server/auth.py` → `tests/server/test_auth.py`
- 대규모 테스트는 여러 파일로 분할 가능 (예: OpenAPI 테스트)

### 2.2 Pytest 설정 (`pyproject.toml`)[7]

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=src",
    "--cov-report=html",
]
```

### 2.3 비동기 테스트 패턴

MCP 서버는 일반적으로 비동기이므로 `pytest-asyncio` 필수:

```python
# tests/conftest.py
import pytest
from fastmcp import FastMCP

@pytest.fixture
async def mcp_server():
    mcp = FastMCP("test-server")

    @mcp.tool()
    async def test_tool(message: str) -> str:
        return f"Echo: {message}"

    return mcp

# tests/test_server.py
import pytest

@pytest.mark.asyncio
async def test_tool_execution(mcp_server):
    result = await mcp_server.call_tool("test_tool", message="hello")
    assert result == "Echo: hello"
```

---

## 3. 불필요한 파일 정리 모범 사례

### 3.1 `pyproject.toml`로 통합 가능한 파일들[8][9][10]

`pyproject.toml`은 **단일 선언적 설정 파일**로 다음을 대체합니다:

#### 제거 가능한 레거시 파일[8][9]

```
❌ setup.py              → [project] section in pyproject.toml
❌ setup.cfg             → [tool.*] sections in pyproject.toml
❌ MANIFEST.in           → [tool.setuptools] section
❌ requirements.txt      → dependencies in [project]
❌ requirements-dev.txt  → [project.optional-dependencies]
```

#### 통합 가능한 도구 설정[8][9][10]

```
❌ pytest.ini            → [tool.pytest.ini_options]
❌ mypy.ini              → [tool.mypy]
❌ .isort.cfg            → [tool.isort]
❌ tox.ini               → [tool.tox]
❌ .coveragerc           → [tool.coverage.run]
```

### 3.2 통합된 `pyproject.toml` 예시

```toml
[project]
name = "my-mcp-server"
version = "0.1.0"
description = "MCP server for X functionality"
requires-python = ">=3.13"
dependencies = [
    "fastmcp>=2.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.1",
    "ruff>=0.1.0",
]

[project.scripts]
my-mcp-server = "my_mcp_server.server:main"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.mypy]
python_version = "3.13"
strict = true

[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]
```

### 3.3 정리 체크리스트

#### 반드시 유지해야 하는 파일
```
✅ pyproject.toml        # 통합 설정
✅ uv.lock               # 의존성 잠금
✅ .python-version       # Python 버전 명시
✅ .gitignore            # Git 제외 규칙
✅ README.md             # 프로젝트 문서
✅ LICENSE               # 라이선스 정보
```

#### 선택적 설정 파일
```
✅ fastmcp.json          # FastMCP 배포 설정 (배포 시 권장)[1]
✅ .mcp.json             # Claude Desktop/Code 통합
✅ .pre-commit-config.yaml  # Pre-commit hooks
```

#### 제거 고려 대상 (현재 crawl4ai-mcp 프로젝트)
```
❌ __pycache__/          # .gitignore에 추가 (커밋하지 말 것)
⚠️  code_claude_com/     # 목적 불명 - 삭제 또는 문서화 필요
⚠️  prompts/             # 31개 파일 - 목적에 따라 정리 고려
⚠️  docs/                # 간단한 프로젝트는 README.md로 충분
```

---

## 4. FastMCP 기반 프로젝트 구조 예시

### 4.1 미니멀 구조 (단일 파일)[11][12]

간단한 MCP 서버는 **단일 `server.py` 파일**로 충분:

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("minimal-server")

@mcp.tool()
async def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

```toml
# pyproject.toml
[project]
name = "minimal-mcp"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["fastmcp>=2.0"]

[project.scripts]
minimal-mcp = "server:main"
```

### 4.2 모듈화된 구조 (확장 가능)[1][13]

복잡한 서버는 **관심사별 분리**:

```
src/advanced_mcp_server/
├── __init__.py
├── server.py                # 서버 초기화 및 마운팅
├── config.py                # 환경 설정
├── tools/
│   ├── __init__.py
│   ├── database.py          # DB 도구
│   ├── api.py               # API 통합 도구
│   └── processing.py        # 데이터 처리 도구
├── resources/
│   ├── __init__.py
│   └── data_sources.py      # 리소스 핸들러
└── utils/
    ├── __init__.py
    └── validators.py        # 유틸리티 함수
```

```python
# server.py - FastMCP 마운팅 패턴[1]
from fastmcp import FastMCP
from .tools import database, api, processing

mcp = FastMCP("advanced-server")

# 서브모듈을 독립적인 FastMCP 인스턴스로 마운트
mcp.mount(database.mcp, prefix="/db")
mcp.mount(api.mcp, prefix="/api")
mcp.mount(processing.mcp, prefix="/process")
```

### 4.3 FastMCP 설정 파일 (`fastmcp.json`)[14][15]

배포 시 권장되는 **선언적 설정 파일**:

```json
{
  "source": {
    "entrypoint": "src/my_mcp_server/server.py"
  },
  "environment": {
    "python": "3.13",
    "dependencies": [
      "fastmcp>=2.0",
      "httpx>=0.27.0"
    ]
  },
  "deployment": {
    "transport": "stdio",
    "log_level": "INFO"
  }
}
```

**3대 질문에 답합니다**[14]:
1. **Source** = 서버 코드 위치 (WHERE)
2. **Environment** = 환경 설정 (WHAT)
3. **Deployment** = 실행 방법 (HOW)

---

## 5. 도구 및 API 설계 모범 사례

### 5.1 Tool Budget 관리[16]

**Anti-pattern**: API 엔드포인트당 하나의 도구 생성

```python
# ❌ 나쁜 예: 도구 폭발
@mcp.tool()
def get_user(): ...
@mcp.tool()
def get_invoices(): ...
@mcp.tool()
def validate_user(): ...
@mcp.tool()
def create_invoice(): ...
# ... 50개의 도구
```

**Best practice**: 프롬프트를 매크로로 사용하여 도구 체인[16]

```python
# ✅ 좋은 예: 프롬프트 기반 워크플로우
@mcp.tool()
def query_database(query: str): ...

@mcp.prompt()
def fetch_user_invoices(user_id: str):
    """내부적으로 여러 도구를 호출하는 프롬프트"""
    return [
        {"role": "user", "content": f"Fetch user {user_id}"},
        {"role": "assistant", "content": "query_database(...)"},
        {"role": "user", "content": "Now fetch their invoices"},
    ]
```

**장점**[16]:
- 서버 복잡도 감소
- 배포 비용 절감
- 사용자 인지 부하 감소

### 5.2 Self-Contained Tool Calls (자기 완결적 도구)[16][17]

서버 시작 시가 아닌 **도구 호출 시점에 연결 생성**:

```python
# ❌ 나쁜 예: 서버 시작 시 연결
db_connection = None

async def startup():
    global db_connection
    db_connection = await connect_to_db()  # 실패 시 서버 시작 불가

@mcp.tool()
async def query(sql: str):
    return await db_connection.execute(sql)

# ✅ 좋은 예: 도구 호출마다 연결
@mcp.tool()
async def query(sql: str):
    async with connect_to_db() as conn:  # 도구 실행 시 연결
        return await conn.execute(sql)
```

**장점**[16][17]:
- 잘못된 설정에도 도구 목록 조회 가능
- 에이전트가 설정 문제 이해 가능
- 약간의 지연 시간을 유용성으로 교환

### 5.3 에러 메시지 설계[17]

**에이전트를 위한 에러 메시지**:

```python
# ❌ 사람 중심 메시지
raise ValueError("You don't have access to this system")

# ✅ 에이전트 중심 메시지
raise ValueError(
    "To access this system, configure API_TOKEN. "
    f"Current token '{token[:8]}...' is invalid. "
    "Expected format: 'sk-...'"
)
```

에이전트가 **왜**(설정 오류) vs **무엇**(접근 거부)을 이해하도록 돕습니다[17].

---

## 6. 보안 및 배포 모범 사례

### 6.1 OAuth 2.1 필수화[5]

2025년 3월 MCP 사양 업데이트에 따라:

```python
# HTTP 기반 전송은 OAuth 2.1 필수
from fastmcp.auth import OAuth21Authenticator

mcp = FastMCP(
    "secure-server",
    auth=OAuth21Authenticator(
        client_id=os.getenv("OAUTH_CLIENT_ID"),
        client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
    )
)
```

**보안 체크리스트**[5][18]:
- ✅ 세션 ID 기반 인증 사용 금지
- ✅ 예측 불가능한 세션 식별자 생성
- ✅ 모든 승인된 요청 검증
- ✅ 데이터 노출 최소화
- ✅ 암호화 및 안전한 저장소 사용

### 6.2 Docker 컨테이너화[6][16][19]

2025년 표준: **Docker 패키징**[6]

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# uv를 사용한 의존성 설치
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY src/ ./src/

# stdio 전송 메커니즘 지원
CMD ["uv", "run", "python", "-m", "my_mcp_server.server"]
```

**Docker MCP 레지스트리 제출 요구사항**[16]:
- ✅ stdio 전송 메커니즘 지원 필수
- ✅ 적절한 Dockerfile 설정
- ✅ 자기 완결적 도구 호출 구현
- ✅ 직접 사용이 아닌 에이전트 상호작용 최적화

### 6.3 입력 검증 및 스키마 강제[6][20]

```python
from pydantic import BaseModel, Field

class QueryInput(BaseModel):
    sql: str = Field(..., description="SQL query to execute")
    limit: int = Field(100, ge=1, le=1000, description="Result limit")

@mcp.tool()
async def query(input: QueryInput) -> str:
    # Pydantic이 자동으로 검증
    return await execute_query(input.sql, input.limit)
```

**장점**[20]:
- 주입 공격 방지
- 손상된 프로토콜 메시지 방지
- 자동 문서 생성
- 타입 안전성

---

## 7. 테스트 및 검증 전략

### 7.1 MCP Inspector 통합[17][21]

**필수 테스트 도구**:

```bash
# 설치
npm install -g @modelcontextprotocol/inspector

# 서버 검사 (자동 스키마 검증)
npx @modelcontextprotocol/inspector server.py

# 개발 모드 (Inspector UI)
fastmcp dev server.py
```

**3단계 테스트 워크플로우**[17]:

1. **설정 검증**: 서버가 올바르게 시작되는가?
2. **도구 발견**: 에이전트가 도구를 올바르게 인식하는가?
3. **도구 실행**: 실패 모드가 적절히 처리되는가?

### 7.2 엄격한 스키마 준수[20]

```python
# 출력 스키마 정의 (MCP 2025-06-18 사양)[22]
from pydantic import BaseModel

class ToolOutput(BaseModel):
    result: str
    metadata: dict

@mcp.tool(output_schema=ToolOutput.model_json_schema())
async def my_tool(input: str) -> ToolOutput:
    return ToolOutput(
        result=f"Processed: {input}",
        metadata={"timestamp": "2025-12-17"}
    )
```

**장점**[20]:
- 미묘한 버그 방지
- 재앙적인 프로덕션 오류 방지
- Inspector가 자동으로 검증
- 회귀 테스트 커버리지

### 7.3 상세 로깅[20]

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@mcp.tool()
async def debug_tool(input: str):
    logging.debug(f"Received input: {input}")
    try:
        result = await process(input)
        logging.debug(f"Processed result: {result}")
        return result
    except Exception as e:
        logging.error(f"Error processing: {e}", exc_info=True)
        raise
```

**효과**[20]: 디버깅을 위한 평균 해결 시간(MTTR)을 최대 40% 단축.

---

## 8. 성능 및 확장성 지침

### 8.1 성능 목표[18]

**프로덕션 MCP 서버 벤치마크**:

| 메트릭 | 목표 |
|--------|------|
| 처리량 (Throughput) | >1000 req/s per instance |
| P95 지연 시간 (단순 작업) | <100ms |
| P99 지연 시간 (복잡 작업) | <500ms |
| 오류율 (정상 조건) | <0.1% |
| 가용성 (Uptime) | >99.9% |

### 8.2 효율적인 데이터 처리[18]

```python
# 연결 풀링
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://...",
    pool_size=20,
    max_overflow=10,
)

# 다중 레벨 캐싱
from functools import lru_cache
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost")

@lru_cache(maxsize=100)  # 인메모리 캐시
async def get_cached_data(key: str):
    # 분산 캐시 확인
    cached = await redis_client.get(key)
    if cached:
        return cached

    # DB에서 가져오기
    data = await fetch_from_db(key)
    await redis_client.setex(key, 3600, data)  # 1시간 TTL
    return data

# 비동기 처리
@mcp.tool()
async def long_running_task(data: str) -> dict:
    task_id = generate_task_id()
    asyncio.create_task(process_in_background(task_id, data))
    return {"task_id": task_id, "status": "processing"}
```

### 8.3 Kubernetes 배포[18]

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    spec:
      containers:
      - name: mcp-server
        image: my-mcp-server:latest
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5

---
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcp-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-server
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 9. crawl4ai-mcp 프로젝트 개선 제안

### 9.1 현재 구조 분석

```
crawl4ai-mcp/
├── __pycache__/           ❌ .gitignore에 추가 필요
├── .venv/                 ✅ 가상 환경
├── configs/               ✅ 설정 모듈화 (우수)
├── strategies/            ✅ 전략 패턴 (우수)
├── utils/                 ✅ 유틸리티 분리 (우수)
├── docs/                  ⚠️  간단한 프로젝트는 README로 충분
├── prompts/               ⚠️  31개 파일 - 목적 확인 필요
├── code_claude_com/       ❌ 목적 불명
├── cli.py                 ✅ CLI 인터페이스
├── core.py                ✅ 핵심 로직
├── mcp_server.py          ✅ MCP 서버
├── pyproject.toml         ✅ 통합 설정
└── uv.lock                ✅ 의존성 잠금
```

### 9.2 권장 리팩토링

#### 단계 1: 디렉토리 구조 표준화

```bash
# 소스 코드를 src/ 디렉토리로 이동
mkdir -p src/crawl4ai_mcp
mv cli.py core.py mcp_server.py src/crawl4ai_mcp/
mv configs strategies utils src/crawl4ai_mcp/

# __init__.py 추가
touch src/crawl4ai_mcp/__init__.py
touch src/crawl4ai_mcp/configs/__init__.py
touch src/crawl4ai_mcp/strategies/__init__.py
touch src/crawl4ai_mcp/utils/__init__.py

# 테스트 디렉토리 생성
mkdir -p tests/{unit,integration}
touch tests/__init__.py
touch tests/conftest.py
```

**결과 구조**:
```
crawl4ai-mcp/
├── src/
│   └── crawl4ai_mcp/
│       ├── __init__.py
│       ├── server.py          # mcp_server.py 리네임
│       ├── core.py
│       ├── cli.py
│       ├── configs/
│       ├── strategies/
│       └── utils/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_core.py
│   │   └── test_strategies.py
│   └── integration/
│       └── test_server.py
├── examples/
│   └── basic_usage.py
├── .gitignore             # __pycache__ 추가
├── pyproject.toml         # [project.scripts] 업데이트
└── README.md
```

#### 단계 2: `pyproject.toml` 업데이트

```toml
[project]
name = "crawl4ai-mcp"
version = "0.1.0"
description = "MCP server for web document crawling using Crawl4AI"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "crawl4ai>=0.7.4",
    "typer>=0.19.2",
    "mcp[cli]>=1.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.1",
    "ruff>=0.1.0",
]

[project.scripts]
crawl4ai-mcp = "crawl4ai_mcp.server:main"
crawl4ai-cli = "crawl4ai_mcp.cli:app"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = ["--cov=src/crawl4ai_mcp", "--cov-report=html"]

[tool.ruff]
line-length = 100
target-version = "py313"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### 단계 3: `.gitignore` 업데이트

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# MCP specific
code_claude_com/  # 목적 불명 - 삭제 고려
prompts/          # 필요시 유지, 불필요시 삭제
```

#### 단계 4: 테스트 추가

```python
# tests/conftest.py
import pytest
from crawl4ai_mcp.server import mcp

@pytest.fixture
def mcp_server():
    """MCP 서버 인스턴스 픽스처"""
    return mcp

@pytest.fixture
async def sample_url():
    """테스트용 샘플 URL"""
    return "https://example.com"

# tests/unit/test_core.py
import pytest
from crawl4ai_mcp.core import crawl_single_page

@pytest.mark.asyncio
async def test_crawl_single_page(sample_url):
    """단일 페이지 크롤링 테스트"""
    result = await crawl_single_page(sample_url)
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0

# tests/integration/test_server.py
import pytest

@pytest.mark.asyncio
async def test_mcp_tool_crawl_page(mcp_server, sample_url):
    """MCP 도구 통합 테스트"""
    result = await mcp_server.call_tool(
        "crawl_page",
        url=sample_url
    )
    assert result is not None
```

#### 단계 5: `fastmcp.json` 추가 (배포 최적화)

```json
{
  "source": {
    "entrypoint": "src/crawl4ai_mcp/server.py"
  },
  "environment": {
    "python": "3.13",
    "dependencies": [
      "crawl4ai>=0.7.4",
      "typer>=0.19.2",
      "mcp[cli]>=1.2.0"
    ]
  },
  "deployment": {
    "transport": "stdio",
    "log_level": "INFO"
  }
}
```

#### 단계 6: Dockerfile 추가 (컨테이너화)

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# uv 설치
RUN pip install --no-cache-dir uv

# 의존성 복사 및 설치
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# 소스 코드 복사
COPY src/ ./src/

# 환경 변수
ENV PYTHONUNBUFFERED=1

# stdio 전송 지원
CMD ["uv", "run", "python", "-m", "crawl4ai_mcp.server"]
```

### 9.3 불필요한 파일 정리 권장사항

```bash
# 1. __pycache__ 제거 및 .gitignore 추가
rm -rf __pycache__
echo "__pycache__/" >> .gitignore

# 2. 목적 불명 디렉토리 확인 후 제거
# code_claude_com/ - 사용하지 않으면 삭제
rm -rf code_claude_com/

# 3. prompts/ 디렉토리 정리
# 31개 파일이 무엇인지 확인 필요
# 불필요하면 examples/ 또는 docs/examples/ 로 이동하거나 삭제

# 4. docs/ 디렉토리 평가
# 간단한 프로젝트라면 README.md로 충분
# 복잡한 문서가 필요하면 유지

# 5. 레거시 설정 파일 확인
# pytest.ini, setup.py, requirements.txt 등이 있다면 제거
```

---

## 10. 요약 및 체크리스트

### 10.1 핵심 원칙

1. **단일 책임 원칙**: 하나의 MCP 서버는 하나의 명확한 목적[5]
2. **모듈화**: 관심사 분리 및 재사용 가능한 컴포넌트[6]
3. **자기 완결성**: 도구 호출은 서버 상태에 의존하지 않음[16][17]
4. **에이전트 중심 설계**: 에러 메시지와 문서를 에이전트를 위해 작성[17]
5. **컨테이너화**: Docker를 사용한 일관된 배포[6][16]

### 10.2 프로젝트 구조 체크리스트

#### 필수 요소
- ✅ `src/` 디렉토리에 소스 코드 구성
- ✅ `tests/` 디렉토리에 소스 미러링 구조
- ✅ `pyproject.toml` 통합 설정
- ✅ `.gitignore`에 `__pycache__/`, `.venv/` 포함
- ✅ `README.md` 프로젝트 문서화

#### 권장 요소
- ✅ `fastmcp.json` 배포 설정 (배포 시)[14]
- ✅ `.mcp.json` Claude 통합
- ✅ `Dockerfile` 컨테이너화
- ✅ `examples/` 샘플 코드
- ✅ `.python-version` Python 버전 명시

#### 제거 대상
- ❌ `setup.py`, `setup.cfg` (pyproject.toml로 대체)
- ❌ `requirements.txt` (pyproject.toml로 대체)
- ❌ `pytest.ini` (pyproject.toml로 통합)
- ❌ 도구별 설정 파일 (`.isort.cfg`, `mypy.ini` 등)
- ❌ `__pycache__/` (항상 .gitignore)

### 10.3 테스트 체크리스트

- ✅ `pytest-asyncio` 설치
- ✅ `tests/conftest.py`에 공유 픽스처
- ✅ MCP Inspector로 스키마 검증
- ✅ 단위 테스트 (도구 로직)
- ✅ 통합 테스트 (서버 전체)
- ✅ 커버리지 80% 이상 목표

### 10.4 보안 및 성능 체크리스트

- ✅ OAuth 2.1 인증 구현 (HTTP 전송 시)[5]
- ✅ Pydantic 스키마 검증[20]
- ✅ 환경 변수로 민감 정보 관리
- ✅ 연결 풀링 및 캐싱 구현[18]
- ✅ 상세 로깅 및 모니터링[20]
- ✅ P95 지연 시간 <100ms 목표[18]

---

## Footnotes

[1] FastMCP Documentation - Project Configuration. https://github.com/jlowin/fastmcp/blob/main/docs/deployment/server-configuration.mdx (Accessed: 2025-12-17)

[2] FastMCP Documentation - Test Organization. https://github.com/jlowin/fastmcp/blob/main/docs/development/tests.mdx (Accessed: 2025-12-17)

[3] Model Context Protocol Python SDK. https://github.com/modelcontextprotocol/python-sdk (Accessed: 2025-12-17)

[4] JoshuaWink/fastmcp-templates - Templates and best practices for building MCP applications. https://github.com/JoshuaWink/fastmcp-templates (Accessed: 2025-12-17)

[5] MarkTechPost - 7 MCP Server Best Practices for Scalable AI Integrations in 2025. https://www.marktechpost.com/2025/07/23/7-mcp-server-best-practices-for-scalable-ai-integrations-in-2025/ (Accessed: 2025-12-17)

[6] Docker Blog - Top 5 MCP Server Best Practices. https://www.docker.com/blog/mcp-server-best-practices/ (Accessed: 2025-12-17)

[7] Writing your pyproject.toml - Python Packaging User Guide. https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ (Accessed: 2025-12-17)

[8] The Complete Guide to pyproject.toml. https://devsjc.github.io/blog/20240627-the-complete-guide-to-pyproject-toml/ (Accessed: 2025-12-17)

[9] Managing Python Projects With pyproject.toml | Better Stack Community. https://betterstack.com/community/guides/scaling-python/pyproject-explained/ (Accessed: 2025-12-17)

[10] How to Manage Python Projects With pyproject.toml – Real Python. https://realpython.com/python-pyproject-toml/ (Accessed: 2025-12-17)

[11] GitHub - jlowin/fastmcp: The fast, Pythonic way to build MCP servers and clients. https://github.com/jlowin/fastmcp (Accessed: 2025-12-17)

[12] FastMCP Official Website. https://gofastmcp.com (Accessed: 2025-12-17)

[13] Model Context Protocol - Build an MCP server. https://modelcontextprotocol.io/docs/develop/build-server (Accessed: 2025-12-17)

[14] FastMCP Configuration Demo - Configuration Structure. https://github.com/jlowin/fastmcp/blob/main/examples/fastmcp_config_demo/README.md (Accessed: 2025-12-17)

[15] FastMCP Configuration File Documentation. https://github.com/jlowin/fastmcp/blob/main/docs/integrations/mcp-json-configuration.mdx (Accessed: 2025-12-17)

[16] Docker Blog - MCP Server Best Practices: Project Structure & Organization. https://www.docker.com/blog/mcp-server-best-practices/ (Accessed: 2025-12-17)

[17] Docker Blog - MCP Server Lifecycle Structure and Error Handling. https://www.docker.com/blog/mcp-server-best-practices/ (Accessed: 2025-12-17)

[18] MCP Best Practices: Architecture & Implementation Guide. https://modelcontextprotocol.info/docs/best-practices/ (Accessed: 2025-12-17)

[19] The New Stack - 15 Best Practices for Building MCP Servers in Production. https://thenewstack.io/15-best-practices-for-building-mcp-servers-in-production/ (Accessed: 2025-12-17)

[20] MCP Best Practices - Testing & Validation. https://modelcontextprotocol.info/docs/best-practices/ (Accessed: 2025-12-17)

[21] Model Context Protocol - MCP Inspector. https://github.com/modelcontextprotocol/inspector (Accessed: 2025-12-17)

[22] Model Context Protocol Specification 2025-06-18. https://modelcontextprotocol.io/docs/specification/2025-06-18 (Accessed: 2025-12-17)

---

**참고 자료 (추가 읽기)**

- Model Context Protocol Official Documentation: https://modelcontextprotocol.io
- FastMCP GitHub Repository: https://github.com/jlowin/fastmcp
- Python Packaging User Guide: https://packaging.python.org
- Docker MCP Best Practices: https://www.docker.com/blog/mcp-server-best-practices/
- MCP Best Practices Architecture Guide: https://modelcontextprotocol.info/docs/best-practices/
