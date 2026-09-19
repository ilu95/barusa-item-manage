#!/usr/bin/env python3
"""Cloudflare Workers AI로 모자 착용샷을 생성한다.

인물 베이스컷과 모자 상품컷을 레퍼런스로 넣어 FLUX.2 [klein]에 합성을 시킨다.

  python3 scripts/cf_tryon.py --person models/female_01/front.png \
                              --hat products/cap_navy/main.png --n 3

자격증명은 환경변수나 저장소 루트의 .env에서 읽는다:
  CF_ACCOUNT_ID, CF_API_TOKEN
"""

import argparse
import base64
import io
import json
import os
import pathlib
import random
import sys
import time

import requests
from PIL import Image, ImageDraw, ImageFont

API_BASE = "https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{model}"

MODELS = {
    "klein-4b": "@cf/black-forest-labs/flux-2-klein-4b",
    "klein-9b": "@cf/black-forest-labs/flux-2-klein-9b",
}

# Cloudflare 제약: 입력 레퍼런스 이미지는 512x512 미만이어야 한다.
MAX_INPUT_SIDE = 480

DEFAULT_PROMPT = (
    "Image 0 is a photo of a person. Image 1 is a hat product photo. "
    "Put the exact hat from image 1 onto the head of the person in image 0. "
    "Keep the person's face, hairstyle, skin tone, clothing, pose, lighting and "
    "background exactly as in image 0. The hat must match image 1 exactly in "
    "shape, brim length, color, material, stitching and logo placement. "
    "The hat sits naturally on the head with correct perspective and a soft "
    "contact shadow. Photorealistic e-commerce product photograph, sharp focus."
)

DISCLOSURE = "AI 생성 이미지 · 실제 제품과 차이가 있을 수 있습니다"

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "C:/Windows/Fonts/malgun.ttf",
]


