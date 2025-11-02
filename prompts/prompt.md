uv run cli.py crawl https://developers.figma.com/docs/figma-mcp-server \
 --prefix https://developers.figma.com/docs/figma-mcp-server
결과: @developer

1. 제대로 크롤링을 해왔는지 chrome dev mcp로 확인(네브바를 확인)
2. 루트 폴더 이름이 `developers`가 아니라 `developers_figma_com` 이였으면 좋겠어

1. 폴더명은 잘 변했어
2. 제대로 크롤링을 해왔는지 chrome dev mcp로 확인하라는 것은 빠짐없이 잘 가져왔냐고 질문한거야
   지금은 페이지를 5개 밖에 안가져오네? 원래대로 돌려줘 nav 태그를 제거하면 다음 페이지로 넘어가기 위한 링크들도 제거되니까
