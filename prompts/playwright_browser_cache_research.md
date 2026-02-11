# Playwright 브라우저 중복 설치 문제 해결 방법 연구 보고서

**작성일**: 2025-12-17
**연구 대상**: Playwright 브라우저 캐시 및 설치 관리
**환경**: Python 3.13, uv 패키지 매니저, crawl4ai 라이브러리, macOS (Apple Silicon)

---

## Executive Summary

Playwright 브라우저가 매번 재설치되는 문제는 환경변수 설정 부재, 가상환경 격리, 그리고 패키지 매니저별 경로 차이에서 발생합니다. 본 보고서는 2025년 기준 최신 모범 사례를 바탕으로 영구적인 해결책을 제시합니다.

**핵심 발견사항**:
- Playwright는 OS별 기본 캐시 디렉토리를 사용하며, macOS의 경우 `~/Library/Caches/ms-playwright`입니다[1][2]
- `PLAYWRIGHT_BROWSERS_PATH` 환경변수로 브라우저 설치 위치를 제어할 수 있습니다[2][3]
- uv를 포함한 Python 가상환경은 Playwright CLI와 별도로 관리되어 경로 충돌이 발생할 수 있습니다[4][5]
- crawl4ai는 `crawl4ai-setup` 명령어로 Playwright를 자동 설정하지만, 환경변수가 올바르게 설정되지 않으면 매번 재설치를 요구합니다[6][7]

---

## 1. Playwright 브라우저 캐시 위치 및 환경변수

### 1.1 기본 캐시 위치

Playwright는 운영체제별로 다른 기본 캐시 디렉토리를 사용합니다[1][2]:

- **Windows**: `%USERPROFILE%\AppData\Local\ms-playwright`
- **macOS**: `~/Library/Caches/ms-playwright`
- **Linux**: `~/.cache/ms-playwright`

현재 시스템에서 확인한 실제 설치 위치:
```
/Users/seungwonan/Library/Caches/ms-playwright/chromium-1187
/Users/seungwonan/Library/Caches/ms-playwright/chromium_headless_shell-1187
/Users/seungwonan/Library/Caches/ms-playwright/ffmpeg-1011
```

각 브라우저는 버전별로 별도 디렉토리에 설치되며, Playwright 버전이 변경되면 새로운 브라우저 버전이 다운로드됩니다[2].

### 1.2 PLAYWRIGHT_BROWSERS_PATH 환경변수

이 환경변수는 브라우저 설치 위치를 사용자 정의할 수 있게 합니다[2][3].

**중요**: 이 환경변수는 **설치 시**와 **실행 시** 모두에 동일하게 설정되어야 합니다[2][8].

#### 설정 방법

**Bash/Zsh (macOS/Linux)**:
```bash
# 브라우저 설치
export PLAYWRIGHT_BROWSERS_PATH=$HOME/pw-browsers
uv run playwright install chromium

# 스크립트 실행 시에도 동일하게 설정
export PLAYWRIGHT_BROWSERS_PATH=$HOME/pw-browsers
uv run python your_script.py
```

**영구 설정** (~/.bashrc 또는 ~/.zshrc에 추가):
```bash
export PLAYWRIGHT_BROWSERS_PATH=$HOME/pw-browsers
```

**PowerShell (Windows)**:
```powershell
$Env:PLAYWRIGHT_BROWSERS_PATH="$Env:USERPROFILE\pw-browsers"
playwright install
```

**특수 값 "0"**: 프로젝트의 `node_modules` 내부에 브라우저를 설치합니다[3]. Python 프로젝트에서는 권장되지 않습니다.

### 1.3 자동 가비지 컬렉션

Playwright는 더 이상 사용되지 않는 브라우저 버전을 자동으로 삭제합니다[2][9]. 이를 비활성화하려면:

```bash
export PLAYWRIGHT_SKIP_BROWSER_GC=1
```

---

## 2. 2025년 기준 Playwright 설치 모범 사례

### 2.1 기본 설치 프로세스

**1단계: Playwright Python 라이브러리 설치**
```bash
pip install playwright
# 또는 uv 사용 시
uv pip install playwright
```

**2단계: 브라우저 바이너리 설치**
```bash
playwright install
# 특정 브라우저만 설치
playwright install chromium
# OS 의존성까지 함께 설치 (Linux)
playwright install --with-deps chromium
```

**headless shell만 필요한 경우** (CI 환경 최적화)[10]:
```bash
playwright install --only-shell
```

