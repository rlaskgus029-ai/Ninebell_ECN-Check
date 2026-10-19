# Ninebell ECN 적용 확인

PROJECT NO.를 입력하면 그 장비에 적용해야 하는 ECN을 보여주는 사이트입니다.

- `data/ecn_rules.json`: ECN 최종본 PDF에서 정리한 적용 규칙 (적용 장비 타입, 적용 범위, 적용일자, 판정 기준)
- `data/equipment.json`: Backlog (클로드) 구글시트에서 만든 장비 목록 (PO DATE, 기구/전장 E-BOM, 출하일)
- `scripts/build_equipment.py`: Backlog CSV → equipment.json 변환

## 판정 규칙
- ECN-D: (E-BOM) 표기 → 기구 E-BOM / ECN-E: (E-BOM) 표기 → 전장 E-BOM
- (PO) 또는 날짜만 → PO DATE
- ECN-G(제어): 적용 장비 타입만 맞으면 적용 / ECN-I(IMP): 제외
- 적용 범위: 신규=적용일 이후, 기발주=미출하 장비 포함, 기출하=날짜와 무관하게 적용
- 적용일자 After Approval → 확인 필요 / 적용일자 빈칸 → 승인일 기준
- 특정 장비 지정 ECN → 지정 장비 + 같은 타입
- PJT/SCS/RCS 사양 확인이 필요한 ECN은 확인 필요로 표시
