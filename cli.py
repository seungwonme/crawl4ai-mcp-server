"""CLI interface for the crawler."""

import asyncio

import typer

from core import crawl_documentation, crawl_single_page

app = typer.Typer(help="공식문서 크롤러 - 웹사이트를 크롤링하여 디렉토리 구조로 저장")


@app.command()
def crawl(
    url: str = typer.Argument(..., help="크롤링할 시작 URL"),
    output_dir: str = typer.Option(None, "--output-dir", "-o", help="출력 디렉토리 (기본: 도메인명)"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="재귀적으로 링크를 따라가며 크롤링 (Deep Crawl)"),
    max_pages: int = typer.Option(100, "--max-pages", "-p", help="최대 크롤링 페이지 수 (--recursive 사용 시)"),
    max_depth: int = typer.Option(2, "--max-depth", "-d", help="최대 크롤링 깊이 (--recursive 사용 시)"),
    prefix: str = typer.Option(None, "--prefix", "-px", help="URL 프리픽스 필터 (--recursive 사용 시, 지정 시 해당 프리픽스로 시작하는 URL만 크롤링)"),
):
    """웹사이트 크롤링 실행"""
    # 유효성 검사: --prefix는 --recursive와 함께만 사용 가능
    if prefix and not recursive:
        typer.echo("❌ Error: --prefix 옵션은 --recursive 옵션과 함께 사용해야 합니다.", err=True)
        raise typer.Exit(code=1)

    if recursive:
        # Deep Crawl 모드
        asyncio.run(crawl_documentation(url, output_dir, max_pages, max_depth, prefix))
    else:
        # 단일 페이지 모드
        markdown = asyncio.run(crawl_single_page(url, output_dir))
        if not output_dir:
            # 출력 디렉토리가 없으면 마크다운 출력
            typer.echo("\n" + markdown)


@app.command()
def config_list():
    """사용 가능한 설정 프리셋 목록"""
    print("=== Browser Configs ===")
    print("- FAST_CONFIG: 빠른 크롤링용 (텍스트 모드)")
    print("- DEBUG_CONFIG: 디버깅용 (브라우저 표시)")
    print("- STEALTH_CONFIG: 스텔스 크롤링용")

    print("\n=== Crawler Configs ===")
    print("- DOCS_CRAWL_CONFIG: 문서 크롤링 기본 설정")
    print("- TEXT_ONLY_CONFIG: 빠른 텍스트 추출용")
    print("- COMPREHENSIVE_CONFIG: 전체 데이터 수집용")


if __name__ == "__main__":
    app()