**new headless mode 사용 시**[10]:
```bash
# headless shell 제외
playwright install --no-shell
# 실행 시
pytest --browser-channel chromium
```

### 2.2 검증 명령어

**설치된 브라우저 확인**[2]:
```bash
playwright install --list
```

**브라우저 삭제**[2]:
```bash
# 현재 설치만 삭제
playwright uninstall
# 모든 Playwright 설치의 브라우저 삭제
playwright uninstall --all
```

### 2.3 CI/CD 환경 모범 사례

**캐싱은 권장되지 않습니다**[11]. 브라우저 바이너리 다운로드 시간과 캐시 복원 시간이 비슷하며, Linux에서는 OS 의존성이 캐시 불가능하기 때문입니다.

그러나 캐싱이 필요한 경우, Playwright 버전을 해시 키로 사용하여 캐시를 관리합니다[12]:

**GitHub Actions 예시**:
```yaml
- name: Cache Playwright browsers
  uses: actions/cache@v4
  with:
    path: ~/.cache/ms-playwright
    key: ${{ runner.os }}-playwright-${{ hashFiles('**/requirements.txt') }}

- name: Install Playwright browsers
  run: playwright install --with-deps chromium
```

**Docker 환경에서는 공식 이미지 사용**[11]:
```yaml
container:
  image: mcr.microsoft.com/playwright/python:v1.56.0-noble
```

---

## 3. uv 패키지 매니저와 Playwright 호환성

### 3.1 uv의 특징과 Playwright 통합

uv는 Rust로 작성된 초고속 Python 패키지 매니저로, pip, venv, poetry 등을 대체합니다[13][14]. 하지만 Playwright는 **2단계 설치 프로세스**가 필요하기 때문에 추가 설정이 필요합니다[4][5].

**문제점**: `uv add playwright`로 패키지를 설치해도, 후속 단계인 `playwright install`이 자동으로 실행되지 않습니다[4].

### 3.2 uv 환경에서 Playwright 설치 워크플로우

**방법 1: 표준 워크플로우** (권장)
```bash
# 1. 가상환경 생성
uv venv

# 2. Playwright 설치
uv pip install playwright

# 3. 브라우저 설치 (활성화된 가상환경에서)
source .venv/bin/activate  # Windows: .venv\Scripts\activate
playwright install chromium
```

**방법 2: uv run 사용**
```bash
uv pip install playwright
uv run playwright install chromium
```

**방법 3: 환경변수로 가상환경 내 설치** [5][15]
```bash
# .venv 내부에 브라우저 설치
export PLAYWRIGHT_BROWSERS_PATH=./.venv/ms-playwright
uv pip install playwright
uv run playwright install chromium

# 실행 시에도 동일한 환경변수 필요
export PLAYWRIGHT_BROWSERS_PATH=./.venv/ms-playwright
uv run python script.py
```

### 3.3 Docker 환경에서 uv + Playwright

**Dockerfile 예시** (Scrapy + Playwright)[5]:
```dockerfile
FROM python:3.13-slim

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 작업 디렉토리 설정
WORKDIR /app

# 가상환경 생성 및 의존성 설치
ENV VIRTUAL_ENV=/opt/venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Playwright 브라우저 경로 설정
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/venv/ms-playwright

# 의존성 설치
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Playwright 브라우저 설치
RUN playwright install --with-deps chromium

COPY . .
CMD ["python", "main.py"]
```

---

## 4. crawl4ai에서 Playwright 설정하는 방법

### 4.1 crawl4ai-setup의 동작 원리

crawl4ai는 설치 후 `crawl4ai-setup` 명령어를 실행하여 Playwright를 자동으로 설정합니다[6][7]:

```bash
pip install crawl4ai
crawl4ai-setup
```

**동작 과정**[7]:
1. Playwright 브라우저(Chromium, Firefox) 설치 또는 업데이트
2. OS 레벨 의존성 확인 (Linux의 경우 libnss3, libatk-bridge2.0 등)
3. 환경이 크롤링 준비가 되었는지 확인

예상 다운로드 크기: 약 100-200MB[7]

### 4.2 수동 설치가 필요한 경우

`crawl4ai-setup`이 실패하거나 특정 브라우저만 필요한 경우[6][7]:

```bash
# Chromium + OS 의존성
python -m playwright install --with-deps chromium

# 강제 재설치
playwright install chromium --force
```

### 4.3 crawl4ai-doctor로 진단

설치 검증 및 문제 진단[7][16]:
```bash
crawl4ai-doctor
```

