## 프로젝트 생성 ##

아래와 같이 `hello` 디렉토리를 생성한 후 uv 로 프로젝트를 생성하고 langgraph 를 설치한다.
uv는 패키지 및 프로젝트 관리도구로, 기본적으로 패키지를 관리할 때 프로젝트 단위로 관리한다. (파이썬 버전 관리 + 프로젝트 및 패키지 관리 + 가상환경 관리) 
```
mkdir hello
uv init
uv add langgraph
```

생성된 프로젝트 파일 정보를 확인한다.
```
ls -la 
```
[결과]
```
drwxr-xr-x@ 8 automake  staff     256  5월 22 23:01 .
drwxr-xr-x@ 6 automake  staff     192  5월 22 23:00 ..
-rw-r--r--@ 1 automake  staff       5  5월 22 23:01 .python-version
drwxr-xr-x@ 8 automake  staff     256  5월 22 23:01 .venv
-rw-r--r--@ 1 automake  staff      83  5월 22 23:01 main.py
-rw-r--r--@ 1 automake  staff     176  5월 22 23:01 pyproject.toml
-rw-r--r--@ 1 automake  staff       0  5월 22 23:01 README.md
-rw-r--r--@ 1 automake  staff  136035  5월 22 23:01 uv.lock
```

파이썬 프로젝트 설정 파일을 확인한다.
```
cat pyproject.toml
```
[결과]
```
[project]
name = "hello"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "langgraph>=1.2.1",
]
```

## 그래프 작성 ##
```
from langgraph.graph import StateGraph, MessagesState, START, END

def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()

result = graph.invoke(
    { "message": [ 
        {"role": "user", "content": "hi there"}
    ]}
)

import pprint
pprint.pprint(result)
```


## 프로젝트 실행 ##
```
uv run main.py
```
[결과]
```
{'messages': [AIMessage(content='hello world', additional_kwargs={}, response_metadata={}, id='dfd3d9ab-c850-4fee-ad50-b7735df289e1', tool_calls=[], invalid_tool_calls=[])]}
```


## 레퍼런스 ##

* https://docs.langchain.com/oss/python/langgraph/overview
