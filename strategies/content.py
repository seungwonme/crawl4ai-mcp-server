"""Content processing strategies."""

import re


def clean_navigation_content(markdown: str) -> str:
    """마크다운에서 네비게이션 컨텐츠 제거

    제거 대상:
    - 첫 heading 이전의 리스트/링크
    - "Was this page helpful?" 섹션
    - "ON THIS PAGE" 섹션
    - 푸터 링크 (FigJam, Enterprise 등)
    - "Next/Previous" 네비게이션

    Args:
        markdown: 원본 마크다운 텍스트

    Returns:
        정리된 마크다운 텍스트
    """
    lines = markdown.split("\n")
    content_start = 0
    content_end = len(lines)

    # 첫 번째 heading 찾기
    for i, line in enumerate(lines):
        stripped = line.strip()

        # 빈 줄이거나 리스트/링크인 경우 계속
        if not stripped or stripped.startswith("*") or stripped.startswith("["):
            continue

        # 첫 번째 heading을 찾으면 시작점으로 설정
        if stripped.startswith("#") and i > 0:
            content_start = i
            break

    # 하단 네비게이션/푸터 제거를 위한 패턴
    footer_patterns = [
        r"Was this page helpful\?",
        r"ON THIS PAGE",
        r"\[Next\s+.*\]",
        r"\[Previous\s+.*\]",
        r"Community Forum",
        r"Discord Server",
        r"GitHub Samples",
        r"FigJam.*Enterprise.*Learn",
    ]

    # 하단에서 푸터 시작점 찾기
    for i in range(len(lines) - 1, content_start, -1):
        line = lines[i]
        for pattern in footer_patterns:
            if re.search(pattern, line):
                content_end = i
                break
        if content_end < len(lines):
            break

    result = "\n".join(lines[content_start:content_end]).strip()

    # 추가 정리: 연속된 빈 줄을 하나로
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result


def extract_main_content(html: str) -> str:
    """HTML에서 메인 컨텐츠만 추출

    nav, header, footer, aside 태그 제거

    Args:
        html: 원본 HTML

    Returns:
        정리된 HTML
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    # 네비게이션 관련 태그 제거
    for tag in soup.find_all(["nav", "header", "footer", "aside"]):
        tag.decompose()

    return str(soup)
