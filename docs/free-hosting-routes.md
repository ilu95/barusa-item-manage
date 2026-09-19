# GPU 없이 무료로 쓸 수 있는 경로 조사 (2026-09 기준)

앞 문서(`open-model-survey.md`)가 **"어떤 모델을 쓸 권리가 있나"**였다면,
이 문서는 **"GPU 없이 공짜로 어디서 돌리나"**입니다. 축이 다릅니다.

---

## 0. 먼저 — 헷갈리면 안 되는 두 축

무료 AI 도구를 고를 때 검사해야 할 게 두 개인데, 대부분 하나만 봅니다.

| | 무엇을 정하나 | 예 |
|---|---|---|
| **① 모델 가중치 라이선스** | 모델 파일을 **내가 직접 돌릴** 권리 | Apache 2.0, MIT, FLUX Non-Commercial |
| **② 서비스 이용약관** | 그 **서비스에서** 만든 결과물을 뭘 해도 되나 | NVIDIA 개발자 약관, Meta AI 약관 |

**핵심 원칙: 호스팅 API로 쓸 때 적용되는 건 ②입니다.**

그래서 이런 역전이 생깁니다.
- 가중치가 **비상업**인 모델도 → 제공자가 상용 라이선스를 사서 서비스하면 **쓸 수 있음**
  (예: Cloudflare가 서비스하는 FLUX.2 klein 9B)
- 가중치가 **Apache 2.0**인 모델도 → 서비스 약관이 "평가 전용"이면 **못 씀**
  (예: NVIDIA NIM으로 돌리는 Qwen-Image-Edit)

두 번째가 특히 함정입니다. 아래 NVIDIA 항목을 보세요.

---

## 1. 인스타에서 본 조합 (Meta AI + Vibes AI) — 우리 용도엔 못 씁니다

이유가 두 가지인데, 둘 다 치명적입니다.

**① 상업 이용 문제.** Meta AI로 생성한 영상은 상업적 사용이 승인돼 있지 않습니다.
또 Meta 약관은 생성물에 대해 Meta에 광범위한 권리를 부여합니다.
쇼핑몰 상품 콘텐츠는 명백한 상업적 사용입니다.

**② 애초에 기능이 안 맞습니다.** 이게 더 근본적입니다.
Meta AI는 **텍스트 프롬프트로 새 이미지를 만드는** 도구입니다.
우리가 필요한 건 **"이 사진 속 이 사람에게, 이 모자를 씌워라"** 라는 편집(image-to-image,
다중 레퍼런스)입니다. 텍스트만으로는 우리 실제 모자를 재현할 수 없습니다.
비슷하게 생긴 다른 모자가 나올 뿐이고, 그건 상품 이미지로 쓸 수 없습니다.

→ 그 조합은 "아무 홍보 영상이나 빠르게 뽑기"에는 유효하지만,
**실제 상품 착용샷에는 원천적으로 안 맞습니다.** 우리가 참고할 건 아닙니다.

---

## 2. 요청하신 서비스들 조사 결과

| 경로 | 무료 한도 | 상업 이용 | 이미지 편집 | 판정 |
|---|---|---|---|---|
| **Cloudflare Workers AI** | **10,000 뉴런/일**, 카드 불필요 | ⚠️ 약관 확인 | **FLUX.2 klein** (생성+편집) | 🟢 **1순위** |
| **ModelScope** | **2,000 호출/일** | ⚠️ 약관 확인 | **Qwen-Image-Edit 직접** | 🟡 가입 장벽 |
| NVIDIA build (NIM) | 무료, 한도 비공개 | ❌ **개발·테스트·평가 전용** | Qwen-Image-Edit 있음 | 🔴 테스트만 |
| OpenRouter | `:free`는 50 req/일 | 유료면 가능 | 가능 | 🔴 **무료 이미지 모델 없음** |
| Bytez | **$1 / 4주** | — | 가능 | 🔴 한도 과소 |
| Dreamina (CapCut) | 가입+정기 크레딧 | ⚠️ 출력물 권리 불명확 | 가능 | 🔴 약관 리스크 |
| HF Inference Providers | 월 $0.10 크레딧 | — | — | 🔴 한도 과소 |
| HF ZeroGPU Spaces | 하루 5분 H200 | — | Space 수동 조작 | 🟡 테스트용 |
| SiliconFlow | 가입 $1 내외 | 유료면 가능 | Qwen-Image-Edit **$0.04/장** | 🟡 저렴한 유료 |
| Together AI | FLUX.1 schnell 무료 엔드포인트 | | **schnell은 T2I 전용** | 🔴 편집 불가 |
| Google AI Studio | 이미지는 사실상 유료 키 필요 | ✅ 가능 (무료분은 학습 사용) | Nano Banana Pro | 🟡 $0.039~/장 |
| **로컬 GPU** | **무제한** | ✅ | 전부 | 🟢 최종 목적지 |

