# FG05 — Three languages working together

In a LifeBuckets development project, I would distinguish three interacting languages.

The first describes the product. Bucket, category and item have meanings within LifeBuckets. The second describes the development process. Sprint, release, review evidence and approval have meanings within SDLC2. The third consists of the operating conventions through which we work with Codex.

These boundaries matter even when the same word appears in more than one place. An item status in the application is different from a sprint status in governance. We should identify which domain owns the meaning whenever the context could be ambiguous.

A change request connects the domains. We specify the LifeBuckets behavior we want, apply the SDLC2 process to govern that change, and map the work onto the agent platform’s available mechanisms.

Codex DSL is convenient shorthand for that last area, but it contains several mechanisms with different interpreters. Our methodology should keep its meaning independently of those mechanisms. If we change development agents, our definition of review or approval should survive, even when its implementation changes.
