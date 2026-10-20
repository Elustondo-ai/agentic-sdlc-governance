# Slide 13 — Explanation and example

Consider a hypothetical component contract for deciding when to display a warning. A useful worked example would state a sequence of input events, any intermediate state that matters, and the expected output. An exception example would show what happens when the observation is missing or uncertain.

Those examples help a reviewer distinguish a vague intention from a specific decision. They can also expose disagreement: perhaps the written rule says a pause resets the timer, while an example continues counting. The correct response is to resolve that conflict, not generate a test that quietly chooses one interpretation.

An ambiguity log records such questions and the resulting decisions. Dependency links identify which other contracts or tests may be affected. Reconciliation means comparing the implementation against something whose expected behavior has been established, rather than trusting two generated artifacts simply because they agree.

This is our proposed application of the reference's lesson. The local presentation build demonstrates packaging and reproducibility; it does not reproduce the paper's research results or validate the whole methodology.