### 🔴 NVIDIA build.nvidia.com — 가장 큰 함정
Qwen-Image-Edit을 무료로 제공하고 모델 자체는 Apache 2.0이라 문제없어 보이지만,
**NVIDIA 개발자 프로그램을 통한 NIM 접근은 프로토타이핑·연구·개발·테스트 전용**입니다.
프로덕션 사용(= 실제 사업 거래, 실사용자 대상 활동)은 **NVIDIA AI Enterprise**
라이선스가 필요하고, 이는 GPU당 연 $4,500 수준입니다.

→ **모델 비교·테스트 용도로는 아주 좋습니다.** 카드 없이 Qwen-Image-Edit을
바로 찔러볼 수 있으니 1단계 PoC에 쓰세요. 다만 **여기서 뽑은 이미지를
쇼핑몰에 올리면 안 됩니다.**

### 🔴 OpenRouter — 이미지엔 무료가 없습니다
`:free` 접미사가 붙는 무료 모델은 **텍스트 모델뿐**입니다(하루 50회).
이미지 생성 모델(FLUX.2, Seedream, Nano Banana 등)은 **전부 장당 과금**입니다.
대본·카피 쓰는 데는 유용하지만 착용샷 생성 경로로는 해당 없습니다.

### 🔴 Bytez — 무료 티어가 축소됐습니다
현재 **$1 크레딧이 4주마다 갱신**되는 수준이고, 미사용분은 소멸합니다.
하루 200회 무료였던 Early Access 프로그램은 **2026년 3월 15일 종료**됐습니다.
모델 수(22만 개)는 많지만 우리 용도의 지속 운영에는 한도가 맞지 않습니다.

### 🔴 Dreamina (CapCut / ByteDance) — 무료지만 권리가 불명확
베타 기간 무료 크레딧에 워터마크 없는 다운로드가 되는 건 맞습니다. 다만:
- 제품 페이지에 **출력물 상업 라이선스·소유권 배분이 명시돼 있지 않고**,
  권리가 워크플로마다 다를 수 있다는 지적이 있습니다.
- Seedance 2.0은 안전 정책상 **실제 얼굴이 포함된 이미지의 영상화를 차단**합니다.
  우리 가상 모델이 사실적일수록 여기 걸릴 가능성이 있습니다.
- 약관 최종 개정 2026-01-22.

쇼핑몰 상품 이미지는 분쟁 시 손해가 큰 영역이라, **권리가 불명확한 서비스는 피하는 게 맞습니다.**

---

## 3. 🟢 Cloudflare Workers AI — 현시점 가장 현실적인 무료 경로

- **하루 10,000 뉴런 무료**, Workers 무료 플랜에서도 제공, **신용카드 불필요**
- UTC 00:00 리셋, 한도 초과 시 과금이 아니라 **정지**(예상 못 한 청구가 없음)
- 초과분 단가는 1,000 뉴런당 $0.011
- **FLUX.2 [klein]** 보유 — 생성과 편집이 한 모델에 통합, **다중 레퍼런스 편집 지원**

### 무료 한도로 하루 몇 장?
공개 단가로 역산한 **추정치**입니다 (1,000 뉴런 = $0.011 기준):

| 모델 | 장당 단가 | 환산 뉴런 | 하루 무료 생성량 |
|---|---|---|---|
| FLUX.1 schnell | 43 뉴런 (공식) | 43 | **약 230장** |
| FLUX.2 klein 4B | 1024² = 512 타일 4장 × $0.000287 ≈ $0.00115 | ≈104 | **약 95장** |
| FLUX.2 klein 9B | 첫 1MP $0.015 | ≈1,364 | **약 7장** |

**우리는 하루 3~30장이면 충분합니다.** klein 4B 기준 무료 한도의 1/3도 안 씁니다.

### 이게 왜 다른 선택지보다 나은가
**FLUX.2 klein 4B는 Apache 2.0입니다.** 즉 Cloudflare에서 무료로 쓰다가,
품질이 확인되면 **똑같은 모델을 우리 GPU에 내려받아 그대로 돌릴 수 있습니다.**
(8GB VRAM이면 됩니다.) 서비스 약관·한도·가격 변동에서 벗어날 퇴로가 있는 겁니다.

단, Cloudflare가 서비스하는 **klein 9B는 가중치 자체는 비상업**입니다.
API로 쓰는 동안은 Cloudflare 약관이 적용되지만, **로컬 이전은 불가**합니다.
→ 퇴로를 남기려면 **4B를 기준으로 파이프라인을 짜세요.**

---

## 4. 🟡 ModelScope — Qwen-Image-Edit을 직접 쓰는 경로

- **가입 계정당 하루 2,000회 무료 API 호출** (전 모델 공통 쿼터)
- Qwen-Image-Edit-2509 / 2511 모두 등재돼 있음 (알리바바 본진)
- 한도만 보면 우리 용도엔 차고 넘칩니다

**장벽:** 가입에 알리바바 계정 또는 중국 휴대폰 번호가 필요해 해외 사용자는
막히는 경우가 있습니다. 가입이 되면 가장 강력한 무료 경로입니다.

가입이 안 되면 대안은 **SiliconFlow의 Qwen-Image-Edit 장당 $0.04**입니다.
하루 30장이면 **월 약 5만 원** 수준으로, 무료는 아니지만 GPU 없이 즉시 시작할 수 있습니다.

