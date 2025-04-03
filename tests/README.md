알겠습니다! 파이썬이나 프로그래밍, 테스트 등에 대해 전혀 모른다고 가정하고 이 코드를 한 줄 한 줄 차근차근 설명해 드릴게요. 마치 레고 블록을 조립하는 설명서를 보듯 따라오시면 됩니다.

**1. 필요한 도구 가져오기 (Import)**

```python
import asyncio
import pytest
import pytest_asyncio
from crawl4ai import AsyncWebCrawler
```

- `import asyncio`: `asyncio`라는 도구 상자를 가져옵니다. 이 도구는 프로그램이 여러 작업을 동시에 처리하는 것처럼 보이게 도와줍니다. 특히 웹사이트 로딩처럼 시간이 걸리는 작업을 기다리는 동안 다른 일을 할 수 있게 해줘서 효율적입니다. (비동기 처리)
- `import pytest`: `pytest`라는 도구 상자를 가져옵니다. 이 도구는 우리가 만든 코드가 제대로 작동하는지 확인하는 '테스트'를 만들고 실행하는 데 사용됩니다.
- `import pytest_asyncio`: `pytest` 도구 상자의 확장팩입니다. 위에서 가져온 `asyncio` 도구를 사용하는 코드를 테스트할 때 특별히 필요한 기능들을 제공합니다.
- `from crawl4ai import AsyncWebCrawler`: `crawl4ai`라는 이름의 크롤링 전문 도구 상자에서 `AsyncWebCrawler`라는 특정 도구(설계도 혹은 클래스)를 가져옵니다. 이 `AsyncWebCrawler`가 실제로 웹사이트에 접속해서 정보를 가져오는 역할을 합니다. 'Async'가 붙어있으니, `asyncio`와 함께 작동하는 똑똑한 크롤러입니다.

```python
# playwright 관련 import는 필요 없음
```

- 주석입니다. `#`으로 시작하는 줄은 컴퓨터가 무시합니다. 사람에게 설명을 남기는 용도죠. 여기서는 이 코드에 직접 `playwright`를 가져오는 부분이 없다는 메모입니다. (`crawl4ai`가 내부적으로 `playwright`라는 다른 도구를 사용하긴 합니다.)

```python
from src.config.browser import setup_browser_config
from src.config.markdown import setup_markdown_generator
from src.config.run import setup_run_config
from tests.utils.file import save_png_to_unique_file, save_text_to_unique_file
```

- 이 줄들은 우리가 _직접 만든_ 다른 파일들에서 필요한 도구(함수)들을 가져오는 부분입니다.
- `from src.config.browser import setup_browser_config`: `src/config/browser.py` 파일 안에 있는 `setup_browser_config`라는 함수를 가져옵니다. 이 함수는 웹 브라우저(크롬 같은 것)를 어떻게 설정할지에 대한 정보를 만들어줍니다 (예: 눈에 보이게 할지, 숨어서 작동하게 할지 등).
- `from src.config.markdown import setup_markdown_generator`: `src/config/markdown.py` 파일 안의 `setup_markdown_generator` 함수를 가져옵니다. 웹사이트에서 가져온 정보를 '마크다운'이라는 보기 좋은 형식으로 만드는 방법을 설정하는 함수입니다.
- `from src.config.run import setup_run_config`: `src/config/run.py` 파일 안의 `setup_run_config` 함수를 가져옵니다. 크롤러가 한 번 작동할 때 필요한 여러 설정들을 묶어주는 함수입니다.
- `from tests.utils.file import ...`: `tests/utils/file.py` 파일 안의 `save_png_to_unique_file`, `save_text_to_unique_file` 함수들을 가져옵니다. 이 함수들은 테스트 결과를 파일(텍스트 파일, 이미지 파일)로 저장하는 역할을 합니다.

**2. 테스트할 웹사이트 주소 목록**

```python
stock_urls = [
    "https://finance.naver.com/sise/",
    "https://finance.yahoo.com/most-active",
]
```

