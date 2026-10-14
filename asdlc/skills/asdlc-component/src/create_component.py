#!/usr/bin/env python3
"""Create or check an ASDLC component without overwriting existing content."""
import argparse
import re
from pathlib import Path

STAGES = [
("01", "context-and-domain-analysis", "Context and Domain Analysis"),
("02", "intent", "Intent"),
("03", "system-model-and-use-cases", "System Model and Use Cases"),
("04", "benchmarks-test-strategy-and-success-criteria", "Benchmarks, Test Strategy and Success Criteria"),
("05", "high-level-solution-design-and-architecture", "High-Level Solution Design and Architecture"),
("06", "viable-proof-of-concept", "Viable Proof of Concept"),
("07", "planning", "Planning"),
("08", "low-level-design", "Low-Level Design"),
("09", "build-and-test-cycle", "Build and Test Cycle"),
("10", "document-review-and-release", "Document, Review and Release"),
("11", "operational-reality-devops-and-user-acceptance", "Operational Reality, DevOps and User Acceptance"),
("12", "observability-insights-and-learning", "Observability, Insights and Learning"),
]
def files_for(name):
    out = {
        "README.md": f"# {name}\n\nASDLC component. Scope, owner, and current state: to be reviewed.\n\n`docs/`: lifecycle; `types/`: contracts; `src/`: implementation; `tests/`: verification.\n",
        "docs/00-governance/README.md": "# Governance\n\nStatus: not reviewed. Record authority, approval boundaries, and operating policies.\n",
        "types/README.md": "# Type contracts\n\nUse an appropriate notation (Markdown, Python, TypeScript, schema, etc.). Document inputs, outputs, constraints and failures.\n",
        "src/README.md": "# Implementation\n\nImplementation belongs here; no language is prescribed.\n",
        "tests/README.md": "# Tests\n\nTests and validation evidence belong here.\n",
    }
    for n,slug,title in STAGES:
        out[f"docs/{n}-{slug}/README.md"] = f"# {n} — {title}\n\nStatus: not started. Record decisions and evidence here when this stage is undertaken.\n"
    return out
def run(repo,name,check=False):
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*",name):
        raise ValueError("Component name must be lowercase kebab-case")
    repo=repo.resolve()
    if not repo.is_dir(): raise ValueError("Repository root must exist")
    target=repo/"asdlc"/"components"/name
    expected=files_for(name)
    if check:
        missing=[str(target/p) for p in expected if not (target/p).is_file()]
        if missing: raise ValueError("Missing files:\n"+"\n".join(missing))
        return target
    if target.exists(): raise FileExistsError(f"Refusing to overwrite existing component: {target}")
    target.mkdir(parents=True)
    for relative,content in expected.items():
        p=target/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding="utf-8")
    return target
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True,type=Path)
    ap.add_argument("--name",required=True)
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    print(run(args.repo,args.name,args.check))