---

## 5. 권장 전략 — 2단 구성

```
[1단계: 지금 · GPU 없이 · 무료]
   비교 테스트   NVIDIA build (Qwen-Image-Edit)   ← 테스트 전용, 결과물 게시 금지
                 HF ZeroGPU Space                  ← 손으로 몇 장 돌려보기
   실제 생성     Cloudflare Workers AI (FLUX.2 klein 4B)
                 또는 ModelScope (Qwen-Image-Edit)  ← 가입 되면

[2단계: 품질 확정 후 · 로컬 이전]
   같은 모델을 우리 장비로 (klein 4B = 8GB, Qwen-Image-Edit = 12~20GB)
   → 약관·한도·가격 변동에서 완전히 독립
```

### 관통하는 원칙 하나
> **지금 무료 서비스를 쓰더라도, "나중에 내 장비로 내릴 수 있는 모델"만 고르세요.**

Apache 2.0 모델(FLUX.2 klein 4B, Qwen-Image-Edit)을 서비스로 쓰다가 그대로
로컬로 내리는 게 유일하게 안전한 경로입니다.

Nano Banana나 Seedream에 파이프라인을 맞추면 성능은 좋겠지만, 가격이 오르거나
약관이 바뀌거나 서비스가 종료될 때 **처음부터 다시 만들어야 합니다.**
프롬프트도 마스크 규격도 전부 모델에 종속되기 때문입니다.
Bytez의 무료 200회/일이 2026년 3월에 사라진 게 바로 그 사례입니다.

---

## 6. 무료 서비스 공통 리스크 (이건 어느 서비스를 쓰든 남습니다)

1. **입출력이 모델 학습에 사용될 수 있음.** Google은 무료 티어 입출력을 모델 개선에
   사용한다고 명시합니다. **출시 전 신상품 사진을 올리는 건 위험합니다.**
   기획 중인 신상 디자인이 외부 모델 학습에 들어갑니다.
2. **한도·약관 수시 변경.** Bytez 무료 티어 종료(2026-03-15)가 실제 사례입니다.
3. **워터마크.** Google 이미지는 비가시 SynthID가 항상 들어갑니다(상업 사용은 무방).
4. **서비스 종료 리스크.** 파이프라인이 특정 서비스에 묶여 있으면 그대로 멈춥니다.

이 4가지 때문에 **최종 목적지는 로컬**이어야 합니다.
하루 30장 규모면 RTX 4090급 1장으로 충분하고, 앞서 계산한 대로
클라우드 대비 6개월이면 회수됩니다.

---

## 7. 결론

요청하신 5개 중 **실제로 쓸 수 있는 건 사실상 없거나 제한적**입니다.
- Bytez → 한도 과소
- NVIDIA NIM → **개발·테스트 전용, 상업 사용 불가**
- OpenRouter → **무료 이미지 모델 자체가 없음**
- Dreamina → 출력물 권리 불명확
- NVIDIA의 Qwen-Image → 모델은 좋지만 NIM 약관에 막힘

대신 조사 과정에서 **더 나은 걸 찾았습니다.**

> **Cloudflare Workers AI의 FLUX.2 klein 4B**
> 하루 약 95장 무료, 카드 불필요, 초과 시 과금 아닌 정지,
> 생성+다중 레퍼런스 편집 통합, **Apache 2.0이라 로컬 이전 가능**

우리 요구(하루 3~30장, 상업 사용, 인물+모자 편집, 퇴로 확보)를 전부 만족하는
유일한 무료 경로입니다.

---

## 참고 링크

- Cloudflare Workers AI 모델: https://developers.cloudflare.com/workers-ai/models/
- Cloudflare Workers AI 가격: https://developers.cloudflare.com/workers-ai/platform/pricing/
- Cloudflare 파트너 모델 발표: https://blog.cloudflare.com/workers-ai-partner-models/
- NVIDIA NIM 개발자 안내: https://developer.nvidia.com/nim
- NVIDIA NIM FAQ(프로덕션 정의): https://docs.api.nvidia.com/nim/docs/product
- NVIDIA AI 제품 약관: https://www.nvidia.com/en-us/agreements/enterprise-software/product-specific-terms-for-ai-products/
- OpenRouter 이미지 모델: https://openrouter.ai/collections/image-models
- Bytez 문서: https://github.com/Bytez-com/docs
- ModelScope Qwen-Image-Edit-2511: https://modelscope.ai/models/Qwen/Qwen-Image-Edit-2511
- SiliconFlow Qwen-Image-Edit: https://www.siliconflow.com/models/qwen-image-edit
- Dreamina 이용약관: https://dreamina.capcut.com/clause/dreamina-terms-of-service
- Meta AI 이미지·영상 생성 안내: https://www.meta.com/help/artificial-intelligence/1337455336906126/
- Meta AI 약관: https://www.facebook.com/legal/ai-terms
- HF ZeroGPU: https://huggingface.co/docs/hub/en/spaces-zerogpu
