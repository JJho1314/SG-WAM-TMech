#!/usr/bin/env sh
set -eu

if [ "$(uname -s 2>/dev/null || true)" = "Darwin" ] && [ -x /usr/libexec/path_helper ]; then
  eval "$(/usr/libexec/path_helper -s)"
fi

# Prepend known TeX Live locations to PATH. Later matches end up earlier in
# PATH, so list the most-preferred install LAST. On this machine the working
# full TeX Live lives in the user's home ($HOME/texlive/2026/bin/x86_64-linux),
# so it is listed last to win. The conda-forge texlive-core in /opt/miniconda3
# is incomplete (no format files, missing packages) and must NOT shadow the
# real install, so it is listed earlier (lower priority) as a mere fallback.
for texbin in \
  /Library/TeX/texbin \
  /usr/local/texlive/2026/bin/universal-darwin \
  /usr/local/texlive/*/bin/universal-darwin \
  /usr/local/texlive/*/bin/* \
  /opt/miniconda3/bin \
  "$HOME"/texlive/*/bin/*; do
  if [ -d "$texbin" ]; then
    PATH="$texbin:$PATH"
  fi
done
export PATH

if ! command -v latexmk >/dev/null 2>&1; then
  cat >&2 <<'EOF'
Error: latexmk was not found.

Install a LaTeX distribution and rebuild. On this Linux machine, TeX Live is
provided via miniconda at /opt/miniconda3/bin. If it is missing, install a
LaTeX toolchain (e.g. `conda install -c conda-forge texlive-core latexmk`
into that environment, or a system TeX Live), then reopen VS Code so LaTeX
Workshop picks up the updated PATH. This wrapper prepends the known TeX Live
locations to PATH for LaTeX Workshop builds.
EOF
  exit 127
fi

exec latexmk "$@"
