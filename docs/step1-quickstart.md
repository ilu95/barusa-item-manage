# 1단계 실행 가이드 — 첫 착용샷 뽑기

목표: **GPU 없이, 카드 등록 없이, 오늘 안에 착용샷 1장.**
경로: Cloudflare Workers AI + FLUX.2 [klein] 4B

---

## ⚠️ 먼저 알고 시작할 것 (중요)

FLUX.2 klein은 **마스크 인페인팅이 아니라 레퍼런스 기반 재생성**입니다.
인물 사진을 넣으면 그 픽셀을 그대로 두고 모자만 덧그리는 게 아니라,
**레퍼런스를 참고해 이미지를 새로 그립니다.**

그래서:
- 얼굴이 베이스컷과 **픽셀 단위로 동일하지는 않습니다.** 미세하게 달라집니다.
- 앞서 설계한 "베이스컷 고정 재사용 = 동일 인물성 100% 보장"은
  **로컬 인페인팅에서 성립하는 이야기**였습니다. API 방식에서는 근사치입니다.

**1단계에서 확인할 질문이 바로 이겁니다:**
> 같은 베이스컷으로 여러 번 돌렸을 때, 소비자가 "같은 모델"로 인식할 만큼 일관된가?

- **된다** → 이 경로로 계속 갑니다. 비용 0, 장비 0.
- **안 된다** → Qwen-Image-Edit + 마스크 인페인팅(로컬 또는 ModelScope)으로 갑니다.

어느 쪽이든 1단계를 해야 알 수 있고, 비용은 0원입니다.

---

## STEP 1. Cloudflare 계정과 API 토큰 (5분)

1. https://dash.cloudflare.com/sign-up/workers-and-pages 에서 가입
   → **신용카드 필요 없습니다.**
2. 대시보드에서 **Workers AI** 페이지로 이동
3. **Use REST API** 클릭
4. **Create a Workers AI API Token** → 내용 확인 → **Create API Token** → **Copy API Token**
   - 토큰은 이때 한 번만 전체가 보입니다. 바로 복사해 두세요.
5. 같은 화면의 **Get Account ID**에서 **Account ID** 복사

> 템플릿 대신 직접 토큰을 만들 경우, `Workers AI - Read` 와 `Workers AI - Edit`
> 권한이 **둘 다** 필요합니다.

---

## STEP 2. 저장소와 환경 준비 (5분)

```bash
git clone https://github.com/ilu95/barusa-item-manage.git
cd barusa-item-manage
git checkout claude/hat-shop-ai-try-on-fzarvi

pip install pillow requests

cp .env.example .env
```

`.env` 파일을 열어 STEP 1에서 복사한 값을 채웁니다.

```
CF_ACCOUNT_ID=여기에_계정_ID
CF_API_TOKEN=여기에_토큰
```

> `.env` 는 `.gitignore` 에 들어 있어 커밋되지 않습니다. 토큰은 절대 공유하지 마세요.

---

## STEP 3. 인물 베이스컷 만들기 (20분)

전속 모델 사진이 필요합니다. 세 가지 방법 중 편한 걸 고르세요.

**(a) 같은 Cloudflare로 만들기** — 프롬프트만으로 인물 생성
```bash
curl -X POST \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/ai/run/@cf/black-forest-labs/flux-2-klein-4b" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -F 'prompt=Studio portrait of a Korean woman in her twenties, upper body, short bob hair, plain light grey background, soft even lighting, looking at camera, forehead and hairline clearly visible, no hat, photorealistic' \
  -F width=1024 -F height=1024 \
  | python3 -c "import sys,json,base64,pathlib; d=json.load(sys.stdin); pathlib.Path('models/female_01/front.png').parent.mkdir(parents=True,exist_ok=True); pathlib.Path('models/female_01/front.png').write_bytes(base64.b64decode(d['result']['image'])); print('저장 완료')"
```

**(b) 무료 웹 도구로 만들기** — Cloudflare 멀티모달 플레이그라운드에서 손으로
https://multi-modal.ai.cloudflare.com/

**(c) 이미 있는 사진 사용** — 단, 실존 인물이면 초상권 동의가 필요합니다.

베이스컷 요건:
- 배경 단색, 상반신, **이마와 헤어라인이 보일 것**
- 짧거나 묶은 머리 (긴 생머리는 모자 합성 실패율이 높습니다)
- 모자를 쓰지 않은 상태

`models/female_01/front.png` 로 저장하세요.

---

## STEP 4. 모자 상품컷 준비 (5분)

`products/cap_navy/main.png` 로 저장합니다.
배경이 제거된 PNG면 가장 좋고, 아니어도 일단 돌아갑니다.

> 스크립트가 투명 배경을 흰색으로 평탄화한 뒤 512px 미만으로 줄여서 보냅니다.
> (Cloudflare 제약: 입력 레퍼런스는 512×512 미만이어야 합니다.)

---

## STEP 5. 착용샷 생성 (1분)

```bash
python3 scripts/cf_tryon.py \
  --person models/female_01/front.png \
  --hat products/cap_navy/main.png \
  --n 3
```

