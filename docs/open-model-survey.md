# 오픈소스 이미지·영상 생성 모델 조사 (2026-09 기준)

목적: 모자 착용샷 생성에 **무료로, 상업적으로** 쓸 수 있는 모델 확정.

## 검증 방법

시중 블로그·SEO 사이트의 라이선스 표기가 **상당수 틀렸습니다.** 그래서 이 문서의 라이선스는
전부 GitHub 공식 저장소의 LICENSE 원문을 직접 받아 확인했습니다.
(huggingface.co는 이 작업 환경의 egress 정책으로 차단돼 GitHub raw를 사용했습니다.)

표기 규칙: ✅ 상업 이용 자유 / ⚠️ 조건부 / ❌ 불가

---

## 0. 먼저 — 한국에서 **쓸 수 없는** 모델군

**Tencent Hunyuan 전 제품군.** 라이선스 첫 줄에 이렇게 박혀 있습니다.

> THIS LICENSE AGREEMENT DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM
> AND **SOUTH KOREA** AND IS EXPRESSLY LIMITED TO THE TERRITORY, AS DEFINED BELOW.
>
> 1.l "Territory" shall mean the worldwide territory, **excluding** the territory of
> the European Union, United Kingdom and **South Korea**.

즉 한국 사업자에게는 **라이선스 자체가 부여되지 않습니다.** 5조 c항은 Territory 밖에서
모델뿐 아니라 **생성 결과물(Output)의 사용·배포까지 금지**합니다.

원문 확인 완료 (3개 저장소 모두 동일 문구):
- `Tencent-Hunyuan/HunyuanVideo/LICENSE.txt`
- `Tencent-Hunyuan/HunyuanVideo-I2V/LICENSE.txt`
- `Tencent-Hunyuan/HunyuanVideo-1.5/LICENSE`
- `Tencent-Hunyuan/HunyuanImage-3.0/LICENSE`

→ **HunyuanVideo, HunyuanVideo 1.5, HunyuanImage 3.0 전부 후보에서 제외.** ❌
국내 블로그들이 "무료 오픈소스"로 자주 소개하는 모델이라 특히 주의가 필요합니다.

---

## 1. 이미지 생성 (Text-to-Image)

| 모델 | 크기 | 라이선스 | 상업 | 비고 |
|---|---|---|---|---|
| **Qwen-Image / Qwen-Image-2512** | 20B | Apache 2.0 | ✅ | 알리바바. 2025-08-04 최초, **2512는 2025-12-31** |
| **Z-Image / Z-Image-Turbo** | 6B | Apache 2.0 | ✅ | 알리바바 Tongyi-MAI, 2025-11-26 |
| **FLUX.2 [klein] 4B** | 4B | Apache 2.0 | ✅ | BFL, 2026-01-15. **생성+편집 겸용** |
| **FLUX.2 [klein] 4B Base** | 4B | Apache 2.0 | ✅ | 파인튜닝·LoRA 학습용 |
| **FLUX.1 [schnell]** | 12B | Apache 2.0 | ✅ | 구형이지만 자유 |
| **HiDream-I1** | 17B | MIT | ✅ | |
| Stable Diffusion 3.5 | 8B | Stability Community | ⚠️ | 연매출 $1M 미만 무료 |
| FLUX.2 [dev] | 32B | FLUX Non-Commercial | ❌ | 유료 계약 필요 |
| FLUX.2 [klein] 9B / 9B KV / 9B Base | 9B | FLUX Non-Commercial | ❌ | **4B만 Apache입니다** |
| FLUX.1 [dev] | 12B | Non-Commercial v1.1.1 | ❌ | |
| HunyuanImage 3.0 | 80B | Tencent Community | ❌ | **한국 제외** |

### 주목할 두 모델

**Z-Image-Turbo (6B, Apache 2.0)** — 공식 README 기준:
- 8 NFE로 **H800에서 1초 미만**, 소비자 GPU **16GB에 들어감**
- stable-diffusion.cpp 사용 시 **VRAM 4GB에서도 구동**
- 2025-12-08 Artificial Analysis T2I 리더보드 **종합 8위, 오픈소스 1위**
- Z-Image-Edit / Z-Image-Omni-Base는 README에 아직 **"To be released"** (미출시)

