#!/usr/bin/env python3
"""규격 드리프트 가드: 팩 규격(스킬 frontmatter 필드·계약 키·사람 여부 값)은 자기완결 원칙 때문에
templates/·CLAUDE.md·docs/check-criteria.md에 재진술된다. 정본은 check/_common.py다. 어긋나면 여기서 실패한다.
paperthin의 check-catalog-sync와 같은 자리다: 하나의 집이 다른 곳을 먹이는 대신, CI가 복사본을 지킨다.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import CONTRACT_KEYS, HUMAN_VALUES, SKILL_FIELDS, parse_contract

ROOT = Path(__file__).resolve().parent.parent
fail = 0


def err(msg):
    global fail
    fail = 1
    print(f"::error::spec-sync: {msg}")


card = (ROOT / "templates/skill-card.md").read_text(encoding="utf-8")
fm = card.split("---")[1]
card_fields = [line.split(":")[0].strip() for line in fm.splitlines() if re.match(r"^\w+:", line)]
if card_fields != SKILL_FIELDS:
    err(f"templates/skill-card.md 필드 {card_fields} != 정본 {SKILL_FIELDS}")
for v in HUMAN_VALUES:
    if v not in fm:
        err(f"templates/skill-card.md의 human 주석에 '{v}'가 없음")

c = parse_contract(ROOT / "templates/CONTRACT.md")
if c is None:
    err("templates/CONTRACT.md에 contract 블록이 없음")
else:
    block = re.search(r"```contract\n(.*?)```", (ROOT / "templates/CONTRACT.md").read_text(encoding="utf-8"), re.S).group(1)
    keys = re.findall(r"^(\w+):", re.sub(r"#.*", "", block), re.M)
    if keys != CONTRACT_KEYS:
        err(f"templates/CONTRACT.md 키 {keys} != 정본 {CONTRACT_KEYS}")

for doc in ["CLAUDE.md", "docs/check-criteria.md"]:
    text = (ROOT / doc).read_text(encoding="utf-8")
    for k in CONTRACT_KEYS:
        if f"`{k}`" not in text and k not in text:
            err(f"{doc}가 계약 키 '{k}'를 언급하지 않음")
    for f in SKILL_FIELDS:
        if f"`{f}`" not in text:
            err(f"{doc}가 스킬 필드 '{f}'를 언급하지 않음")

if fail:
    print("✗ 규격 드리프트"); sys.exit(1)
print(f"✓ 규격 동기 OK: 스킬 필드 {len(SKILL_FIELDS)}개 · 계약 키 {len(CONTRACT_KEYS)}개 · 사람 여부 값 {len(HUMAN_VALUES)}개가 templates/ · CLAUDE.md · docs/와 일치")
