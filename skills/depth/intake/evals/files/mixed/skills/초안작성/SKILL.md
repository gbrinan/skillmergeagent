---
name: 초안작성
owner: 김보고
quadrant: depth
human: 자동
inputs: [주간실적]
outputs: [보고서초안]
reads: [주간실적.xlsx]
writes: []
next: null
---

# 초안작성: 주간 실적을 보고서 초안으로

## 절차
1. 주간실적.xlsx의 이번 주 시트를 읽는다.
2. 항목별 증감을 문장으로 쓴다.

## 판단기준
- 전주 대비 ±10%를 넘는 항목만 본문에 올린다.
