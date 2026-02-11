"""Browser configuration presets."""

from crawl4ai import BrowserConfig

# 빠른 크롤링용 - 텍스트 모드, 최소 리소스
FAST_CONFIG = BrowserConfig(
    headless=True,
    text_mode=True,  # 이미지 비활성화
    light_mode=True,  # 백그라운드 기능 최소화로 성능 향상
    viewport_width=1280,
    viewport_height=720,
    verbose=False,
)

# 디버깅용 - 브라우저 표시, 상세 로그
DEBUG_CONFIG = BrowserConfig(
    headless=False,
    viewport_width=1920,
    viewport_height=1080,
    verbose=True,
)

# 스텔스 크롤링용 - playwright-stealth 기반 봇 감지 회피
STEALTH_CONFIG = BrowserConfig(
    headless=True,
    viewport_width=1920,
    viewport_height=1080,
    enable_stealth=True,  # playwright-stealth로 브라우저 핑거프린트 수정
    user_agent_mode="random",  # 랜덤 User-Agent로 봇 감지 회피
)

# 프록시 사용 예시
def create_proxy_config(proxy_url: str, username: str = None, password: str = None) -> BrowserConfig:
    """프록시를 사용하는 브라우저 설정 생성

    Args:
        proxy_url: 프록시 서버 URL (예: "http://proxy.example.com:8080")
        username: 프록시 인증 사용자명
        password: 프록시 인증 비밀번호
    """
    proxy_config = {"server": proxy_url}
    if username and password:
        proxy_config["username"] = username
        proxy_config["password"] = password

    return BrowserConfig(
        headless=True,
        proxy_config=proxy_config,
        verbose=True,
    )