**FLUX.2 [klein] 4B (Apache 2.0)** — 공식 README 라이선스 표 기준:
- 텍스트→이미지 + **단일/다중 레퍼런스 이미지 편집** 모두 지원
- **~8GB VRAM** (RTX 3090/4070 이상), 1초 미만 생성
- klein 제품군 중 **4B와 4B Base만 Apache 2.0**, 9B 계열은 전부 비상업

---

## 2. 이미지 편집 (Instruction-based Edit) — **우리가 실제로 쓸 영역**

| 모델 | 크기 | 라이선스 | 상업 | 출시 |
|---|---|---|---|---|
| **Qwen-Image-Edit-2511** | 20B | Apache 2.0 | ✅ | 2025-12-23 |
| **Qwen-Image-Edit-2509** | 20B | Apache 2.0 | ✅ | 2025-09-22 |
| **Qwen-Image-Layered** | 20B | Apache 2.0 | ✅ | 2025-12-19 |
| **FLUX.2 [klein] 4B** | 4B | Apache 2.0 | ✅ | 2026-01-15 |
| **Step1X-Edit** | 19B | Apache 2.0 | ✅ | StepFun |
| **OmniGen2** | 7B | Apache 2.0 | ✅ | VectorSpaceLab |
| **FireRed-Image-Edit** | — | Apache 2.0 | ✅ | 샤오홍슈 |
| **JoyAI-Image** | — | Apache 2.0 | ✅ | JD |
| Z-Image-Edit | 6B | (Apache 예정) | — | **미출시** |
| FLUX.1 Kontext [dev] | 12B | Non-Commercial | ❌ | |
| **FLUX.1 Fill / Depth / Canny / Redux [dev]** | 12B | Non-Commercial | ❌ | ⚠️ 아래 참조 |

### ⚠️ FLUX.1 Fill 함정
인페인팅에 널리 쓰이는 **FLUX.1 Fill [dev]**가 FLUX.1 [dev] 비상업 라이선스에
**명시적으로 포함**돼 있습니다. 원문:

> The "FLUX.1 [dev] Model" means the FLUX.1 [dev] AI models ... including but not
> limited to FLUX.1 [dev], **FLUX.1 Fill [dev]**, FLUX.1 Depth [dev],
> FLUX.1 Canny [dev], FLUX.1 Redux [dev] ...

ComfyUI 인페인팅 튜토리얼 대다수가 Flux Fill을 씁니다. 그대로 따라 하면 **비상업 모델로
상업 이미지를 만드는 상태**가 됩니다. 우리 파이프라인에는 넣지 않습니다.

### 각 후보의 성격
- **Qwen-Image-Edit-2511** — 2511의 공식 개선 포인트가 **캐릭터 일관성 강화**와
  **커뮤니티 LoRA 내장**입니다. 2509는 "person + product" 다중 이미지 편집과
  ControlNet(keypoint/sketch) 네이티브 지원을 추가했습니다. 둘 다 우리 용도와 정확히 맞습니다.
- **FLUX.2 klein 4B** — 20B 대비 1/5 크기에 다중 레퍼런스 편집이 되고 8GB에 들어갑니다.
  하루 수십 장 규모라면 품질 차이보다 **속도·VRAM 이점이 더 클 수 있습니다.**
- 나머지(Step1X-Edit, OmniGen2, FireRed, JoyAI)는 결과가 안 나올 때 돌려볼 예비 카드.

---

## 3. 영상 생성

