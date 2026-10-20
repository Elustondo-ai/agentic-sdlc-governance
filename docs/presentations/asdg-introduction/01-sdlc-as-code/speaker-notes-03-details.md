# Slide 01 — Explanation and example

Consider a small, hypothetical Speaker Coach feature that warns someone after a long uninterrupted turn. Context asks who uses the warning and in what kind of conversation. Intent might be to help the user share speaking time without distracting them. A use case follows a turn beginning, continuing, and ending; an alternative case handles uncertainty about who is speaking.

Before selecting an implementation, we would compare a simple timer with an approach that recognizes turn boundaries. Our success criteria should address false warnings and usability, not merely whether a timer can run. High-level design separates the observation, assessment, and visual-feedback responsibilities. A proof of concept is useful only for an unresolved assumption, such as whether the available signal identifies turn boundaries well enough.

Low-level design then states what each component receives, what it returns, and what happens when input is missing. A contract could be expressed in Markdown or in a suitable type language; the purpose is clarity, not a compulsory programming language. Build and test checks the implementation. Review checks that the human understands it. Acceptance checks whether the warning is actually useful in a running application.

This is an illustration, not a report that Speaker Coach already implements these capabilities. It also shows why having twelve folders cannot prove that a lifecycle was followed. Each relevant stage needs enough substance and evidence for the decision at hand; an unchanged architectural decision may simply be referenced rather than rewritten.
