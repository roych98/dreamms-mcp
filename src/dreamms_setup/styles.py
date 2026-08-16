"""Textual CSS for the setup wizard."""

CSS = """
Screen {
    align: center middle;
    background: #080f1c;
    color: #dce8f9;
}

Header {
    background: #142238;
    color: #91a5c1;
}

Footer {
    background: #0b1424;
    color: #91a5c1;
}

#app {
    width: 88%;
    max-width: 110;
    height: auto;
    max-height: 100%;
    overflow-y: auto;
    border: round #4d9cff;
    padding: 1 2;
    background: #0e1727;
}

#title-row {
    width: 100%;
    height: 4;
    align: left middle;
}

#title-copy {
    width: 1fr;
    height: auto;
}

#title {
    color: #dce8f9;
    text-style: bold;
}

#subtitle, .field-hint, #detail-note {
    color: #91a5c1;
}

#badge {
    width: 13;
    height: 3;
    content-align: center middle;
    border: round #4fd9c3;
    background: #4fd9c3;
    color: #08251f;
    text-style: bold;
}

#intro {
    min-height: 4;
    margin: 1 0;
    padding: 1;
    border: round #496887;
    background: #182a43;
    color: #dce8f9;
}

#form-grid, #details {
    width: 100%;
    height: auto;
    grid-size: 2;
    grid-columns: 1fr 1fr;
    grid-gutter: 1 3;
}

.field-group {
    height: auto;
}

.field-label {
    margin: 0;
    color: #dce8f9;
    text-style: bold;
}

Input, Select {
    height: 3;
    margin: 0;
    border: round #4b627f;
    background: #101a2b;
    color: #dce8f9;
}

Input:focus, Select:focus {
    border: round #5aa7ff;
}

.field-hint {
    height: auto;
    margin: 0 0 1 0;
}

#buttons {
    width: 100%;
    height: 3;
    margin: 1 0;
    align: left middle;
}

Button {
    min-width: 0;
    width: auto;
    height: 3;
    margin: 0 1 0 0;
    padding: 0 2;
    border: round #4b678a;
    background: #1a2a41;
    color: #dce8f9;
    text-style: bold;
}

Button:hover {
    background: #284363;
}

#configure {
    border: round #58a8ff;
    background: #176eb8;
}

#configure:hover {
    background: #258bd9;
}

#details {
    min-height: 5;
}

#status {
    min-height: 5;
    padding: 1;
    border: round #4fd9c3;
    background: #182a43;
    color: #4fd9c3;
}

#config-card {
    height: auto;
    padding: 0 1;
}

#config-path {
    color: #dce8f9;
}

"""
