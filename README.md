# boox-to-computer

Handwritten notes from an ONYX Boox tablet, automatically transcribed by a vision model and filed as searchable Markdown in Obsidian.

## How it works

```
Boox Notes app --(native WebDAV sync, PDF)--> ~/boox-inbox (this Mac)
  --> boox-to-computer watch
    --> render pages (PyMuPDF)
    --> transcribe (Gemini 2.5 Flash free tier)
    --> write Markdown + page images into your Obsidian vault
```

The pipeline never touches the tablet's internal stroke database (root-only, and blocked by Android scoped storage anyway).
It uses the Notes app's own PDF export, which is the stable, supported seam.

Every PDF is SHA-256 hashed and recorded in a state file, so re-syncs and re-runs never duplicate notes or burn OCR quota.
The original page image is always embedded above the transcription, so nothing is lost even if OCR misreads something.

## Setup

### 1. Install

```sh
uv sync
cp config.example.yaml config.yaml
```

Edit `config.yaml`: set `vault` to your Obsidian vault path and paste your Gemini API key.
Get a free key at https://aistudio.google.com -> "Get API key".
You can also set the `GEMINI_API_KEY` environment variable instead of putting it in the file.
`config.yaml` is gitignored, so the key never gets committed.

### 2. One-time tablet setup

On the Boox (Note Air, firmware 3.1+):

1. Open the Notes app -> hamburger menu -> Settings.
2. Enable automatic PDF export of notes if available ("auto-generate PDF on close").
3. In Notes sync settings, choose **WebDAV** as the cloud provider.
4. Enter the WebDAV URL of the inbox server (below), plus any username/password you configured.
5. Set sync to happen on change (or a short interval).

### 3. Inbox server on the Mac

Any WebDAV server pointed at `~/boox-inbox` works.
The simplest is [dufs](https://github.com/sigoden/dufs):

```sh
brew install dufs
dufs --allow-upload --allow-mkdir ~/boox-inbox --bind 0.0.0.0 --port 5000
```

Find your Mac's LAN IP (`ipconfig getifaddr en0`) and use `http://<mac-ip>:5000` as the WebDAV URL on the tablet.
Alternatives: Syncthing on both ends, or the Boox's native Dropbox sync with the Dropbox folder as `inbox`.

### 4. Run

```sh
# one-off: process everything currently in the inbox
uv run boox-to-computer sync

# continuous: watch the inbox forever
uv run boox-to-computer watch

# test a single file
uv run boox-to-computer process "/path/to/exported note.pdf"

# see what has been processed and today's free-tier usage
uv run boox-to-computer status
```

To run the watcher at login, create a launchd agent or just leave `watch` running in a tmux window.

## Where notes land

`<vault>/Handwritten Boox Notes/<notebook>/<note-name>.md` with page images in an `attachments/` subfolder next to each note.
The vault's own sync (Obsidian Sync, iCloud, git, ...) carries the notes to your other devices.

## OCR backends

| backend | cost | quality | privacy |
|---|---|---|---|
| `gemini` (default) | $0 within free tier (250 pages/day) | excellent on handwriting | cloud |
| `mistral` | ~$0.05 per 100 pages | excellent, purpose-built OCR | cloud |
| `local` | $0, runs on this Mac | good, needs 8GB+ free RAM | fully local |

For `local`: `brew install ollama && ollama pull qwen3-vl`, then set `backend: local` in `config.yaml`.
