# Crawl4AI Documentation Crawler

Crawl4AI 라이브러리 기반 웹 문서 크롤링 도구입니다. 문서 사이트를 크롤링하여 마크다운 파일로 저장합니다.

## 기능

- **단일 페이지 크롤링**: 특정 페이지만 크롤링하여 마크다운으로 변환
- **Deep Crawl**: 재귀적으로 링크를 추적하여 전체 문서 사이트 크롤링
- **URL 프리픽스 필터**: 특정 경로의 페이지만 선택적으로 크롤링
- **자동 네비게이션 제거**: 크롤링된 문서에서 네비게이션/푸터 자동 제거
- **도메인 기반 출력**: 도메인명을 기반으로 자동 디렉토리 생성

## 설치

```bash
# 의존성 설치
uv sync
```

## 사용법

### 기본 사용 (단일 페이지 크롤링)

```bash
# 콘솔에 마크다운 출력
uv run cli.py crawl https://docs.crawl4ai.com

# 파일로 저장
uv run cli.py crawl https://docs.crawl4ai.com -o output
```

### Deep Crawl (재귀적 크롤링)

```bash
# 기본 Deep Crawl (최대 100페이지, 깊이 2)
uv run cli.py crawl https://docs.crawl4ai.com --recursive

# 페이지 수와 깊이 제한
uv run cli.py crawl https://docs.crawl4ai.com \
  --recursive \
  --max-pages 50 \
  --max-depth 3

# URL 프리픽스 필터 사용 (특정 경로만 크롤링)
uv run cli.py crawl https://developers.figma.com/docs/figma-mcp-server \
  --recursive \
  --prefix https://developers.figma.com/docs/figma-mcp-server
```

### CLI 옵션

| 옵션 | 단축 | 설명 | 기본값 |
|------|------|------|--------|
| `--output-dir` | `-o` | 출력 디렉토리 | 도메인명 (Deep Crawl) / 미지정 시 콘솔 출력 (단일 페이지) |
| `--recursive` | `-r` | Deep Crawl 모드 활성화 | `False` |
| `--max-pages` | `-p` | 최대 크롤링 페이지 수 (Deep Crawl 전용) | `100` |
| `--max-depth` | `-d` | 최대 크롤링 깊이 (Deep Crawl 전용) | `2` |
| `--prefix` | `-px` | URL 프리픽스 필터 (Deep Crawl 전용) | `None` |

### 설정 프리셋 확인

```bash
uv run cli.py config-list
```

## 출력 형식

### 단일 페이지 모드
- `output_dir` 미지정: 콘솔에 마크다운 출력
- `output_dir` 지정: `{output_dir}/index.md` 형식으로 저장

### Deep Crawl 모드
URL 경로를 디렉토리 구조로 변환하여 저장:

```
https://docs.crawl4ai.com/core/deep-crawling/
→ docs_crawl4ai_com/core/deep-crawling.md

https://developers.figma.com/docs/api
→ developers_figma_com/docs/api.md
```

## 프로젝트 구조

```
.
├── cli.py              # CLI 인터페이스
├── core.py             # 핵심 크롤링 로직
├── configs/            # 설정 프리셋
│   ├── browser.py      # 브라우저 설정
│   ├── crawler.py      # 크롤러 설정
│   └── deep_crawl.py   # Deep Crawl 전략
├── strategies/         # 컨텐츠 처리 전략
│   └── content.py      # 마크다운 정리
└── utils/              # 유틸리티 함수
    ├── domain.py       # 도메인 추출
    └── path.py         # URL → 파일경로 변환
```

## 예시

### Figma MCP Server 문서 크롤링

```bash
# Figma MCP Server 문서만 크롤링 (프리픽스 필터 사용)
uv run cli.py crawl https://developers.figma.com/docs/figma-mcp-server \
  --recursive \
  --prefix https://developers.figma.com/docs/figma-mcp-server \
  --max-pages 20

# 결과: developers_figma_com/ 디렉토리에 저장
```

### Crawl4AI 문서 전체 크롤링

```bash
# 전체 문서 크롤링
uv run cli.py crawl https://docs.crawl4ai.com \
  --recursive \
  --max-pages 100 \
  --max-depth 3

# 결과: docs_crawl4ai_com/ 디렉토리에 저장
```

## 참고사항

1. **인코딩**: 모든 파일은 UTF-8로 저장됩니다
2. **네비게이션 제거**: 크롤링 시 자동으로 네비게이션/푸터가 제거됩니다
3. **도메인 필터**: Deep Crawl 시 동일 도메인 페이지만 크롤링됩니다
4. **URL 헤더**: 각 마크다운 파일 상단에 원본 URL이 헤더로 추가됩니다

## 기술 스택

- **Crawl4AI**: 웹 크롤링 라이브러리
- **Typer**: CLI 프레임워크
- **AsyncIO**: 비동기 크롤링
- **Python 3.13+**: 최신 Python 버전

## 라이센스

MIT License

## 기여

이슈 및 PR은 언제든 환영합니다.
