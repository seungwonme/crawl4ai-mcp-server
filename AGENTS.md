# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

웹 문서 크롤링 MCP 서버 - Crawl4AI 라이브러리 기반으로 문서 사이트를 크롤링하여 마크다운으로 저장합니다.

## Package Structure

```
crawl4ai-mcp-server/
├── pyproject.toml                    # 패키지 설정 (hatchling 빌드)
├── src/
│   └── crawl4ai_mcp_server/
│       ├── __init__.py               # 패키지 메타데이터
│       ├── server.py                 # MCP 서버 (FastMCP 기반)
│       ├── core.py                   # 핵심 크롤링 로직
│       ├── cli.py                    # Typer 기반 CLI
│       ├── configs/                  # 설정 프리셋
│       │   ├── browser.py            # BrowserConfig 프리셋
│       │   ├── crawler.py            # CrawlerRunConfig 프리셋
│       │   └── deep_crawl.py         # Deep Crawl 전략 팩토리
│       ├── strategies/
│       │   └── content.py            # 마크다운 정리
│       └── utils/
│           ├── domain.py             # 도메인 추출
│           └── path.py               # URL → 파일경로 변환
```

### Entry Points
- **server.py**: MCP 서버 인터페이스 (엔트리포인트: `crawl4ai_mcp_server.server:main`)
- **cli.py**: Typer 기반 CLI 인터페이스
- **core.py**: 핵심 크롤링 로직
  - `crawl_single_page()`: 단일 페이지 크롤링 및 마크다운 반환
  - `crawl_documentation()`: Deep Crawl (재귀적 링크 추적)

### Configuration System (configs/)
설정은 세 가지 레이어로 분리:
- **browser.py**: 브라우저 설정 프리셋 (FAST_CONFIG, DEBUG_CONFIG, STEALTH_CONFIG)
- **crawler.py**: 크롤러 실행 설정 (DOCS_CRAWL_CONFIG, TEXT_ONLY_CONFIG, COMPREHENSIVE_CONFIG)
  - 모든 설정에 `LXMLWebScrapingStrategy` 적용 (고속 HTML 파싱)
- **deep_crawl.py**: Deep Crawl 전략 팩토리 함수 (BFS/DFS/Best-First 전략 생성)
  - 모든 전략에 `ContentTypeFilter(allowed_types=["text/html"])` 적용

### Processing Pipeline

**단일 페이지 모드 (기본)**:
1. URL → `core.crawl_single_page()`
2. `AsyncWebCrawler(config=BrowserConfig)` 로 페이지 크롤링
3. 마크다운 정리 (strategies/content.py)
4. 파일 저장 또는 콘솔 출력

**Deep Crawl 모드 (--recursive)**:
1. URL → `core.crawl_documentation()`
2. Domain 추출 → 출력 디렉토리 생성 (utils/domain.py)
3. Deep Crawl 전략 생성 (configs/deep_crawl.py) - BFS 또는 DFS 선택 가능
4. `AsyncWebCrawler(config=BrowserConfig)` 로 비동기 크롤링
5. 각 결과마다:
   - URL → 파일경로 변환 (utils/path.py)
   - 마크다운 정리 (strategies/content.py)
   - 파일 저장

## Installation & Configuration

### 다른 사용자 (uvx로 바로 사용)
```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/seungwonme/crawl4ai-mcp-server", "crawl4ai-mcp-server"]
    }
  }
}
```

### PyPI 배포 후 (향후)
```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "uvx",
      "args": ["crawl4ai-mcp-server"]
    }
  }
}
```

### 로컬 개발
```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/crawl4ai-mcp-server", "crawl4ai-mcp-server"]
    }
  }
}
```

## MCP Server

### Tools
MCP 서버는 두 개의 도구를 제공합니다:

1. **crawl_page**: 단일 페이지 크롤링
   - `url` (필수): 크롤링할 URL
   - `output_dir` (선택): 출력 디렉토리 (미지정 시 마크다운만 반환)
   - `stealth` (선택): 스텔스 모드 (봇 감지 우회, 기본값: false)