- `stock_urls = [...]`: `stock_urls`라는 이름의 목록(리스트)을 만듭니다. 이 목록에는 우리가 테스트에서 방문해볼 웹사이트 주소(URL) 두 개가 들어있습니다. 첫 번째는 네이버 금융, 두 번째는 야후 파이낸스입니다.

**3. 특별한 준비 작업 1: 이벤트 루프 만들기 (세션 단위)**

```python
# --- 세션 스코프 이벤트 루프 정의 (다시 추가) ---
# 세션 스코프의 비동기 픽스처(webcrawler)를 지원하기 위해 필요합니다.
@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

- `@pytest.fixture(scope="session")`: 이 줄은 마법 지팡이 같은 역할을 합니다. 아래에 정의될 `event_loop` 함수가 평범한 함수가 아니라, `pytest` 테스트를 위한 '준비물'(픽스처)임을 알려줍니다. `scope="session"`은 이 준비물을 딱 **한 번만** 만들어서, 전체 테스트가 진행되는 동안 계속 사용하겠다는 의미입니다. (테스트 시작할 때 만들고, 모든 테스트 끝날 때 정리)
- `def event_loop(request):`: `event_loop`라는 이름의 준비물(함수)을 정의합니다. `request`는 `pytest`가 내부적으로 사용하는 정보인데, 지금은 몰라도 괜찮습니다.
- `"""..."""`: 함수에 대한 설명입니다 (독스트링). 이 준비물은 테스트 세션(전체 테스트 과정)을 위한 기본 이벤트 루프 인스턴스를 만든다고 설명하네요.
- `loop = asyncio.get_event_loop_policy().new_event_loop()`: `asyncio` 도구 상자를 사용해서 '이벤트 루프'라는 것을 새로 만듭니다. 이벤트 루프는 비동기 작업(기다림이 필요한 작업)들을 관리하고 순서를 조절하는 일꾼이라고 생각하면 쉽습니다. 세션 스코프이므로 이 일꾼은 전체 테스트 동안 딱 한 명만 존재합니다.
- `yield loop`: 여기가 중요합니다! `yield`는 '잠시 빌려준다'는 의미입니다. 이 준비물 함수는 여기서 멈추고, 만들어진 `loop` (이벤트 루프 일꾼)를 필요한 곳(뒤에 나올 `webcrawler` 준비물)에 빌려줍니다. 그리고 모든 테스트가 끝날 때까지 기다립니다.
- `loop.close()`: 모든 테스트가 끝나고 `yield` 다음으로 돌아오면, 빌려줬던 `loop` 일꾼을 깔끔하게 정리(종료)합니다.

**왜 이게 필요할까요?** 우리가 만들 다음 준비물(`webcrawler`)은 비동기 작업이고 세션 스코프입니다. 세션 전체에 걸쳐 비동기 작업을 관리할 일꾼(`event_loop`)도 세션 스코프로 만들어줘야 서로 호흡을 맞출 수 있기 때문입니다.

**4. 특별한 준비 작업 2: 웹 크롤러 만들기 (세션 단위)**

```python
# --- 세션 스코프 웹크롤러 픽스처 ---
# 정의된 세션 스코프 event_loop를 사용합니다.
@pytest_asyncio.fixture(scope="session")
async def webcrawler(event_loop):  # 세션 스코프 event_loop 파라미터 추가
    """테스트 세션 동안 AsyncWebCrawler 인스턴스를 관리합니다."""
    print("\n>>> [Session] 웹크롤러/브라우저 시작")
    browser_conf = setup_browser_config()
    async with AsyncWebCrawler(config=browser_conf) as crawler:
        print(">>> [Session] 웹크롤러/브라우저 시작 완료")
        yield crawler
    print(">>> [Session] 웹크롤러/브라우저 종료 완료")
