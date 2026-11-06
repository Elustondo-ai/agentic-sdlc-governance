"""Validate one report run and emit its slide order. This utility never writes."""
import argparse
import json
import sys
from pathlib import Path

CORE = Path(__file__).resolve().parents[2]
KINDS = ("definition", "status", "plan")
COORDINATOR = "ASDG-COORDINATOR"


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def texts(values):
    return isinstance(values, list) and bool(values) and all(map(nonempty, values))


def validate_packet(packet, role, run):
    if not isinstance(packet, dict) or packet.get("role_id") != role["role_id"]:
        raise ValueError("packet role does not match the assignment")
    for key in ("run_id", "project", "snapshot"):
        if packet.get(key) != run[key]:
            raise ValueError(f"packet {key} differs from the run")
    loaded = packet.get("loaded")
    if not texts(loaded) or not {role["entry"], role["skill"]}.issubset(loaded):
        raise ValueError("packet is missing required role source references")
    slides = packet.get("slides")
    if not isinstance(slides, list) or len(slides) != len(KINDS):
        raise ValueError("expected exactly three slides")
    for slide, kind in zip(slides, KINDS):
        if not isinstance(slide, dict) or slide.get("kind") != kind:
            raise ValueError(f"expected slide kind {kind}")
        if not all(nonempty(slide.get(key)) for key in ("headline", "visual_brief", "notes")):
            raise ValueError(f"{kind} needs a headline, visual brief and spoken notes")
        if not texts(slide.get("points")) or len(slide["points"]) > 3 or not texts(slide.get("sources")):
            raise ValueError(f"{kind} needs 1–3 points and source references")
    return slides


def ordered_report(run, catalogue):
    if not isinstance(run, dict) or not all(nonempty(run.get(k)) for k in ("run_id", "project", "snapshot")):
        raise ValueError("run_id, project and snapshot must identify this run")
    roster = {r["role_id"]: r for r in sorted(catalogue["agents"], key=lambda r: r["stage"]) if r["stage"] > 0}
    owner, client = run.get("owner"), run.get("client")
    governance = owner == COORDINATOR
    if client not in ("codex", "claude") or not nonempty(owner) or (not governance and owner not in roster):
        raise ValueError("unsupported client or reporting role")
    if governance and (client == "claude" or run.get("named_delegation") is not True):
        raise ValueError("BLOCKED: named ASDG delegation unavailable on this client")
    expected = list(roster) if governance else [owner]
    outcomes = run.get("outcomes")
    if not isinstance(outcomes, dict) or set(outcomes) != set(expected):
        raise ValueError("one explicit outcome is required for every assigned role")
    slides, missing, workers = [], {}, set()
    for role_id in expected:
        item = outcomes[role_id]
        if not isinstance(item, dict):
            raise ValueError(f"invalid outcome for {role_id}")
        if "reason" in item:
            if "packet" in item or not nonempty(item["reason"]):
                raise ValueError(f"ambiguous failure for {role_id}")
            missing[role_id] = item["reason"]
            continue
        if governance:
            worker = item.get("worker_ref")
            if not nonempty(worker) or worker in workers:
                raise ValueError("each returned role needs a distinct worker receipt")
            workers.add(worker)
        section = validate_packet(item.get("packet"), roster[role_id], run)
        slides.extend(dict(slide, role_id=role_id) for slide in section)
    if not slides:
        return {"status": "BLOCKED", "missing": missing, "slides": []}
    if missing:
        slides.append({"kind": "coverage", "role_id": COORDINATOR, "missing": missing})
    return {"status": "PARTIAL" if missing else "COMPLETE", "missing": missing, "slides": slides}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def renderer_preflight(provider):
    if provider is None:
        return {"status": "UNAVAILABLE", "reason": "a reviewed provider checkout is required"}
    script = provider.resolve() / "asdg/skills/asdg-presentation/src/build.py"
    if not script.is_file():
        return {"status": "UNAVAILABLE", "reason": f"missing provider renderer: {script}"}
    return {"status": "LOCATED", "script": str(script)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path, help="parent's JSON run envelope")
    parser.add_argument("--provider", type=Path, help="explicit reviewed provider checkout for export")
    args = parser.parse_args()
    try:
        catalogue = json.loads((CORE / "00-governance/types/agent-catalog.json").read_text())
        plan = ordered_report(json.loads(args.run.read_text(), object_pairs_hook=unique_object), catalogue)
        plan["renderer"] = renderer_preflight(args.provider)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    return 1 if plan["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(main())
