# FG03a — LifeBuckets: a personal assistant

LifeBuckets is an ambitious open-source project we are developing to help an individual organize everyday life. Its scope includes health, career, email, the personal workspace and other responsibilities that usually live across separate applications.

The target architecture combines an organized Google Drive workspace with a coordinating agent running in the cloud. Drive holds the buckets, documents and shared context. The cloud agent uses that information to understand requests, plan work and coordinate actions.

You can interact through the LifeBuckets user interface and its conversational assistant. The shared workspace also lets connected assistants such as ChatGPT or Gemini work with the same information. That access depends on the integrations and permissions available in the chosen interface. The documents remain accessible directly in Google Drive as well.

Through integrations, the cloud agent is intended to retrieve information and make authorized updates in services such as Apple Reminders, Google Calendar and email. It connects the places where people already manage information instead of requiring everything to live inside one new screen.

This diagram describes the direction of the project, rather than claiming that every integration is already complete. LifeBuckets gives us a concrete example for this chapter: a product with its own domain vocabulary, developed under SDLC2 and implemented with the help of a development agent.