```

- `@pytest_asyncio.fixture(scope="session")`: 이번에도 준비물(픽스처)을 만드는데, `pytest_asyncio`의 것을 사용합니다. 왜냐하면 이 준비물 자체가 비동기 작업(`async def`)이기 때문입니다. `scope="session"`은 역시 이 준비물(웹 크롤러)도 전체 테스트 동안 딱 **하나만** 만들어서 공유하겠다는 뜻입니다.
- `async def webcrawler(event_loop):`: `webcrawler`라는 이름의 비동기 준비물 함수를 정의합니다. `async`가 붙었으니 이 함수는 중간에 기다릴 수 있습니다. 파라미터로 `event_loop`를 받습니다. `pytest`는 똑똑해서, 이름이 같은 'event_loop' 픽스처(위에서 만든 세션 스코프 이벤트 루프)를 찾아서 자동으로 여기에 넣어줍니다.
- `"""..."""`: 이 준비물은 테스트 세션 동안 `AsyncWebCrawler` 인스턴스(실제 크롤러 객체)를 관리한다고 설명합니다.
- `print("\n>>> [Session] 웹크롤러/브라우저 시작")`: 테스트 실행 중 화면에 메시지를 보여줍니다. 이제 웹 크롤러와 내부 브라우저를 시작한다는 뜻입니다.
- `browser_conf = setup_browser_config()`: 위에서 가져온 함수를 호출해서 브라우저 설정값을 가져옵니다.
- `async with AsyncWebCrawler(config=browser_conf) as crawler:`: 이 부분이 핵심입니다!
  - `AsyncWebCrawler(config=browser_conf)`: 실제 웹 크롤러 객체를 만듭니다. 이때 브라우저 설정값을 넘겨줍니다.
  - `async with ... as crawler:`: `async with`는 비동기 자원(여기서는 웹 크롤러와 내부 브라우저)을 안전하게 사용하고 정리하는 특별한 방법입니다.
    - `async with`가 시작될 때: `AsyncWebCrawler` 객체가 내부적으로 `__aenter__` 메소드를 실행합니다. 이 과정에서 **실제 웹 브라우저(크롬 등)가 백그라운드에서 실행됩니다.**
    - `as crawler`: 성공적으로 시작된 웹 크롤러 객체를 `crawler`라는 이름으로 사용할 수 있게 됩니다.
- `print(">>> [Session] 웹크롤러/브라우저 시작 완료")`: 브라우저까지 성공적으로 시작되었다는 메시지를 보여줍니다.
- `yield crawler`: 위 `event_loop`의 `yield`와 같습니다. 여기서 멈추고, 준비된 `crawler` 객체를 테스트 함수들에게 빌려줍니다. 그리고 모든 테스트가 끝날 때까지 기다립니다. **모든 테스트는 이 동일한 `crawler` 객체를 사용하게 됩니다.**
- `print(">>> [Session] 웹크롤러/브라우저 종료 완료")`: 모든 테스트가 끝나고 `yield` 다음으로 돌아오면, `async with` 블록이 끝나는 시점입니다. 이때 `AsyncWebCrawler` 객체가 내부적으로 `__aexit__` 메소드를 실행하여 **백그라운드에서 실행되던 웹 브라우저를 닫고 관련 자원을 정리합니다.** 이 메시지는 그 정리가 완료되었다는 뜻입니다.

**왜 이렇게 할까요?** 웹 브라우저를 띄우고 닫는 것은 시간이 꽤 걸리는 작업입니다. 각 테스트마다 브라우저를 띄우고 닫으면 매우 비효율적이고, 이전 테스트의 브라우저가 완전히 닫히기 전에 다음 테스트가 새 브라우저를 띄우려다 충돌(우리가 겪었던 에러!)이 발생할 수 있습니다. 그래서 세션 전체에서 브라우저를 딱 한 번만 띄우고 모든 테스트가 공유해서 사용하는 것이 훨씬 안정적이고 빠릅니다.

**5. 테스트 실행하기 1: 여러 주식 사이트 크롤링**

```python
# --- 테스트 함수 (webcrawler 픽스처 사용) ---
@pytest.mark.asyncio  # 이 마크는 테스트 함수 자체의 실행 루프를 관리 (기본: 함수 스코프)
async def test_stock_data_crawling(webcrawler):  # 세션 스코프 webcrawler 주입
    """주식 데이터 크롤링 테스트"""
    print(f"\n>>> test_stock_data_crawling 실행 중 (크롤러 ID: {id(webcrawler)})")
    for url in stock_urls:
        md_generator = setup_markdown_generator()
        run_conf = setup_run_config(md_generator)
        result = await webcrawler.arun(url=url, run_config=run_conf)
        assert result is not None, f"{url} 크롤링 실패"
        assert result.markdown is not None, "마크다운 콘텐츠가 생성되지 않았습니다."
        file_name = url.split("/")[-2] if url.endswith("/") else url.split("/")[-1]
        save_text_to_unique_file(result.markdown, f"stock_data_{file_name}", "md", "test_results")
        if result.screenshot:
            save_png_to_unique_file(
                result.screenshot, f"stock_screenshot_{file_name}", "test_results"
            )

