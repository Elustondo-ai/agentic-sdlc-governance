# Stage acceptance tests: case guide

[Module guide](test_stage_review.md) · [Source](test_stage_review.py)

Each method below belongs to `StageReviewTests`, takes `self`, returns `None` and uses unittest assertions.
Names describe the intended regression checks; this index is not an execution result.

| Test method | Responsibility |
| --- | --- |
| `test_readiness_is_not_acceptance` | readiness is not acceptance. |
| `test_changed_picture_diagram_source_or_navigation_invalidates_acceptance` | changed picture diagram source or navigation invalidates acceptance. |
| `test_no_matching_readiness_or_fake_actor_or_wrong_stage` | no matching readiness or fake actor or wrong stage. |
| `test_missing_broken_remote_and_escaping_dependencies_fail` | missing broken remote and escaping dependencies fail. |
| `test_symlink_is_not_an_approved_asset` | symlink is not an approved asset. |
| `test_outgoing_sources_are_validated_without_approving_another_stage` | outgoing sources are validated without approving another stage. |
| `test_state_readback_reports_acceptance_without_mutating_unrelated_state` | state readback reports acceptance without mutating unrelated state. |
