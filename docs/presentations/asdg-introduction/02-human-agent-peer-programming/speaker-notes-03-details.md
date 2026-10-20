# Slide 02 — Explanation and example

Imagine an implementation agent changing the warning behavior in Speaker Coach. A quality-focused agent could check boundary cases, while a reviewer examines whether the change still satisfies the intended behavior. All three should refer to the same contract and the same candidate change.

Their agreement would not automatically make the result correct. They might share an incorrect assumption. That is why the repository must include independently inspectable evidence, and why the human needs a clear account of what changed and what remains uncertain.

The benefit of specialization is not the number of agent names. It is the separation of responsibilities. We can initially perform these roles sequentially in one session. More concurrency is justified only when we can manage the coordination and review it creates.

Shared context also means shared navigation, not unlimited access. A participant should receive the material and tools needed for its task. Nothing about the illustrated control plane, a green checkmark, or an agent's confident response creates permission to merge or publish.
