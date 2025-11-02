# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

웹 문서 크롤링 도구 - Crawl4AI 라이브러리 기반으로 문서 사이트를 크롤링하여 마크다운으로 저장합니다.

## Core Architecture

### Entry Points
- **cli.py**: Typer 기반 CLI 인터페이스 (메인 엔트리포인트)
- **core.py**: 핵심 크롤링 로직
  - `crawl_single_page()`: 단일 페이지 크롤링 및 마크다운 반환
  - `crawl_documentation()`: Deep Crawl (재귀적 링크 추적)

### Configuration System (configs/)
설정은 세 가지 레이어로 분리:
- **browser.py**: 브라우저 설정 프리셋 (FAST_CONFIG, DEBUG_CONFIG, STEALTH_CONFIG)
- **crawler.py**: 크롤러 실행 설정 (DOCS_CRAWL_CONFIG, TEXT_ONLY_CONFIG, COMPREHENSIVE_CONFIG)
- **deep_crawl.py**: Deep Crawl 전략 팩토리 함수 (BFS/Best-First 전략 생성)

### Processing Pipeline

**단일 페이지 모드 (기본)**:
1. URL → `core.crawl_single_page()`
2. AsyncWebCrawler로 페이지 크롤링
3. 마크다운 정리 (strategies/content.py)
4. 파일 저장 또는 콘솔 출력

**Deep Crawl 모드 (--recursive)**:
1. URL → `core.crawl_documentation()`
2. Domain 추출 → 출력 디렉토리 생성 (utils/domain.py)
3. Deep Crawl 전략 생성 (configs/deep_crawl.py)
4. AsyncWebCrawler로 비동기 크롤링
5. 각 결과마다:
   - URL → 파일경로 변환 (utils/path.py)
   - 마크다운 정리 (strategies/content.py)
   - 파일 저장

### Content Processing Strategy (strategies/)
- **content.py**:
  - `clean_navigation_content()`: 마크다운에서 네비게이션 제거
    - 첫 heading 이전의 리스트/링크 제거
    - "Was this page helpful?", "ON THIS PAGE" 섹션 제거
    - Next/Previous 네비게이션 제거
    - 푸터 링크 (Community Forum, Discord, GitHub 등) 제거
  - `extract_main_content()`: HTML에서 nav/header/footer/aside 제거 (사용 안 함)

## Common Commands

### Development
```bash
# 의존성 설치
uv sync

# 크롤링 실행
uv run python cli.py crawl <URL> [options]

# 단일 페이지 크롤링 (기본)
uv run cli.py crawl https://docs.crawl4ai.com

# 단일 페이지를 파일로 저장
uv run cli.py crawl https://docs.crawl4ai.com -o output

# Deep Crawl (재귀적 크롤링)
uv run cli.py crawl https://docs.crawl4ai.com --recursive --max-pages 10 --max-depth 2

# URL 프리픽스 필터 사용 (Deep Crawl 전용)
uv run cli.py crawl https://developers.figma.com/docs/figma-mcp-server \
  --recursive --prefix https://developers.figma.com/docs/figma-mcp-server

# 설정 프리셋 확인
uv run python cli.py config-list

# 직접 테스트 (core.py)
uv run python core.py
```

### CLI Options
- `--output-dir, -o`: 출력 디렉토리 (기본값: 도메인명 / 미지정 시 콘솔 출력)
- `--recursive, -r`: 재귀적으로 링크를 따라가며 크롤링 (Deep Crawl 모드)
- `--max-pages, -p`: 최대 크롤링 페이지 수 (기본값: 100, --recursive 사용 시)
- `--max-depth, -d`: 최대 크롤링 깊이 (기본값: 2, --recursive 사용 시)
- `--prefix, -px`: URL 프리픽스 필터 (--recursive 전용, 지정 시 해당 프리픽스로 시작하는 URL만 크롤링)

## Key Implementation Details

### Domain Extraction Logic (utils/domain.py)
- `developers.figma.com` → `developers_figma_com` (모든 `.`을 `_`로 변경)
- `docs.crawl4ai.com` → `docs_crawl4ai_com` (www 제거 후 `.`을 `_`로 변경)
- `www.example.com` → `example_com` (www 제거 후 `.`을 `_`로 변경)

### URL to Filepath Conversion (utils/path.py)
- `https://docs.crawl4ai.com/core/deep-crawling/` → `{output_dir}/core/deep-crawling.md`
- 루트 URL (`/`) → `index.md`

### Deep Crawl Strategies
- **BFS Strategy**: 너비 우선 탐색, 동일 도메인만
  - `create_bfs_strategy()` 함수로 생성
  - `url_prefix` 파라미터로 URL 프리픽스 필터 적용 가능
- **Best-First Strategy**: 키워드 기반 우선순위 (문서 사이트용)
- 모든 전략은 DomainFilter로 동일 도메인만 크롤링
- **URL Prefix Filter**:
  - `URLPatternFilter(patterns=[f"{prefix}*"], use_glob=True)` 형태로 구현
  - DomainFilter와 함께 FilterChain에 추가
  - 예: `https://example.com/docs/api` → `https://example.com/docs/api/*`만 크롤링

### Configuration Cloning Pattern
```python
# configs에서 기본 설정 가져와서 strategy만 오버라이드
config = DOCS_CRAWL_CONFIG.clone(deep_crawl_strategy=strategy)
```

### Async Streaming Pattern

**Deep Crawl (여러 페이지)**:
```python
async with AsyncWebCrawler() as crawler:
    async for result in await crawler.arun(start_url, config=config):
        # 스트리밍 처리
```

**단일 페이지**:
```python
async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url, config=config)
    # 결과 처리
```

### URL Prefix Filter Implementation
```python
# configs/deep_crawl.py
filters = [DomainFilter(allowed_domains=[domain])]

if url_prefix:
    filters.append(URLPatternFilter(
        patterns=[f"{url_prefix}*"],
        use_glob=True
    ))

filter_chain = FilterChain(filters)
```

## Important Notes

1. **크롤링 모드**:
   - **단일 페이지 모드 (기본)**: 지정된 URL만 크롤링, 마크다운 반환/저장
     - `output_dir` 미지정: 마크다운을 콘솔에 출력
     - `output_dir` 지정: 마크다운을 파일로 저장
   - **Deep Crawl 모드 (--recursive)**: 링크를 재귀적으로 추적하여 여러 페이지 크롤링
     - 항상 파일로 저장 (`output_dir` 기본값: 도메인명)
   - **CLI 유효성 검사**: `--prefix` 옵션은 `--recursive` 없이 사용 시 에러 발생

2. **인코딩**: 모든 파일 저장 시 `encoding="utf-8"` 명시 필수

3. **에러 처리**: `result.success` 체크 후 실패한 URL은 콘솔에만 출력 (`❌ Failed: {url}`)

4. **마크다운 정리 (2단계 전략)**:
   - **HTML 레벨** (configs/crawler.py): `excluded_tags=["script", "style"]`
     - nav, header, footer는 제거하지 않음 → Deep Crawl 시 링크 추출 필요
   - **마크다운 레벨** (strategies/content.py): `clean_navigation_content()`
     - 첫 heading 이전 리스트/링크 제거
     - 정규식 패턴으로 푸터/네비게이션 제거
     - "Was this page helpful?", "ON THIS PAGE", "Next/Previous" 등
   - 저장 시 URL을 헤더로 추가: `# {url}\n\n{content}`

5. **설정 확장**: 새로운 프리셋 추가 시 configs/ 디렉토리에 추가하고 `cli.py config-list` 명령어 업데이트