**검사 항목**[16]:
- Python 버전 호환성 (3.9 이상)
- Playwright 설치 여부
- 환경변수 또는 라이브러리 충돌
- 브라우저 실행 가능 여부

문제 발견 시 구체적인 해결책(예: 시스템 패키지 설치)을 제공하며, `crawl4ai-setup` 재실행을 권장합니다[16].

### 4.4 API 전용 모드 (브라우저 설치 생략)

브라우저 없이 API 클라이언트만 사용하는 경우[7]:
```bash
export CRAWL4AI_MODE=api
pip install crawl4ai
```

### 4.5 Google Colab 환경

```python
!pip install crawl4ai
!crawl4ai-setup

# 실패 시 수동 설치
!playwright install chromium
# 또는
!playwright install chromium --force

# 전체 기능 설치 (시간 소요)
!pip install crawl4ai[all]
!crawl4ai-download-models
```

**테스트 코드**[6]:
```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def test():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        print(result.markdown[:300])

asyncio.run(test())
```

---

## 5. 시스템 레벨 vs 프로젝트 레벨 Playwright 설치

### 5.1 시스템 레벨 설치 (전역 설치)

**장점**:
- 여러 프로젝트에서 브라우저 공유로 디스크 공간 절약
- 한 번 설치하면 모든 프로젝트에서 사용 가능
- 설치 시간 단축

**단점**:
- 버전 충돌 가능성 (프로젝트마다 다른 Playwright 버전 필요 시)
- 권한 문제 발생 가능 (공유 서버 환경)

**설치 방법**:
```bash
# 시스템 Python 또는 pipx 사용
pipx install playwright
pipx run playwright install chromium

# 또는 전역 pip
pip install --user playwright
playwright install chromium
```

**기본 캐시 사용** (macOS 기준):
```
~/Library/Caches/ms-playwright/
```

### 5.2 프로젝트 레벨 설치 (가상환경)

**장점**:
- 프로젝트별 독립적인 Playwright 버전 관리
- 재현 가능한 환경 (requirements.txt 또는 pyproject.toml)
- 배포 시 격리된 환경 보장

**단점**:
- 프로젝트마다 브라우저 재설치 필요 (디스크 공간 다량 사용)
- 초기 설정 복잡도 증가

**권장 방법**: 가상환경 내부가 아닌 **공유 캐시 디렉토리 사용**[2][8][15]

**최적 설정** (~/.bashrc 또는 ~/.zshrc):
```bash
# 프로젝트 간 브라우저 공유
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.playwright-browsers
```

이렇게 하면:
- 가상환경은 프로젝트별로 독립적
- 브라우저 바이너리는 전역적으로 공유
- 디스크 공간 절약 + 재현성 확보

### 5.3 비교표

| 항목 | 시스템 레벨 | 프로젝트 레벨 (공유 캐시) | 프로젝트 레벨 (격리) |
|------|------------|--------------------------|---------------------|
| **설치 위치** | 전역 Python | 가상환경 + 공유 캐시 | 가상환경 내부 |
| **디스크 사용량** | 최소 | 중간 | 최대 |
| **버전 관리** | 어려움 | 쉬움 | 쉬움 |
| **CI/CD 적합성** | 낮음 | 높음 | 중간 |
| **설정 복잡도** | 낮음 | 중간 | 높음 |
| **권장 용도** | 개인 로컬 개발 | **프로덕션/팀 프로젝트** | Docker 컨테이너 |

---

## 6. 문제 해결 가이드

### 6.1 "브라우저를 찾을 수 없음" 오류

**원인**: 설치 시와 실행 시 `PLAYWRIGHT_BROWSERS_PATH` 불일치[2][8]

**해결책**:
```bash
# 1. 현재 설정 확인
echo $PLAYWRIGHT_BROWSERS_PATH

# 2. 브라우저가 실제로 설치된 위치 확인
playwright install --dry-run chromium

# 3. 환경변수를 영구 설정
echo 'export PLAYWRIGHT_BROWSERS_PATH=$HOME/.playwright-browsers' >> ~/.zshrc
source ~/.zshrc

# 4. 브라우저 재설치
playwright install chromium
```

### 6.2 매번 재설치되는 문제 (crawl4ai)

**원인**:
- `crawl4ai-setup`이 기본 캐시를 사용하지만, 스크립트 실행 시 다른 경로를 참조
- uv 가상환경과 시스템 Playwright CLI 경로 불일치

**해결책**:

**방법 1: 환경변수 고정** (권장)
```bash
# ~/.zshrc에 추가
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.playwright-browsers

# 터미널 재시작 후
crawl4ai-setup
crawl4ai-doctor

# 스크립트 실행
uv run python your_script.py
```

**방법 2: 가상환경 활성화 후 설치**
```bash
source .venv/bin/activate
pip install crawl4ai
crawl4ai-setup

# 실행 시에도 활성화 필요
python your_script.py
```

**방법 3: 절대 경로 사용** (pyproject.toml에 스크립트 추가)
```toml
[project.scripts]
crawl-run = "mcp_server:main"

[tool.crawl4ai]
browser_path = "~/.playwright-browsers"
```

### 6.3 Docker에서 브라우저 실행 실패

**원인**: Chromium이 IPC(Inter-Process Communication)를 위해 공유 메모리(/dev/shm)가 필요하지만, 기본 Docker 할당(64MB)이 부족[7]

**해결책**:
```bash
docker run --shm-size="2g" your-image
```

**Dockerfile 최적화**:
```dockerfile
FROM python:3.13-slim

# Playwright 공식 이미지 사용 (권장)
# FROM mcr.microsoft.com/playwright/python:v1.56.0-noble

# 또는 수동 설정
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers
RUN pip install crawl4ai && playwright install --with-deps chromium
```

### 6.4 프록시 또는 방화벽 환경

**HTTP 프록시 사용**[2]:
```bash
# Bash
export HTTPS_PROXY=https://192.0.2.1
playwright install

# PowerShell
$Env:HTTPS_PROXY="https://192.0.2.1"
playwright install
```

**커스텀 다운로드 서버**[2]:
```bash
export PLAYWRIGHT_DOWNLOAD_HOST=http://internal-mirror.example.com
playwright install
```

**브라우저별 개별 설정**[2]:
```bash
export PLAYWRIGHT_CHROMIUM_DOWNLOAD_HOST=http://mirror1.example.com
export PLAYWRIGHT_FIREFOX_DOWNLOAD_HOST=http://mirror2.example.com
export PLAYWRIGHT_WEBKIT_DOWNLOAD_HOST=http://mirror3.example.com
playwright install
```

**SSL 인증서 문제**[2]:
```bash
export NODE_EXTRA_CA_CERTS="/path/to/cert.pem"
playwright install
```

### 6.5 디버깅 방법

**브라우저 실행 로그 확인**[11]:
```bash
DEBUG=pw:browser pytest
# 또는
DEBUG=pw:browser python your_script.py
```

**crawl4ai 진단 실행**:
```bash
crawl4ai-doctor
```

**수동 브라우저 테스트**[10]:
```bash
# Chromium 직접 실행
playwright open https://example.com
```

---

## 7. 권장 설정 (현재 프로젝트 기준)

### 7.1 최종 권장 워크플로우

현재 환경: **Python 3.13 + uv + crawl4ai + macOS**

**1단계: 환경변수 설정** (~/.zshrc 또는 ~/.bashrc)
```bash
# 브라우저 공유 캐시 디렉토리
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.playwright-browsers

# 선택사항: 가비지 컬렉션 비활성화 (여러 Playwright 버전 사용 시)
# export PLAYWRIGHT_SKIP_BROWSER_GC=1
```

**2단계: 터미널 재시작 및 확인**
```bash
source ~/.zshrc
echo $PLAYWRIGHT_BROWSERS_PATH
# 출력: /Users/seungwonan/.playwright-browsers
```

**3단계: 프로젝트 초기화**
```bash
cd /Users/seungwonan/Dev/curriculum/lecture_materials/crawl4ai-mcp

# uv 가상환경 생성 (이미 존재하면 생략)
uv venv

# crawl4ai 설치
uv pip install crawl4ai

# Playwright 브라우저 설치
uv run playwright install chromium

# 또는 crawl4ai-setup 사용
uv run crawl4ai-setup
```

**4단계: 검증**
```bash
# 진단 실행
uv run crawl4ai-doctor

# 간단한 테스트
uv run python -c "
import asyncio
from crawl4ai import AsyncWebCrawler

async def test():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun('https://example.com')
        print('✓ Success:', len(result.markdown), 'characters')

asyncio.run(test())
"
```

**5단계: MCP 서버 실행**
```bash
uv run python mcp_server.py
```

### 7.2 pyproject.toml 업데이트 (선택사항)

현재 프로젝트에 환경변수 힌트 추가:

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

[project.scripts]
crawl4ai-mcp = "mcp_server:main"