```

- `@pytest.mark.asyncio`: 이 함수가 `asyncio`를 사용하는 비동기 함수임을 `pytest`에게 알려줍니다. `pytest`는 이 함수를 실행하기 위한 이벤트 루프를 준비합니다 (기본적으로는 함수마다 새로 준비).
- `async def test_stock_data_crawling(webcrawler):`: `test_`로 시작하는 비동기 함수는 `pytest`가 테스트 대상으로 인식합니다. 파라미터로 `webcrawler`를 받습니다. `pytest`는 위에서 만든 **세션 스코프 `webcrawler` 준비물**을 찾아서 여기에 자동으로 전달해 줍니다.
- `"""..."""`: 이 테스트가 무엇을 하는지 설명합니다 (주식 데이터 크롤링).
- `print(...)`: 어떤 테스트가 실행 중인지, 그리고 사용 중인 `webcrawler` 객체의 고유 번호(ID)를 출력합니다. 이 ID를 보면 여러 테스트에서 같은 객체를 사용하는지 알 수 있습니다.
- `for url in stock_urls:`: 위에서 정의한 `stock_urls` 목록에 있는 각 웹사이트 주소(`url`)에 대해 다음 작업을 반복합니다.
- `md_generator = setup_markdown_generator()`: 마크다운 설정 함수를 호출합니다.
- `run_conf = setup_run_config(md_generator)`: 실행 설정 함수를 호출합니다.
- `result = await webcrawler.arun(url=url, run_config=run_conf)`: **실제 크롤링 작업**을 수행합니다!
  - `webcrawler.arun(...)`: 세션 스코프로 미리 준비된 `webcrawler` 객체에게 명령합니다. "이 `url`로 가서, 이 `run_config` 설정을 사용해서 정보를 가져와줘!"
  - `await`: 웹사이트 접속 및 정보 처리는 시간이 걸리므로, `await`를 써서 작업이 완료될 때까지 기다립니다. 그동안 이벤트 루프는 다른 일을 할 수도 있습니다.
  - `result`: 크롤링 결과가 `result` 변수에 저장됩니다. 여기에는 가져온 텍스트(마크다운 형식), 스크린샷 등이 들어있을 수 있습니다.
- `assert result is not None, ...`: `assert`는 검증 도구입니다. `result`가 비어있지 않은지(None이 아닌지) 확인합니다. 만약 비어있으면(크롤링 실패), 테스트는 실패하고 뒤의 메시지가 출력됩니다.
- `assert result.markdown is not None, ...`: `result` 안에 마크다운 텍스트가 들어있는지 확인합니다. 없으면 테스트 실패.
- `file_name = ...`: URL 주소에서 마지막 부분을 따와서 파일 이름을 만듭니다. (예: `sise`, `most-active`)
- `save_text_to_unique_file(...)`: 가져온 마크다운 텍스트(`result.markdown`)를 위에서 만든 파일 이름으로 `test_results` 폴더 안에 저장합니다.
- `if result.screenshot:`: 결과에 스크린샷이 포함되어 있는지 확인합니다.
- `save_png_to_unique_file(...)`: 스크린샷이 있다면, 그것도 파일로 저장합니다.

**6. 테스트 실행하기 2: 특정 주식 가격 형식 확인**

```python
@pytest.mark.asyncio  # 이 마크는 테스트 함수 자체의 실행 루프를 관리 (기본: 함수 스코프)
async def test_stock_price_format(webcrawler):  # 세션 스코프 webcrawler 주입
    """주식 가격 형식 테스트"""
    print(f"\n>>> test_stock_price_format 실행 중 (크롤러 ID: {id(webcrawler)})")
    url = "https://finance.naver.com/item/main.naver?code=005930"
    md_generator = setup_markdown_generator()
    run_conf = setup_run_config(md_generator)
    result = await webcrawler.arun(url=url, run_config=run_conf)
    assert result is not None, "주식 가격 크롤링 실패"
    assert result.markdown is not None, "마크다운 콘텐츠가 생성되지 않았습니다."
    import re

    price_pattern = r"[\d,]+"
    assert re.search(
        price_pattern, result.markdown
    ), "콘텐츠에서 유효한 가격 형식을 찾을 수 없습니다."
