# Why an adapter exists at all — Deeper explanation

The current repository has a presentation adapter, but the component-creation skill's
discovery adapter was still missing at our last inspection. That is a concrete integration
gap to fix and test.

The adapter is a native discovery aid, not a new independent source of truth. Tools may
differ in whether they automatically read linked documents, so a smoke test should verify
invocation and the actual procedure followed, not merely that the adapter file exists.