# 환경변수 가이드 (주석)
# PLAYWRIGHT_BROWSERS_PATH=$HOME/.playwright-browsers 설정 권장
```

### 7.3 README 추가 섹션

```markdown
## 환경 설정

Playwright 브라우저를 영구적으로 설정하려면:

1. 환경변수 설정 (~/.zshrc):
   ```bash
   export PLAYWRIGHT_BROWSERS_PATH=$HOME/.playwright-browsers
   ```

2. 브라우저 설치:
   ```bash
   uv run playwright install chromium
   ```

3. 확인:
   ```bash
   uv run crawl4ai-doctor
   ```
```

---

## 8. 추가 참고 자료

### 8.1 공식 문서

- [Playwright Python - Browsers](https://playwright.dev/python/docs/browsers) [1][2]
- [Playwright Python - CI](https://playwright.dev/python/docs/ci) [11]
- [Crawl4AI Installation](https://docs.crawl4ai.com/core/installation/) [6][7][16]
- [uv Documentation](https://github.com/astral-sh/uv) [13]

### 8.2 커뮤니티 리소스

- [Playwright GitHub Issues - Caching](https://github.com/microsoft/playwright/issues/7249) [12]
- [uv + Playwright Integration](https://github.com/astral-sh/uv/issues/11818) [4]
- [Docker with uv and Playwright](https://www.xiegerts.com/post/uv-docker-scrapy-playwright/) [5]

### 8.3 관련 GitHub Issues

- [playwright-python#576 - ENV workaround](https://github.com/microsoft/playwright-python/issues/576) [15]
- [Aider AI - Playwright installation issues](https://github.com/Aider-AI/aider/issues/3188) [17]

---

## 결론

Playwright 브라우저 중복 설치 문제는 **환경변수 일관성 유지**로 해결됩니다. 핵심은 `PLAYWRIGHT_BROWSERS_PATH`를 시스템 레벨에서 설정하고, 모든 설치 및 실행 과정에서 동일한 값을 사용하는 것입니다.

**즉시 적용 가능한 해결책**:
```bash
# ~/.zshrc에 추가
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.playwright-browsers

# 재설치
source ~/.zshrc
uv run playwright install chromium
```

이 설정은 프로젝트 간 브라우저 공유, 디스크 공간 절약, 재현 가능한 환경을 모두 만족시키며, 2025년 기준 Playwright 및 crawl4ai의 최신 권장사항과 일치합니다.

---

## Footnotes

[1] [Playwright Python - Managing browser binaries](https://playwright.dev/python/docs/browsers#managing-browser-binaries)
[2] [Playwright Python - Browsers Documentation](https://playwright.dev/python/docs/browsers)
[3] [Playwright - Browser Installation](https://playwright.dev/docs/browsers)
[4] [uv GitHub Issue #11818 - Playwright integration](https://github.com/astral-sh/uv/issues/11818)
[5] [Dockerfile with uv for Scrapy and Playwright](https://www.xiegerts.com/post/uv-docker-scrapy-playwright/)
[6] [Crawl4AI - Basic Installation](https://docs.crawl4ai.com/core/installation/#1-basic-installation)
[7] [Crawl4AI Installation Guide - Crawl4.com](https://www.crawl4.com/blog/crawl4ai-setup-guide-install-config-best-practices)
[8] [Playwright Solutions - GitHub Actions cache](https://playwrightsolutions.com/playwright-github-action-to-cache-the-browser-binaries/)
[9] [Playwright - Stale browser removal](https://playwright.dev/python/docs/browsers#stale-browser-removal)
[10] [Playwright - Chromium headless modes](https://playwright.dev/python/docs/browsers#chromium-new-headless-mode)
[11] [Playwright Python - Continuous Integration](https://playwright.dev/python/docs/ci)
[12] [GitHub Issue #7249 - Caching on GitHub Actions](https://github.com/microsoft/playwright/issues/7249)
[13] [InfoWorld - How to use uv](https://www.infoworld.com/article/2336295/how-to-use-uv-a-superfast-python-package-installer.html)
[14] [GitHub - astral-sh/uv](https://github.com/astral-sh/uv)
[15] [playwright-python#576 - ENV workaround](https://github.com/microsoft/playwright-python/issues/576)
[16] [Crawl4AI - Diagnostics](https://docs.crawl4ai.com/core/installation/#22-diagnostics)
[17] [Aider AI Issue #3188 - Playwright installation](https://github.com/Aider-AI/aider/issues/3188)
