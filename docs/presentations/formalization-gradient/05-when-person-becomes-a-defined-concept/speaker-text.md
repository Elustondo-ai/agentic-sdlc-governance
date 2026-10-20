# FG04 — When “Person” becomes a defined concept

The word person carries many meanings in ordinary conversation. In this illustrative contact system, we give Person a narrower definition: a human contact represented by a stable identifier.

That definition tells us something important before we write code. Changing the display name should not change the identity. A record with a valid identifier, however, does not prove that the contact corresponds to a real human.

The UML class view shows the model’s structure. It has an identifier, a display name and an optional birth date. The typed boundary then explains how unknown incoming data becomes either a Person value or a validation error.

A programming-language type helps developers reason about values, but external input still requires runtime checks. Those checks must reflect the domain rules, including whatever rules we choose for identifiers and dates.

The point is continuity of meaning. We can use the term Person in a conversation, diagram, interface and test, while referring to the same definition. Differences between those representations should be visible and resolved deliberately.
