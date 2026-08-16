"""Textual CSS for the setup wizard."""

CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#app {
    width: 76;
    height: auto;
    max-height: 100%;
    overflow-y: auto;
    border: round $accent;
    padding: 1 2;
    background: $panel;
}

#intro {
    margin-bottom: 1;
    color: $text-muted;
}

.field-label {
    margin-top: 1;
    color: $text;
}

Input, #client, #scope {
    margin-top: 1;
}

#hint, #client-note {
    margin-top: 1;
    color: $text-muted;
}

#buttons {
    margin-top: 1;
    width: 100%;
    height: auto;
    align: center middle;
}

Button {
    min-width: 0;
    width: auto;
    margin: 0 1;
    padding: 0 1;
}

#status {
    margin-top: 1;
    min-height: 3;
    padding: 1;
    border: round $boost;
}
"""
