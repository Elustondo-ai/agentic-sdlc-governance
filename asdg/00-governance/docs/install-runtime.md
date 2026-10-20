# User-local installer runtime

## Installer behavior

Python 3.9+ standard library; no sudo, downloads, package installs, registry or account login.
Creates two managed Python launchers: `~/.local/bin/asdg` and `~/.local/bin/asdg`.
The qualified command avoids depending on a globally unique bare asdg name.
An existing `asd` command is left untouched; rerun this installer to add `asdg`.
Records the Python interpreter and provider checkout in `~/.config/asdg/installation.json`.
Updates zsh `.zprofile` and `.zshrc`, respecting a HOME-contained ZDOTDIR.
For bash, updates `.bashrc` and the first existing `.bash_profile`, `.bash_login`, or `.profile`.
If none exists, creates `.bash_profile`; never hides an existing lower-priority login file.
Appends an identified PATH block only once; changed files have byte-exact backups in the config folder.
Never edits system folders or rewrites unrelated shell configuration.
Colliding executables, edited managed blocks, unsupported shells and symlink destinations stop the install.
Existing shell aliases/functions may shadow PATH; inspect `command -v asdg` in that shell.
An installer cannot export into its parent shell. A fresh terminal loads the saved PATH block.
For the current shell: `export PATH="$HOME/.local/bin:$PATH"`; restart VS Code when needed.
The launchers preserve the caller's directory and support checkout paths with spaces and quotes.
Root `asdg` imports `cli.main`; its `install` operation calls the Python installer directly.
Installed launchers re-execute root `asdg` with the recorded interpreter for reproducibility.
ASDG scripts use Python >= 3.9; application projects may use any language.


[Workflow and initialization](install-cli.md).