2. **crawl_docs**: 재귀적 크롤링 (Deep Crawl)
   - `url` (필수): 시작 URL
   - `output_dir` (선택): 출력 디렉토리 (기본값: 도메인명)
   - `max_pages` (선택): 최대 페이지 수 (기본값: 100)
   - `max_depth` (선택): 최대 깊이 (기본값: 2)
   - `url_prefix` (선택): URL 프리픽스 필터
   - `strategy` (선택): 크롤링 전략 - "bfs" (기본) 또는 "dfs"
   - `stealth` (선택): 스텔스 모드 (봇 감지 우회, 기본값: false)

### Running the MCP Server
```bash
# 엔트리포인트로 실행
uv run crawl4ai-mcp-server

# 개발 모드 (Inspector UI)
uv run mcp dev src/crawl4ai_mcp_server/server.py
```

## Common Commands

### Development
```bash
# 의존성 설치
uv sync

# 단일 페이지 크롤링 (기본)
uv run python -m crawl4ai_mcp_server.cli crawl https://docs.crawl4ai.com

# 단일 페이지를 파일로 저장
uv run python -m crawl4ai_mcp_server.cli crawl https://docs.crawl4ai.com -o output

# Deep Crawl (재귀적 크롤링) - BFS 기본
uv run python -m crawl4ai_mcp_server.cli crawl https://docs.crawl4ai.com --recursive --max-pages 10 --max-depth 2

# Deep Crawl - DFS 전략
uv run python -m crawl4ai_mcp_server.cli crawl https://docs.crawl4ai.com --recursive --strategy dfs --max-pages 10

# URL 프리픽스 필터 사용 (Deep Crawl 전용)
uv run python -m crawl4ai_mcp_server.cli crawl https://developers.figma.com/docs/figma-mcp-server \
  --recursive --prefix https://developers.figma.com/docs/figma-mcp-server
```

### CLI Options
- `--output-dir, -o`: 출력 디렉토리 (기본값: 도메인명 / 미지정 시 콘솔 출력)
- `--recursive, -r`: 재귀적으로 링크를 따라가며 크롤링 (Deep Crawl 모드)
- `--max-pages, -p`: 최대 크롤링 페이지 수 (기본값: 100, --recursive 사용 시)
- `--max-depth, -d`: 최대 크롤링 깊이 (기본값: 2, --recursive 사용 시)
- `--prefix, -px`: URL 프리픽스 필터 (--recursive 전용, 지정 시 해당 프리픽스로 시작하는 URL만 크롤링)
- `--strategy, -s`: 크롤링 전략 (--recursive 전용, `bfs` 기본 또는 `dfs`)

## Key Implementation Details

### BrowserConfig + CrawlerRunConfig 패턴 (공식 권장)
```python
# BrowserConfig: 브라우저 환경 설정 (한 번 생성)
browser_config = BrowserConfig(headless=True, text_mode=True, light_mode=True)

# CrawlerRunConfig: 크롤링 실행 설정 (호출마다 다르게 가능)
crawler_config = CrawlerRunConfig(
    scraping_strategy=LXMLWebScrapingStrategy(),
    cache_mode=CacheMode.BYPASS,
    ...
)

# AsyncWebCrawler에 BrowserConfig 전달
async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(url, config=crawler_config)
```

### Deep Crawl Strategies
- **BFS Strategy**: 너비 우선 탐색, 동일 도메인만
- **DFS Strategy**: 깊이 우선 탐색, 한 경로를 끝까지 탐색 후 백트래킹
- **Best-First Strategy**: 키워드 기반 우선순위 (문서 사이트용)
- 모든 전략은 `DomainFilter` + `ContentTypeFilter`로 동일 도메인 HTML만 크롤링
- 공통 필터 체인은 `_build_filter_chain()` 헬퍼로 생성

## Important Notes

1. **패키지 구조**: `src/crawl4ai_mcp_server/` 레이아웃, 모든 내부 import는 상대 import (`.`) 사용
2. **엔트리포인트**: `crawl4ai_mcp_server.server:main` → `uvx crawl4ai-mcp-server`로 실행
3. **인코딩**: 모든 파일 저장 시 `encoding="utf-8"` 명시 필수
4. **에러 처리**: `result.success` 체크 후 실패한 URL은 stderr에 출력
5. **마크다운 정리**: HTML 레벨 (`excluded_tags`) + 마크다운 레벨 (`clean_navigation_content()`) 2단계 전략