| 모델 | 라이선스 | 상업 | 상태 |
|---|---|---|---|
| **Wan 2.2** | Apache 2.0 | ✅ | **2025-07-28. 알리바바 마지막 오픈웨이트 영상 모델** |
| **Wan 2.1** | Apache 2.0 | ✅ | |
| **LTX-2 / LTX-2.5** | LTX Community License | ⚠️→✅ | **연매출 $10M 미만 무료** (우리는 해당) |
| **Mochi 1** | Apache 2.0 | ✅ | Genmo |
| **Open-Sora** | Apache 2.0 | ✅ | HPC-AI |
| CogVideoX | 코드 Apache 2.0 | ⚠️ | 가중치는 별도 라이선스, 사용 전 확인 필요 |
| HunyuanVideo / 1.5 / I2V | Tencent Community | ❌ | **한국 제외** |
| Wan 2.5 / 2.6 / 2.7 / 3.0 | — | ❌ | **오픈웨이트 아님. 아래 참조** |

### ❗ "Wan 2.5 / 2.7 / 3.0 오픈소스" 는 사실이 아닙니다

여러 블로그가 "Wan 2.5는 Apache 2.0 오픈소스", "Wan 2.7이 2026년 최고의 오픈소스 모델"
이라고 쓰고 있습니다. 직접 확인한 결과:

```
200  Wan-Video/Wan2.1/main/README.md
200  Wan-Video/Wan2.2/main/README.md
404  Wan-Video/Wan2.5/main/README.md
404  Wan-Video/Wan2.6/main/README.md
404  Wan-Video/Wan2.7/main/README.md
404  Wan-Video/Wan3.0/main/README.md
```

**Wan-Video 공식 조직에 2.5 이후 저장소가 존재하지 않습니다.** 2.5는 2025년 9월
Apsara 컨퍼런스에서 프리뷰된 뒤 Alibaba Cloud Bailian API로만 제공됐고, 가중치는
HuggingFace·GitHub·ModelScope 어디에도 공개된 적이 없습니다. 이후 2.6, 2.7, 3.0도 동일합니다.

→ **오픈웨이트 Wan은 2.2가 마지막입니다.**

### LTX-2.x 라이선스 (원문 확인)
`Lightricks/LTX-2/LICENSE-2_x`, 2026-08-11자. 연매출 **$10,000,000 이상**인 법인은
별도 Commercial Use Agreement가 필요하고, 그 미만은 무료입니다. 모자 쇼핑몰은 여유 있게 해당됩니다.
LTX-2.5는 4K·오디오 동기 생성을 지원하고 텍스트 인코더로 Gemma 4 12B 파인튜닝판을 내장합니다.

---

## 4. 보조 모델 (파이프라인 필수 부품)

| 용도 | 모델 | 라이선스 | 상업 |
|---|---|---|---|
| 배경 제거 | **BiRefNet** | MIT | ✅ |
| 배경 제거 (래퍼) | **rembg** | MIT | ✅ |
| 업스케일 | **Real-ESRGAN** | BSD 3-Clause | ✅ |
| 세그멘테이션 | **SAM 2** | Apache 2.0 | ✅ |
| 워크플로우 엔진 | **ComfyUI** | **GPL-3.0** | ⚠️ 아래 |

- **RMBG-2.0**(BRIA)은 배경제거 성능이 좋지만 **비상업 라이선스**입니다. BiRefNet으로 대체하세요.
  (BiRefNet이 RMBG-2.0의 기반 아키텍처이고 MIT입니다.)
- **ComfyUI는 GPL-3.0**입니다. 사내에서 돌려 이미지를 뽑는 용도는 아무 문제 없습니다.
  GPL 의무는 *소프트웨어를 배포할 때* 발생하며, 생성된 이미지에는 미치지 않습니다.
  ComfyUI를 포함한 제품을 고객에게 배포할 계획이 생기면 그때 다시 검토하면 됩니다.

---

## 5. 결론 — 우리가 쓸 조합

전부 Apache 2.0 / MIT / BSD 이고 **로열티·매출 제한이 전혀 없습니다.**

