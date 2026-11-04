# ASDG runtime modules

These modules implement the local command-line tools, project checks and optional coordinator advice.
Each guide explains responsibilities, callable interfaces, data shapes, effects and collaborators beside its source.
Factual operations use the standard library; optional coordinator advice requires its separately installed SDK.

| Module | Responsibility |
| --- | --- |
| [cli_files.py](cli_files.md) | Conservative file transactions. |
| [cli_model.py](cli_model.md) | Project identity and role catalogue. |
| [cli_project.py](cli_project.md) | Initialize and inspect an embedded project. |
| [cli_clients.py](cli_clients.md) | Choose Codex and Claude integrations and render Claude skill adapters. |
| [cli_session.py](cli_session.md) | Check the default 00 Governance session role can load. |
| [cli_status.py](cli_status.md) | Evaluate project status. |
| [cli.py](cli.md) | ASDG command dispatcher. |
| [cli_sprint.py](cli_sprint.md) | Sprint state and scope. |
| [cli_policy.py](cli_policy.md) | Implementation permission calculation. |
| [cli_hook.py](cli_hook.md) | Tool-call guard. |
| [cli_runtime_env.py](cli_runtime_env.md) | Bounded coordinator environment. |
| [agent_config.py](agent_config.md) | Read agent adapter configuration. |
| [documentation.py](documentation.md) | Documentation length and review receipts. |
| [distribution_files.py](distribution_files.md) | Resolve the portable file list for checks and builds. |
| [cli_sync.py](cli_sync.md) | Preview and explicitly apply both methodology synchronization directions. |
| [cli_sync_manifest.py](cli_sync_manifest.md) | Read repository identities, snapshots and adoption baselines. |
| [purpose_review.py](purpose_review.md) | Purpose review and acceptance. |
| [stage_review.py](stage_review.md) | Review other stage documents. |
| [cli_advice.py](cli_advice.md) | Optional coordinator advice. |
| [cli_advice_report.py](cli_advice_report.md) | Save coordinator advice for review. |
| [cli_dashboard.py](cli_dashboard.md) | Local project-status dashboard. |
| [agent_log_event.py](agent_log_event.md) | Normalize public agent activity. |
| [agent_log_hook.py](agent_log_hook.md) | Lifecycle logging adapter. |
| [agent_log_store.py](agent_log_store.md) | Store per-agent activity. |

Return to [entry points](../README.md) or explore the [test guides](../../tests/README.md).
