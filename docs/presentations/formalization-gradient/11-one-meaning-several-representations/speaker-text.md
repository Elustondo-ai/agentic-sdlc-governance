# FG09 — One meaning, several representations

The result of this chapter is an architectural discipline. We define the domain meaning, express it in the forms that help us work, and maintain traceability between those forms.

A human explanation makes the concept understandable. Design and contracts explain its structure and boundaries. Workflows and code give it operational form. Evidence and review tell us whether the implementation actually behaves as intended.

These views serve different readers and purposes. They should refer to a clear governing definition instead of becoming independent, competing versions of the truth.

The feedback path matters. If an implementation disagrees with a specification, the agent should surface the mismatch. We may change the implementation, or deliberately revise the specification. Generating documentation that simply describes the current code does not settle that decision.

This connects back to the purpose of SDLC2: a human-governed development lifecycle that agents can operate. The formalization gradient helps us choose how to express each part so that the human can understand it, the agent can act on it, and the relevant claims can be checked.
