## 1. vscode 환경 설정 ##
* https://github.com/gnosia93/coding-ai/blob/main/langgraph/vscode.md


## 2. Bedrock 환경 설정 ##

### 모델 리스트 조회 ###
```
aws bedrock list-foundation-models \
  --query "modelSummaries[*].[modelId, modelName, responseStreamingSupported]" \
  --output table
```
[결과]
```
-----------------------------------------------------------------------------------------
|                                 ListFoundationModels                                  |
+-----------------------------------------------+---------------------------------------+
|  google.gemma-3-4b-it                         |  Gemma 3 4B IT                        |
|  nvidia.nemotron-nano-12b-v2                  |  NVIDIA Nemotron Nano 12B v2 VL BF16  |
|  anthropic.claude-sonnet-4-20250514-v1:0      |  Claude Sonnet 4                      |
|  anthropic.claude-opus-4-7                    |  Claude Opus 4.7                      |
|  anthropic.claude-haiku-4-5-20251001-v1:0     |  Claude Haiku 4.5                     |
|  qwen.qwen3-235b-a22b-2507-v1:0               |  Qwen3 235B A22B 2507                 |
|  openai.gpt-oss-safeguard-120b                |  GPT OSS Safeguard 120B               |
|  google.gemma-3-27b-it                        |  Gemma 3 27B PT                       |
|  moonshotai.kimi-k2.5                         |  Kimi K2.5                            |
|  openai.gpt-oss-120b-1:0                      |  gpt-oss-120b                         |
|  anthropic.claude-sonnet-4-5-20250929-v1:0    |  Claude Sonnet 4.5                    |
|  qwen.qwen3-vl-235b-a22b                      |  Qwen3 VL 235B A22B                   |
|  qwen.qwen3-next-80b-a3b                      |  Qwen3 Next 80B A3B                   |
|  deepseek.v3.2                                |  DeepSeek V3.2                        |
```

다음 명령어를 이용하여 텍스트 모델만 조회할 수 있다. 
```
aws bedrock list-foundation-models \
  --by-output-modality TEXT \
  --query "modelSummaries[*].[modelId, modelName, responseStreamingSupported]" \
  --output table
```

프로필 ID 를 조회합니다.
```
aws bedrock list-inference-profiles \
  --region ${AWS_REGION} \
  --output table
```

엔트로픽 모델 리스트를 조회한다. 
```
export AWS_REGION=$(aws ec2 describe-availability-zones --query 'AvailabilityZones[0].RegionName' --output text)
echo ${AWS_REGION}

aws bedrock list-foundation-models \
  --region {AWS_REGION} \
  --by-provider anthropic \
  --query "modelSummaries[?modelLifecycle.status=='ACTIVE'].modelId" \
  --output table
```
[결과]
```
-----------------------------------------------
|            ListFoundationModels             |
+---------------------------------------------+
|  anthropic.claude-opus-4-7                  |
|  anthropic.claude-haiku-4-5-20251001-v1:0   |
|  anthropic.claude-sonnet-4-5-20250929-v1:0  |
|  anthropic.claude-sonnet-4-6                |
|  anthropic.claude-opus-4-5-20251101-v1:0    |
|  anthropic.claude-opus-4-6-v1               |
+---------------------------------------------+
```

소넷 4.6 모델을 호출한다. (global prefix 사용)
```
aws bedrock-runtime converse \
  --model-id global.anthropic.claude-sonnet-4-6 \
  --messages '[{"role": "user", "content": [{"text": "안녕? 반가워. 너는 누구니?"}]}]' \
  --region {AWS_REGION}
```
[결과]
```
{
    "output": {
        "message": {
            "role": "assistant",
            "content": [
                {
                    "text": "안녕하세요! 반가워요 😊\n\n저는 **Claude**예요. Anthropic이 만든 AI 어시스턴트입니다.\n\n질문에 답하거나, 대화를 나누거나, 글쓰기, 분석, 번역 등 다양한 방면에서 도움을 드릴 수 있어요.\n\n무엇을 도와드릴까요? 🙂"
                }
            ]
        }
    },
    "stopReason": "end_turn",
    "usage": {
        "inputTokens": 25,
        "outputTokens": 127,
        "totalTokens": 152
    },
    "metrics": {
        "latencyMs": 3019
    }
}
```

## 3. 프로젝트 생성 ##

아래와 같이 `hello` 디렉토리를 생성한 후 uv 로 프로젝트를 생성하고 langgraph 를 설치한다.
uv는 패키지 및 프로젝트 관리도구로, 기본적으로 패키지를 관리할 때 프로젝트 단위로 관리한다. (파이썬 버전 관리 + 프로젝트 및 패키지 관리 + 가상환경 관리) 
```
mkdir hello
uv init
uv add langgraph langchain langchain-aws
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

## 4. hello 그래프 작성 ##
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


hello 그래프를 실행합니다.
```
uv run main.py
```
[결과]
```
{'messages': [AIMessage(content='hello world', additional_kwargs={}, response_metadata={}, id='dfd3d9ab-c850-4fee-ad50-b7735df289e1', tool_calls=[], invalid_tool_calls=[])]}
```

### 5. Tool Call ###

* https://github.com/gnosia93/coding-ai/blob/main/langgraph/src/tools.py
```
uv run tools.py
```
[결과]
```
<IPython.core.display.Image object>
================================ Human Message =================================

Add 3 and 4.
================================== Ai Message ==================================

[{'type': 'tool_use', 'name': 'add', 'input': {'a': 3, 'b': 4}, 'id': 'tooluse_y8wF0xEe8FqplUwg7tiuFG'}]
Tool Calls:
  add (tooluse_y8wF0xEe8FqplUwg7tiuFG)
 Call ID: tooluse_y8wF0xEe8FqplUwg7tiuFG
  Args:
    a: 3
    b: 4
================================= Tool Message =================================

7
================================== Ai Message ==================================

The sum of 3 and 4 is **7**.
automake@mini hello % uv run tools.py
<IPython.core.display.Image object>
================================ Human Message =================================

Add 3 and 4.
================================== Ai Message ==================================

[{'type': 'tool_use', 'name': 'add', 'input': {'a': 3, 'b': 4}, 'id': 'tooluse_dMSqm3YI2oY2D8DYdEpzoj'}]
Tool Calls:
  add (tooluse_dMSqm3YI2oY2D8DYdEpzoj)
 Call ID: tooluse_dMSqm3YI2oY2D8DYdEpzoj
  Args:
    a: 3
    b: 4
================================= Tool Message =================================

7
================================== Ai Message ==================================

The sum of 3 and 4 is **7**.
```




## 레퍼런스 ##

* https://docs.langchain.com/oss/python/langgraph/overview
