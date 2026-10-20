# Slide 06 — Explanation and example

Here is a practical review question for our presentation builder: when additional narration files are added, can the builder accidentally replace the original short deck? The reviewer should be able to find the output-naming decision, the implementation that selects the narration, and a test showing that the two builds remain separate.

That is more useful than a general claim that “all tests passed.” The evidence should address the behavior that changed. It should also state what was not tested, such as how a particular viewer handles a very long speaker-notes panel.

A second question concerns understanding. Could a human explain which files are sources, which are generated, and which notes enter each output? If the person cannot answer after reading the walkthrough, the documentation has not fully served its purpose.

That is a review criterion we can exercise with a few focused questions, not a demand for an examination after every edit. The amount of explanation should follow the significance and complexity of the change.
