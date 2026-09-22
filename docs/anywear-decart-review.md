# Anywear (Decart) 조사 — 우리에게 쓸모 있나

조사일: 2026-09-22

---

## 결론 먼저

**우리가 쓸 도구는 아닙니다. 하지만 조사 가치는 매우 컸습니다.**

이유 세 가지:
1. **범주가 다릅니다.** Anywear는 *소비자가 쇼핑하며 자기 몸에 입혀보는* 도구입니다.
   우리가 필요한 건 *판매자가 상품 이미지를 만드는* 도구입니다.
2. **모자는 이 모델이 약한 카테고리**라고 **Decart 스스로 문서에 적어 놨습니다.**
3. **비용 구조가 소규모 쇼핑몰과 맞지 않습니다.** (아래 계산)

그런데 **가장 중요한 수확**은 따로 있습니다:

> **Decart가 모자·액세서리에 권장하는 우회법이, 우리가 만들고 있는 것과 정확히 같습니다.**
> 그것도 같은 모델 계열(FLUX.2 klein)로요.

업계 최전선 회사가 같은 결론에 도달해 있다는 건, 우리 접근이 맞다는 강력한 방증입니다.

---

## 1. Anywear가 뭔가

- **만든 곳:** Decart (실시간 비디오 확산 모델로 알려진 AI 회사, 비공개·상용)
- **형태:** 무료 Chrome 확장 프로그램. 베타 기간 계정 없이 사용
- **작동:** 사진 업로드가 아니라 **웹캠을 실시간으로 변환**합니다.
  아무 쇼핑몰(Zara, ASOS, Amazon 등) 상품 페이지에서 옷을 끌어다 놓으면
  내 카메라 영상에 실시간으로 입혀집니다.
- **기술:** `lucy-vton` 모델 (현재 Lucy Virtual Try-On 3.5), **WebRTC 스트리밍**.
  요청-응답이 아니라 영상 스트림을 실시간 변환하는 방식입니다.
- **오픈소스 아님.** 가중치 비공개, API 종량제 상용 서비스입니다.

