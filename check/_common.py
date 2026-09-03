"""check/ 스크립트가 공유하는 파서. 스킬 frontmatter · 계약 블록 · 이름 정규화 · 정지 문구 판정."""
import re
from pathlib import Path

# 표 이름으로 인식하는 확장자. 확장자 없는 이름(DB 테이블·시트 탭)은 계약 tables에 적으면 인식한다.
TABLE_EXT = r"(?:xlsx|xls|docx|pptx|pdf|csv|json)"
TABLE_RE = re.compile(r"[\w가-힣]+(?:[_\-][\w가-힣]+)*\." + TABLE_EXT)  # 공백은 이름의 일부로 보지 않는다

HUMAN_MAP = {"자동": "자동", "auto": "자동", "증강": "증강", "augment": "증강",
             "사람고유": "사람고유", "human": "사람고유"}


def norm(s):
    """표기 변형(띄어쓰기·언더스코어·하이픈·대소문자)을 같은 것으로 본다."""
    return re.sub(r"[\s_\-]", "", s).lower()


def human_of(meta):
    return HUMAN_MAP.get((meta.get("human") or "").strip().lower(), (meta.get("human") or "").strip())


def has_halt(body):
    """본문에 '확인 요청 + 멈춤' 문구가 있는가. 한국어(확인·멈)와 영어(confirm·halt/stop/pause) 모두 인정."""
    ko = "확인" in body and "멈" in body
    en = re.search(r"confirm", body, re.I) and re.search(r"\b(halt|stop|pause)", body, re.I)
    return bool(ko or en)


def parse_skill(path):
    text = Path(path).read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", text, re.S)
    if not m:
        return None, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.split("#", 1)[0].strip() if not v.strip().startswith("[") else v.strip()
        if v.startswith("["):
            v = v.split("]", 1)[0]
            meta[k.strip()] = [x.strip() for x in v.strip("[]").split(",") if x.strip()]
        else:
            meta[k.strip()] = None if v in ("null", "~", "") else v
    return meta, m.group(2)


def find_skills(pack):
    """skills/<사분면>/<이름>/SKILL.md (대소문자 무관). archive/ 아래는 제외."""
    pack = Path(pack)
    out = []
    for p in sorted(pack.glob("skills/*/*/*.md")):
        if p.name.lower() == "skill.md" and "archive" not in p.parts:
            out.append(p)
    return out


def next_of(meta):
    return [x.strip() for x in re.split(r"[|,]", meta.get("next") or "") if x.strip()]


def parse_contract(path):
    """CONTRACT.md의 ```contract 블록을 읽는다. 없으면 None."""
    path = Path(path)
    if not path.is_file():
        return None
    m = re.search(r"```contract\r?\n(.*?)```", path.read_text(encoding="utf-8"), re.S)
    if not m:
        return None
    body = re.sub(r"#.*", "", m.group(1))
    c = {"tables": {}, "writers": {}, "chain": [], "payloads": [], "threshold": None, "halt_at": None}
    section = None
    for line in body.splitlines():
        if not line.strip():
            continue
        if re.match(r"^\w+:", line):
            key, val = line.split(":", 1)
            key, val = key.strip(), val.strip()
            if key in ("tables", "writers") and not val:
                section = key
                continue
            section = None
            if key == "chain":
                c["chain"] = [[s.strip() for s in p.split("->") if s.strip()]
                              for p in val.split(";") if p.strip()]
            elif key == "payloads":
                c["payloads"] = [s.strip() for s in val.split(",") if s.strip()]
            elif key in ("threshold", "halt_at"):
                c[key] = None if val in ("(해당 없음)", "(없음)", "") else val
        elif section and ":" in line:
            k, v = line.split(":", 1)
            if section == "tables":
                c["tables"][k.strip()] = [x.strip() for x in v.split(",") if x.strip()]
            else:
                c["writers"][k.strip()] = v.strip()
    return c


def halt_list(c):
    return [x.strip() for x in re.split(r"[,;]", (c or {}).get("halt_at") or "") if x.strip()]
