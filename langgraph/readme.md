## 프로젝트 생성 ##

uv는 기본적으로 패키지를 관리할 때 프로젝트 단위로 관리하므로, 아래와 같이 `hello` 디렉토리를 생성한 후 uv 로 프로젝트를 생성하고 langgraph 를 설치한다.
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


## 프로젝트 실행 ##
```
uv run main.py
```



## 레퍼런스 ##

* https://docs.langchain.com/oss/python/langgraph/overview