Decart는 소비자용 Anywear와 별개로 **판매자용 API 플랫폼**도 운영합니다.
상품 페이지에 "Try it on" 버튼을 붙이는 예제를 공개하고 있습니다.
(https://github.com/DecartAI/tryon-examples — Next.js 예제 7종)

---

## 2. 🔑 가장 중요한 발견 — Decart 공식 문서 원문

`DecartAI/tryon-examples` README의 **Best practices** 섹션입니다.

### (a) 모자는 명시적으로 지원 대상입니다
프롬프트 패턴 표에 **Add** 패턴 예시로 이렇게 적혀 있습니다.

> | **Add** | Adding something the person isn't wearing | `"Add a wide-brimmed straw hat to the person's head"` |

좋은 프롬프트 예시에도 **야구모자가 직접 등장**합니다.

> ✅ `"Add a navy baseball cap to the person's head"`

### (b) 그런데 모자는 실시간 모델이 약한 카테고리라고 스스로 밝힙니다
같은 문서 **"Extreme precision for non-trivial items"** 섹션:

> For **accessories, bags, hats, jewelry**, or other items where the
> **standard real-time model may struggle**, you can add a **pre-generation step
> that produces a photorealistic try-on image** before sending it to Decart's
> real-time model. This gives the model a much clearer reference.

즉 **모자는 실시간 모델이 잘 못 하므로, 먼저 정지 이미지로 착용샷을 만들어
그걸 레퍼런스로 넣으라**는 겁니다.

### (c) 그 우회법에 쓰는 모델이 — FLUX.2 klein 9B 입니다
문서가 제시하는 실제 코드:

```typescript
const result = await fal.subscribe("fal-ai/flux-2/klein/9b/base/edit/lora", {
  input: {
    prompt: "TRYON [person in photo]. Replace the outfit with [garment]...",
    image_urls: [personUrl, clothingUrl],
    loras: [{ path: LORA_URL, scale: 1.0 }],
    guidance_scale: 2.5,
    num_inference_steps: 28,
  },
});
```

**인물 이미지 + 상품 이미지를 레퍼런스로 넣어 FLUX.2 klein으로 착용샷을 만든다.**
→ 우리가 `scripts/cf_tryon.py`로 하고 있는 것과 **완전히 동일한 구조**입니다.

차이는 두 가지뿐입니다.
- 그쪽은 fal.ai로 **klein 9B + 트라이온 LoRA**, 우리는 Cloudflare로 **klein 4B 소지**
- 그쪽은 그 결과를 실시간 모델의 입력으로 쓰고, 우리는 **그 결과 자체가 최종 산출물**

### (d) 레퍼런스 이미지 가이드 — 우리 프롬프트에 바로 반영할 것
- **깨끗한 상품 단독 이미지가 최선** (사람이 입은 사진 말고)
- **흰색/깔끔한 배경**이 이상적
- **최소 512×512 이상** — "모델은 본 것을 재현하므로 선명한 상품컷 = 더 나은 결과"
- 프롬프트는 **색·소재·질감·패턴·핏을 구체적으로, 20~30 단어**
- ❌ `"Put a jacket on the person"` (색·소재·핏 없음), ❌ `"Red hoodie"` (동작 없음)

---

## 3. 비용 — 소규모 쇼핑몰에는 맞지 않습니다

Decart API 요금 (Lucy VTON 3.5 기준, 공개 자료):
- **실시간 720p: 초당 약 $0.02**
- 배치 처리 720p: 초당 약 $0.04 (실시간의 2배)
- 크레딧 1 = $0.01, 종량제, 신규 계정에 무료 크레딧 제공

**우리 쇼핑몰에 붙였을 때:**

| 항목 | 계산 |
|---|---|
| 1분 세션 | $1.20 ≈ **1,700원** |
| 3분 세션 (일반적) | $3.60 ≈ **5,000원** |
| 하루 방문자 10명 체험 | 약 **5만 원/일** = 월 150만 원 |
| 하루 100명 체험 | 약 **50만 원/일** = 월 1,500만 원 |

모자 객단가를 3만 원, 마진을 20~30%로 잡으면 **개당 이익이 6,000~9,000원**입니다.
**체험 세션 한 번이 모자 한 개 이익을 거의 다 먹습니다.** 게다가 체험자 대부분은
구매하지 않습니다. 전환율 5%라면 구매 1건당 체험 비용이 10만 원입니다.

→ 대형 브랜드의 마케팅 예산이라면 몰라도, **우리 규모에서는 성립하지 않습니다.**

---

## 4. 추가로 걸리는 것 — 개인정보 국외이전

우리 쇼핑몰에 Decart 실시간 트라이온을 붙이면, **고객의 웹캠 영상이 해외 사업자
서버로 실시간 전송**됩니다. 개인정보보호법상 **국외이전에 해당**하여 별도 동의가
필요하고, 이전받는 자·국가·목적·보유기간을 고지해야 합니다.

앞서 "고객 셀피를 안 받으면 개인정보 이슈가 전면 소멸한다"고 정리했던 이점이
**이걸 붙이는 순간 통째로 되살아납니다.** 그것도 국내 처리보다 무거운 형태로요.

---

## 5. 그래서 뭘 가져갈 것인가

### 가져갈 것 ✅
1. **접근 방식 검증.** 모자에는 실시간 트라이온이 아니라 **정지 이미지 편집**이 맞다는 걸
   업계 최전선 회사가 자사 문서에서 인정하고 있습니다. 우리 방향이 맞습니다.
2. **프롬프트 패턴.** `Substitute` / `Add` 구조와 20~30 단어 구체 서술 원칙을
   `cf_tryon.py`의 기본 프롬프트에 반영할 가치가 있습니다.
   모자는 **Add 패턴** — `"Add a navy 6-panel baseball cap to the person's head"`.
3. **레퍼런스 이미지 요건.** 상품 단독 / 흰 배경 / 512px 이상 — 우리 STEP 4와 일치합니다.
4. **klein + 트라이온 LoRA 조합.** 우리 1단계에서 klein 기본 모델의 재현율이 부족하면,
   **트라이온 LoRA를 얹는 것**이 다음 수순이라는 힌트를 얻었습니다.

### 안 가져갈 것 ❌
- Decart API 채택 (비용·국외이전)
- 실시간 트라이온 기능 자체 (우리 단계에서 불필요, 모자에 약함)

---

## 6. 참고

- Anywear 공식: https://anywear.decart.ai/
- Chrome 확장: https://chromewebstore.google.com/detail/anywear-live-virtual-try/hijnklblgecbdlhjiofhlhjpndpifejh
- **Decart 트라이온 예제 저장소 (권장 정독):** https://github.com/DecartAI/tryon-examples
- Decart API 문서 — 이커머스 트라이온: https://docs.platform.decart.ai/examples/ecommerce-try-on
- Decart 요금: https://docs.platform.decart.ai/getting-started/pricing
- Lucy VTON 모델 페이지: https://platform.decart.ai/models/lucy-vton

> 참고: `anywear.decart.ai`, `docs.platform.decart.ai` 는 이 작업 환경의 egress 정책상
> 직접 열람이 차단돼, 공식 GitHub 저장소 원문과 검색 결과로 교차 확인했습니다.
> 요금은 변동될 수 있으니 실제 검토 시 공식 요금 페이지를 직접 확인하세요.
