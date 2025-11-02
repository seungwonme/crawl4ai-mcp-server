"""Browser configuration presets."""

from crawl4ai import BrowserConfig

# 빠른 크롤링용 - 텍스트 모드, 최소 리소스
FAST_CONFIG = BrowserConfig(
    headless=True,
    text_mode=True,  # 이미지 비활성화
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

# 스텔스 크롤링용 - 봇 감지 회피
STEALTH_CONFIG = BrowserConfig(
    headless=True,
    viewport_width=1920,
    viewport_height=1080,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    extra_args=["--disable-blink-features=AutomationControlled"],
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
