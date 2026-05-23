### 1. ToolCall 객체의 표준 타입 스펙 (파이썬) ###

langchain_core.messages.tool 모듈에 정의된 ToolCall 구조는 다음과 같습니다. 딱 4가지 필드로만 구성된 매우 심플한 명세서입니다.
```
from typing import TypedDict, Any, Dict, Optional

class ToolCall(TypedDict):
    name: str               # 1. 실행할 도구(함수)의 이름
    args: Dict[str, Any]    # 2. 함수에 넘겨줄 인자(파라미터) 딕셔너리
    id: Optional[str]       # 3. LLM이 발급한 고유 요청 ID (비동기/병렬 매칭용)
    type: str               # 4. 객체의 타입 정보 (항상 "tool_call" 고정)
```

### 2. 필드별 상세 명세 및 예시 ###
이해를 돕기 위해 LLM이 날씨 정보를 물어봤을 때 생성하는 실제 ToolCall 데이터 스펙을 기준으로 뜯어보겠습니다.

```
{
    "name": "get_weather",
    "args": {
        "location": "Seoul",
        "unit": "celsius"
    },
    "id": "call_abc12345xyz",
    "type": "tool_call"
}
```

① name (타입: str)
•	설명: LLM이 호출하기로 결정한 파이썬 함수의 이름입니다.
•	스펙: 개발자가 @tool 데코레이터 등으로 정의해서 모델에게 넘겨준 함수명과 정확히 일치하는 문자열이 들어옵니다.

② args (타입: Dict[str, Any])
•	설명: 함수를 실행할 때 인자값으로 넣어줄 데이터 뭉치입니다.
•	스펙: 항상 파이썬 딕셔너리 형태로 들어옵니다. 값이 숫자인지, 문자열인지, 리스트인지는 개발자가 도구를 선언할 때 지정한 타입 힌트(Type Hint) 스펙을 LLM이 파싱해서 맞춰 채워줍니다.

③ id (타입: str 또는 None)
•	설명: 이 특정 도구 호출 건에 대해 LLM이 부여한 고유 식별자입니다.
•	스펙: 영문과 숫자가 섞인 무작위 문자열입니다. 매우 드물게 도구 호출을 지원하지 않는 옛날 모델의 경우 None이 올 수도 있지만, 클로드 소넷/하이쿠 등 최신 모델은 무조건 고유 문자열 값을 채워줍니다.

④ type (타입: str)
•	설명: 이 데이터 구조의 종류를 명시하는 메타데이터입니다.
•	스펙: 값은 언제나 리터럴 문자열인 "tool_call"로 고정되어 있습니다.
