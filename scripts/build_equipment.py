"""Backlog (클로드) 시트 CSV → data/equipment.json 변환.

사용법: python build_equipment.py backlog.csv ../data/ecn_rules.json ../data/
결과: data/eq1.json ~ eq4.json (GitHub 업로드 크기를 줄이려고 4개로 나눔)
열 위치(시트1): H PROJECT NO. / I TYPE / J EFEM P/N / K Process P/N / M PO DATE /
Q 기구 E-BOM / S 전장 E-BOM / BJ QC 검수 / BK QC 완료(TRUE) /
BP Factory Out Date / BQ 출하 완료(TRUE)
"""
import csv, json, re, sys, datetime

COL = dict(project=7, type=8, efem=9, proc=10, po=12, mech=16, elec=18, out=67, shipped=68, qc=61, qcdone=62, dev=73)


def parse_full(s):
    """26-6-20, 2026-06-20, 2026. 9. 20 → date"""
    s = (s or "").strip()
    m = re.match(r"^(\d{2,4})\s*[-.]\s*(\d{1,2})\s*[-.]\s*(\d{1,2})", s)
    if not m:
        return None
    y, mo, d = map(int, m.groups())
    if y < 100:
        y += 2000
    try:
        return datetime.date(y, mo, d)
    except ValueError:
        return None


def parse_md(s, po):
    """6/25 처럼 연도 없는 날짜 → PO DATE와 가장 가까운 연도로 붙임."""
    s = (s or "").strip()
    full = parse_full(s)
    if full:
        return full
    m = re.match(r"^(\d{1,2})/(\d{1,2})$", s)
    if not m or not po:
        return None
    mo, d = map(int, m.groups())
    cands = []
    for y in (po.year - 1, po.year, po.year + 1):
        try:
            cands.append(datetime.date(y, mo, d))
        except ValueError:
            pass
    return min(cands, key=lambda x: abs((x - po).days)) if cands else None


def iso(d):
    """2026-06-20 → 260620 (용량 절약)"""
    return d.strftime("%y%m%d") if d else None


def main(src, rules, outdir, parts=4):
    pns = set()
    for r in json.load(open(rules, encoding="utf-8"))["ecns"]:
        pns.update((r.get("match") or {}).get("pn") or [])
    rows = list(csv.reader(open(src, encoding="utf-8")))
    out = []
    for r in rows[1:]:
        r = r + [""] * (80 - len(r))
        proj = r[COL["project"]].strip()
        if not proj:
            continue
        po = parse_full(r[COL["po"]])
        out.append([
            proj,
            r[COL["type"]].strip(),
            " ".join(p for p in pns if p in r[COL["efem"]] or p in r[COL["proc"]]),
            iso(po) or "",
            iso(parse_md(r[COL["mech"]], po)) or "",
            iso(parse_md(r[COL["elec"]], po)) or "",
            iso(parse_full(r[COL["out"]])) or "",
            1 if r[COL["shipped"]].strip().upper() == "TRUE" else 0,
            iso(parse_md(r[COL["qc"]], po)) or "",
            1 if r[COL["qcdone"]].strip().upper() == "TRUE" else 0,
        ])
    # 각 행: [PROJECT NO., TYPE, ECN 대상 P/N, PO DATE, 기구 E-BOM, 전장 E-BOM, Factory Out, 출하완료(1/0), QC 검수, QC 완료(1/0)]  날짜는 YYMMDD
    n = (len(out) + parts - 1) // parts
    for i in range(parts):
        json.dump(dict(updated=datetime.date.today().isoformat(), equipment=out[i*n:(i+1)*n]),
                  open(f"{outdir}/eq{i+1}.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(len(out), "equipment")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