`out/` 에 PNG 3장과 각각의 `.json`(프롬프트·시드 기록)이 생깁니다.

### 자주 쓰는 옵션
```bash
--n 5                  # 5장 뽑아서 고르기
--seed 12345           # 시드 고정 (재현·비교용)
--model klein-9b       # 품질 비교 (무료 한도를 훨씬 빨리 소진)
--width 1024 --height 1280   # 세로형 (256~1920)
--guidance 3.5         # 프롬프트 반영 강도
--label                # 하단에 AI 생성 고지 삽입
--prompt "..."         # 프롬프트 직접 지정
--dry-run              # 전송 없이 입력 준비만 확인
```

먼저 `--dry-run` 으로 입력이 제대로 잡히는지 확인하는 걸 권합니다.

---

## STEP 6. 결과 판정

3장을 나란히 놓고 봅니다.

| 확인 항목 | 통과 기준 |
|---|---|
| **인물 일관성** | 3장이 같은 사람으로 보이는가 |
| **상품 재현** | 챙 길이·크라운 깊이·색상·로고가 원본 모자와 같은가 |
| **착용 자연스러움** | 머리에 얹힌 각도, 머리카락과의 접촉, 그림자 |
| **해부학** | 손가락·귀·눈이 망가지지 않았는가 |

- **상품 재현이 안 되면** → 프롬프트에 모자 특징을 명시적으로 서술
  (예: `navy 6-panel baseball cap with flat embroidered white logo on front panel`)
- **인물이 계속 바뀌면** → 시드 고정 후 프롬프트에 `keep the person's face identical to image 0` 강조
- **그래도 안 되면** → klein의 한계입니다. Qwen-Image-Edit 경로로 전환하세요.

---

## 무료 한도 계산 (공식 단가 기준)

Workers Free 플랜: **하루 10,000 뉴런 무료**, UTC 00:00 리셋.
초과 시 과금이 아니라 **정지**되므로 예상 못 한 청구가 없습니다.

| 모델 | 공식 단가 | 우리 호출 1장 | 하루 무료 |
|---|---|---|---|
| **flux-2-klein-4b** | 입력 5.37 / 출력 26.05 뉴런 per 512×512 타일 | 입력 2장 ≈ 10.7 + 출력 1024² 4타일 ≈ 104 = **약 115 뉴런** | **약 87장** |
| flux-2-klein-9b | 첫 1MP 1,363.64 + 입력 MP당 181.82 | **약 1,700 뉴런** | **약 5~6장** |
| flux-1-schnell | 타일 4.80 + 스텝 9.60 | 1024² 4스텝 ≈ 58 뉴런 | 약 170장 (생성 전용) |

출력을 `1024×768`로 하면 타일이 4→3으로 줄어 **약 90 뉴런 / 하루 110장**이 됩니다.

→ 하루 3~30장인 우리 규모에는 **klein-4b 무료 한도로 충분합니다.**
klein-9b는 품질 비교용으로 **하루 몇 장만** 쓰세요.

---

## 라이선스 참고

Cloudflare의 FLUX.2 klein은 **파트너 모델**이고, 모델 페이지가
Black Forest Labs 이용약관(https://bfl.ai/legal/terms-of-service)을 가리킵니다.
API 사용 시에는 이 약관이 적용되므로, 상업적 사용 조건을 한 번 확인하고 시작하세요.

별개로 **klein 4B의 가중치 자체는 Apache 2.0**이라, 나중에 우리 GPU로 내려
돌리는 것은 자유입니다. (klein 9B 가중치는 비상업이라 로컬 이전이 안 됩니다.)
**퇴로를 남기려면 4B 기준으로 파이프라인을 짜세요.**

---

## 문제 해결

| 증상 | 원인 / 조치 |
|---|---|
| `CF_ACCOUNT_ID / CF_API_TOKEN 이 필요합니다` | `.env` 미작성 또는 위치 오류. 저장소 루트에 있어야 합니다 |
| HTTP 400 | 입력 이미지가 512×512 이상이거나 필드명 오류. 스크립트가 자동 처리하므로 원본 손상 여부 확인 |
| HTTP 401 / 403 | 토큰 오타, 또는 권한에 `Workers AI - Read/Edit` 누락 |
| HTTP 429 | 하루 10,000 뉴런 소진. UTC 00:00(한국시간 09:00)에 리셋 |
| 네트워크 오류 | 사내 방화벽/프록시가 api.cloudflare.com 을 막는 경우 |
| 고지 문구가 안 들어감 | 한글 폰트 없음. `--font /path/NanumGothic.ttf` 로 지정 |

---

## 다음 단계

1단계 통과 시:
- 베이스컷을 각도별 3~5컷으로 확장
- 모자 5종으로 재현율 측정
- 컬러 코디 그리드 추가
- 로컬 이전 검토 (klein 4B는 8GB VRAM)

1단계 실패 시:
- `docs/open-model-survey.md` 의 Qwen-Image-Edit 경로로 전환
- ModelScope 무료 2,000회/일 또는 SiliconFlow 장당 $0.04