```
배경 제거   BiRefNet (MIT)
마스크      SAM 2 (Apache 2.0)          ← 베이스컷당 1회, 수동 보정으로 갈음 가능
착용 합성   Qwen-Image-Edit-2511 (Apache 2.0)   ← 주력
            FLUX.2 klein 4B (Apache 2.0)        ← 경량·고속 대안, 8GB
업스케일    Real-ESRGAN (BSD 3-Clause)
엔진        ComfyUI (GPL-3.0, 사내 사용 무관)

(나중에 영상) Wan 2.2 I2V (Apache 2.0) 또는 LTX-2.5 ($10M 미만 무료)
```

### 1단계에서 비교할 것
**Qwen-Image-Edit-2511 vs FLUX.2 klein 4B** 를 같은 모자·같은 베이스컷으로 돌려
비교해야 합니다. 스펙상 트레이드오프가 명확합니다.

| | Qwen-Image-Edit-2511 | FLUX.2 klein 4B |
|---|---|---|
| 크기 | 20B | 4B |
| VRAM | FP8 ~20GB / GGUF ~12GB / 오프로딩 4GB | ~8GB |
| 속도 | H100 편집당 ~45초 | 1초 미만 |
| 강점 | 인물 일관성, ControlNet, 커뮤니티 LoRA 내장 | 속도, 저사양, 다중 레퍼런스 |

하루 30장 규모에서 klein 4B로 충분한 품질이 나오면 **GPU 요구사항이 절반 이하**로 떨어져
로컬 장비 구성이 훨씬 쉬워집니다. 이건 실제로 돌려봐야 아는 부분입니다.

---

## 6. 라이선스 관련 마지막 주의

모델 가중치 라이선스가 자유롭다는 것은 **모델을 쓸 권리**에 대한 것입니다. 별개로 남는 것:

1. **생성물의 상표·저작권** — 다른 브랜드 로고나 실존 인물을 닮은 얼굴이 나오면 그건 별도 문제입니다.
2. **AI 기본법 표시 의무** — 모델 라이선스와 무관하게 국내법상 표시가 필요합니다.
3. **학습 데이터 출처** — 대부분의 오픈 모델이 학습 데이터를 공개하지 않습니다.
   LTX-2가 "라이선스된 학습 데이터"를 명시하는 드문 사례입니다.

---

## 참고 링크

**공식 저장소 (라이선스 원문 확인처)**
- Qwen-Image: https://github.com/QwenLM/Qwen-Image
- Z-Image: https://github.com/Tongyi-MAI/Z-Image
- FLUX.2: https://github.com/black-forest-labs/flux2
- FLUX.1: https://github.com/black-forest-labs/flux
- Step1X-Edit: https://github.com/stepfun-ai/Step1X-Edit
- OmniGen2: https://github.com/VectorSpaceLab/OmniGen2
- FireRed-Image-Edit: https://github.com/FireRedTeam/FireRed-Image-Edit
- JoyAI-Image: https://github.com/jd-opensource/JoyAI-Image
- HiDream-I1: https://github.com/HiDream-ai/HiDream-I1
- Wan 2.2: https://github.com/Wan-Video/Wan2.2
- LTX-2: https://github.com/Lightricks/LTX-2
- Mochi: https://github.com/genmoai/mochi
- Open-Sora: https://github.com/hpcaitech/Open-Sora
- BiRefNet: https://github.com/ZhengPeng7/BiRefNet
- Real-ESRGAN: https://github.com/xinntao/Real-ESRGAN
- SAM 2: https://github.com/facebookresearch/sam2
- ComfyUI: https://github.com/comfyanonymous/ComfyUI

**참고 기사**
- Wan 2.5 오픈소스 여부: https://wan27.org/blog/wan-2-5-open-source-guide
- Wan 3.0 오픈소스 여부: https://www.atlascloud.ai/blog/tips/is-wan-3.0-open-source
- LTX-2 오픈웨이트 발표: https://www.globenewswire.com/news-release/2026/01/06/3213304/0/en/Lightricks-Open-Sources-LTX-2-the-First-Production-Ready-Audio-and-Video-Generation-Model-With-Truly-Open-Weights.html
- Stability Community License: https://stability.ai/news-updates/license-update
- 오픈소스 이미지 모델 개관: https://www.bentoml.com/blog/a-guide-to-open-source-image-generation-models