def load_env(root):
    """.env를 환경변수로 올린다. 이미 설정된 값은 덮어쓰지 않는다."""
    path = root / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def prepare_reference(path, flatten_bg=None):
    """레퍼런스 이미지를 512px 미만으로 줄이고 PNG 바이트로 반환한다."""
    img = Image.open(path)
    if flatten_bg and img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        canvas = Image.new("RGBA", img.size, flatten_bg)
        canvas.alpha_composite(img)
        img = canvas
    img = img.convert("RGB")

    scale = MAX_INPUT_SIDE / max(img.size)
    if scale < 1:
        new_size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
        img = img.resize(new_size, Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue(), img.size


def find_font(explicit=None):
    for candidate in filter(None, [explicit, *FONT_CANDIDATES]):
        if os.path.exists(candidate):
            return candidate
    return None


def add_disclosure(path, text=DISCLOSURE, font_path=None):
    """이미지 하단에 AI 생성 고지 한 줄을 넣는다."""
    resolved = find_font(font_path)
    if not resolved:
        print("  ! 한글 폰트를 못 찾아 고지 문구를 건너뜀 (--font 로 지정 가능)")
        return False

    img = Image.open(path).convert("RGB")
    size = max(14, img.width // 52)
    try:
        font = ImageFont.truetype(resolved, size)
    except OSError:
        font = ImageFont.truetype(resolved, size, index=0)

    draw = ImageDraw.Draw(img, "RGBA")
    pad = size // 2
    box = draw.textbbox((0, 0), text, font=font)
    bar_h = (box[3] - box[1]) + pad * 2
    draw.rectangle([0, img.height - bar_h, img.width, img.height], fill=(0, 0, 0, 140))
    draw.text((pad, img.height - bar_h + pad - box[1]), text, font=font, fill=(255, 255, 255))
    img.save(path)
    return True


def generate(args, account, token, seed, index):
    url = API_BASE.format(account=account, model=MODELS[args.model])

    person_bytes, person_size = prepare_reference(args.person)
    files = {"input_image_0": ("person.png", person_bytes, "image/png")}
    data = {
        "prompt": args.prompt,
        "width": str(args.width),
        "height": str(args.height),
        "seed": str(seed),
    }
    if args.guidance is not None:
        data["guidance"] = str(args.guidance)

    hat_size = None
    if args.hat:
        hat_bytes, hat_size = prepare_reference(args.hat, flatten_bg=(255, 255, 255, 255))
        files["input_image_1"] = ("hat.png", hat_bytes, "image/png")

    print(f"[{index}] seed={seed} 인물={person_size} 모자={hat_size or '-'}", flush=True)

    if args.dry_run:
        print("     (dry-run: 전송 생략)")
        return None

    started = time.time()
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            data=data,
            files=files,
            timeout=args.timeout,
        )
    except requests.exceptions.RequestException as exc:
        print(f"     ! 네트워크 오류: {type(exc).__name__}: {exc}")
        print("       api.cloudflare.com 에 접속 가능한지, 프록시/방화벽 설정을 확인하세요.")
        return None
    elapsed = time.time() - started

    if resp.status_code != 200:
        print(f"     ! HTTP {resp.status_code}: {resp.text[:400]}")
        return None

    try:
        payload = resp.json()
    except ValueError:
        print(f"     ! JSON이 아닌 응답: {resp.text[:400]}")
        return None
    if not payload.get("success", True):
        print(f"     ! API 오류: {json.dumps(payload.get('errors'), ensure_ascii=False)[:400]}")
        return None

    b64 = (payload.get("result") or {}).get("image")
    if not b64:
        print(f"     ! 응답에 image 없음: {json.dumps(payload)[:400]}")
        return None

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{pathlib.Path(args.person).stem}_{seed}"
    img_path = out_dir / f"{stem}.png"
    img_path.write_bytes(base64.b64decode(b64))

    # 재현을 위해 요청 파라미터를 같이 남긴다.
    (out_dir / f"{stem}.json").write_text(
        json.dumps(
            {
                "model": MODELS[args.model],
                "prompt": args.prompt,
                "seed": seed,
                "width": args.width,
                "height": args.height,
                "guidance": args.guidance,
                "person": str(args.person),
                "hat": str(args.hat) if args.hat else None,
                "elapsed_sec": round(elapsed, 2),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    if args.label:
        add_disclosure(img_path, font_path=args.font)

    print(f"     -> {img_path}  ({elapsed:.1f}s)")
    return img_path


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    load_env(root)

    p = argparse.ArgumentParser(description="Cloudflare Workers AI 모자 착용샷 생성")
    p.add_argument("--person", required=True, help="인물 베이스컷 경로")
    p.add_argument("--hat", help="모자 상품컷 경로 (누끼 PNG 권장)")
    p.add_argument("--prompt", default=DEFAULT_PROMPT)
    p.add_argument("--model", default="klein-4b", choices=sorted(MODELS))
    p.add_argument("--out", default="out", help="출력 디렉터리")
    p.add_argument("--n", type=int, default=1, help="생성 장수 (시드를 바꿔가며)")
    p.add_argument("--seed", type=int, help="고정 시드 (미지정 시 랜덤)")
    p.add_argument("--width", type=int, default=1024, help="출력 폭 256-1920")
    p.add_argument("--height", type=int, default=1024, help="출력 높이 256-1920")
    p.add_argument("--guidance", type=float, help="프롬프트 반영 강도")
    p.add_argument("--label", action="store_true", help="하단에 AI 생성 고지 삽입")
    p.add_argument("--font", help="고지 문구에 쓸 한글 폰트 경로")
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--dry-run", action="store_true", help="전송 없이 입력 준비만 확인")
    args = p.parse_args()

    for key in ("width", "height"):
        value = getattr(args, key)
        if not 256 <= value <= 1920:
            p.error(f"--{key} 는 256~1920 범위여야 합니다 (받은 값: {value})")

    account = os.environ.get("CF_ACCOUNT_ID")
    token = os.environ.get("CF_API_TOKEN")
    if not args.dry_run and not (account and token):
        p.error("CF_ACCOUNT_ID / CF_API_TOKEN 이 필요합니다. .env 를 만들거나 export 하세요.")

    made = 0
    for i in range(args.n):
        seed = args.seed if args.seed is not None else random.randint(1, 2**31 - 1)
        if generate(args, account, token, seed, i + 1):
            made += 1

    if not args.dry_run:
        print(f"\n완료: {made}/{args.n} 장 · {args.out}/ 확인")
    return 0 if made or args.dry_run else 1


if __name__ == "__main__":
    sys.exit(main())
