# questions/__init__.py

# Keeps signal wiring stable in older Django setups and explicit app config usage.
# Safe even if Django ignores it (newer Django versions).
default_app_config = "questions.apps.QuestionsConfig"
