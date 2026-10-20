# Slide 12 — Explanation and example

Suppose the unresolved question is whether a simple timing signal can identify a long speaking turn well enough for a useful warning. A proof of concept should define the situations to try, the expected signal, and the kinds of false warning that would invalidate the approach.

We might deliberately exclude accounts, polished styling, and release automation from that experiment because they do not answer the question. That bounded omission is appropriate for an experiment; it would be inappropriate to hide the same omissions in a production-readiness claim.

A disappointing result is still useful when it changes the architectural decision early. A successful result is also limited: it supports the tested assumption under the tested conditions.

Prototype code can be reused, but reuse is a separate engineering decision. It must satisfy the component contracts, tests, review, and operational requirements of the production system. The learning is the necessary output of the experiment; keeping its implementation is optional.
