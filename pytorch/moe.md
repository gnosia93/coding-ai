## Moe ##
•	구조적 본질: 바닐라 트랜스포머의 구조에서 문맥을 파악하는 **어텐션(Attention)은 공유(Dense)**하되, 지식을 인출하는 FFN(Feed-Forward Network)만 8개의 개별 신경망(Expert)으로 물리적으로 분리한 구조입니다.

•	토큰 단위 분산: 문장 단위가 아니라 단어 조각(토큰) 단위로 실시간으로 전문가가 바뀝니다.

•	통신량 폭발 (Top-k): 토큰 하나가 상위 N개(top_k=2)의 방으로 복사(Copy)되어 동시에 날아가므로, 일반 모델에 비해 한 번에 오가는 데이터의 체급(Hidden States 원형)이 무지막지하게 큽니다.

•	레이턴시(Latency) 병목: 모델이 너무 커서 여러 서버(Node)에 찢어 올리다 보니, InfiniBand(IB)나 EFA 네트워크 스택을 거치면서 발생하는 지연 시간(Latency)이 GPU를 놀게 만드는 주범이 됩니다.

•	해법 (Overlap): 이 레이턴시를 숨기기 위해, 개발자가 코드로 현재 레이어 연산 중에 다음 레이어 통신을 백그라운드에서 미리 돌리는 '통신-연산 오버랩'을 명시적으로 제어해야 합니다.

💻 2. 코드 레벨 최종 요약 (PyTorch 실전 아키텍처)
```
import torch
import torch.nn as nn
import torch.distributed as dist

class ExpertLayer(nn.Module):
    """물리적으로 분리된 개별 전문가 신경망 (FFN)"""
    def __init__(self, d_model):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.ReLU(),
            nn.Linear(d_model * 4, d_model)
        )
    def forward(self, x):
        return self.net(x)

class OverlappedMoELayer(nn.Module):
    """통신-연산 오버랩이 적용된 고성능 MoE 레이어"""
    def __init__(self, d_model, num_experts=8, top_k=2):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        
        # 1. 전공 광장 (모든 토큰이 공동 사용)
        self.attention = SharedAttention(d_model)
        self.router = nn.Linear(d_model, num_experts)
        
        # 2. 8개의 완전히 독립된 별개의 신경망을 메모리 상에 물리적으로 생성
        self.experts = nn.ModuleList([ExpertLayer(d_model) for _ in range(num_experts)])
        
        # 💡 [명시적 최적화 1] 통신 전용 백그라운드 CUDA 스트림 개설
        self.comm_stream = torch.cuda.Stream()

    def forward(self, x):
        # [Step 1] 문맥 파악은 다 같이 (Dense 연산)
        context_x = self.attention(x)
        
        # [Step 2] 라우터가 토큰별 전공 방 점수 계산
        logits = self.router(context_x)
        topk_logits, topk_indices = torch.topk(logits, self.top_k, dim=-1)
        
        # ------------------------------------------------------------------
        # 🔥 엔지니어가 하드웨어 통신과 연산의 타이밍을 명시적으로 찢는 구간
        # ------------------------------------------------------------------
        
        # [Step 3] [명시적 최적화 2] 통신 전용 비동기 스트림 영역으로 진입
        with torch.cuda.stream(self.comm_stream):
            # 흩어진 GPU들끼리 토큰 원형 데이터(Hidden States)를 묶어서 교환합니다.
            # async_op=True를 주어, 통신을 백그라운드로 던지고 메인 코드는 0.0001초 만에 탈출합니다.
            async_handle = dist.all_to_all(
                output_tensor_list=self.prepared_expert_inputs,
                input_tensor_list=context_x,
                async_op=True
            )
            
        # [Step 4] 🚀 [통신-연산 오버랩]
        # InfiniBand 고속도로 위에서 토큰 복사본들이 치열하게 순간이동(통신)하는 동안,
        # GPU 연산 장치(Tensor Core)는 멈추지 않고 현재 레이어의 독립적인 연산을 동시에 수행합니다.
        self.execute_independent_local_computations()
        
        # [Step 5] [명시적 최적화 3] FFN 진입 직전 가드레일 설치
        # 옆 서버 GPU 메모리에 토큰들이 완전히 도착할 때까지 명시적으로 기다립니다.
        # 이 한 줄이 없으면 데이터 오염(Race Condition)이 발생합니다.
        async_handle.wait()
        
        # [Step 6] 각자 자기 전공 방(FFN)으로 흩어져서 최종 정답 계산 (Sparse 연산)
        # top_k=2 이므로 토큰별로 2개의 전문가 방 결과값을 가중치와 함께 합산합니다.
        expert_outputs = self.combine_expert_outputs(self.experts, topk_indices, topk_logits)
        
        return expert_outputs
```

### 3. 데이터 흐름 한눈에 보기 ###
	1.	입력 ➡️ [사과] [소스] [코드] [짜줘] 단어 진입.
	
  2.	공유 Attention ➡️ [소스] 단어가 뒤 단어들을 보고 "아, 나 프로그래밍 소스구나!" 하고 문맥 파악.
	
  3.	Router ➡️ [소스] 토큰 복사 후 3번(코딩 방), 5번(컴퓨터 구조 방)으로 목적지 판정 (top_k=2).
	
  4.	비동기 통신 ➡️ 파이토치 async_op=True 가동, InfiniBand/EFA를 통해 대용량 토큰 뭉치가 해당 GPU로 순간이동. (그동안 GPU는 딴 연산 하면서 레이턴시 은닉).
	
  5.	분산 FFN 연산 ➡️ 목적지 GPU의 독자적인 3번, 5번 전공 방에서 타 GPU 간섭 없이 풀 악셀 연산.
	
  6.	출력 ➡️ 결과 합산 후 최종 답변 표출.