```

- 이 테스트 함수도 `@pytest.mark.asyncio`와 `async def`를 사용하고, 파라미터로 **동일한 세션 스코프 `webcrawler`**를 받습니다. (ID를 보면 첫 번째 테스트와 같은 객체임을 알 수 있습니다.)
- `"""..."""`: 이 테스트는 주식 가격 형식을 확인한다고 설명합니다.
- `print(...)`: 실행 중인 테스트 이름과 크롤러 ID를 출력합니다.
- `url = "..."`: 이번에는 테스트할 URL을 딱 하나(삼성전자 네이버 금융 페이지)로 지정합니다.
- `md_generator = ...`, `run_conf = ...`, `result = await webcrawler.arun(...)`: 이전 테스트와 동일하게 설정을 준비하고, **이미 실행 중인 브라우저를 사용하는 `webcrawler`**에게 해당 URL 크롤링을 시킵니다.
- `assert ...`: 크롤링 결과가 비어있지 않은지, 마크다운 텍스트가 있는지 확인합니다.
- `import re`: `re`라는 도구 상자를 가져옵니다. 이 도구는 텍스트 안에서 특정 '패턴'을 찾는 데 사용됩니다 (정규 표현식).
- `price_pattern = r"[\d,]+"`: 찾고 싶은 패턴을 정의합니다. `r""`는 특별한 의미의 문자를 그대로 쓰겠다는 표시입니다. `\d`는 숫자(0-9)를 의미하고, `,`는 쉼표를 의미합니다. `[...]`는 그 안의 문자 중 하나를 의미하고, `+`는 '하나 이상 반복'을 의미합니다. 즉, 이 패턴은 "숫자나 쉼표가 하나 이상 연속으로 나오는 부분" (예: "84,500")을 의미합니다.
- `assert re.search(price_pattern, result.markdown), ...`: `re.search` 함수를 사용해서, 크롤링 결과 텍스트(`result.markdown`) 안에 위에서 정의한 `price_pattern`과 일치하는 부분이 있는지 찾습니다. `assert`는 그런 부분이 **적어도 하나는 있어야 한다**고 검증합니다. 만약 숫자와 쉼표로 된 가격 형식이 전혀 없으면 테스트는 실패합니다.

**요약:**

이 코드는 `pytest`를 사용하여 웹 크롤링 기능을 테스트합니다. 가장 중요한 점은 `@pytest_asyncio.fixture(scope="session")`을 사용하여 웹 브라우저를 포함하는 `webcrawler` 객체를 **테스트 세션 전체에서 딱 한 번만 만들고 공유**한다는 것입니다. 이를 위해 세션 스코프 `event_loop`도 함께 정의했습니다. 각 테스트 함수는 `@pytest.mark.asyncio`로 비동기 실행을 지정하고, 파라미터로 세션 스코프 `webcrawler`를 받아 사용합니다. 이를 통해 각 테스트마다 브라우저를 띄우고 닫는 비효율과 충돌 문제를 해결하고 안정적으로 테스트를 수행할 수 있습니다.
