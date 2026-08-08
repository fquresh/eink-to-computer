# boox-to-computer

Handwritten notes from an ONYX Boox e-ink tablet, transcribed by a vision model and filed as searchable Markdown in Obsidian.

Scribble on the tablet, export the note as a PDF, click one button, and a transcribed Markdown note with the original page images appears in your Obsidian vault.

## How it works

```
Boox Notes app --(export PDF)--> ~/boox-inbox (your computer)
  --> boox-to-computer
    --> render pages to images (PyMuPDF)
    --> transcribe with a vision model (Gemini Flash free tier)
    --> write Markdown + page images into your Obsidian vault
```

The pipeline never touches the tablet's internal stroke database (root-only, and blocked by Android scoped storage anyway).
It uses the Notes app's own PDF export, which is the stable, supported seam.

Every PDF is SHA-256 hashed and recorded in a state file, so re-runs never duplicate notes or burn OCR quota.
The original page image is always embedded above the transcription, so nothing is lost even if OCR misreads something.

## Quick start

### 1. Install

```sh
git clone https://github.com/fquresh/boox-to-computer.git
cd boox-to-computer
uv sync
cp config.example.yaml config.yaml
```

Edit `config.yaml`: set `vault` to your Obsidian vault path and paste your Gemini API key.
Get a free key at https://aistudio.google.com -> "Get API key" -> "Create API key in new project".
You can also set the `GEMINI_API_KEY` environment variable instead of putting it in the file.
`config.yaml` is gitignored, so the key never gets committed.

### 2. Export a note from your Boox

Open a note in the Boox Notes app -> Share & Export -> PDF -> save to Google Drive, or transfer via USB/BooxDrop/AirDrop.
Drop the PDF into the folder you set as `inbox` in `config.yaml` (default: `~/boox-inbox`).

### 3. Click the button

```sh
uv run boox-to-computer gui
```

A web page opens with a single "Process Notes" button.
Click it, and your note lands in Obsidian as searchable Markdown.

On macOS, double-click the bundled `Boox to Computer.app` to launch the GUI without a terminal.

## Usage

```sh
# web UI (one-button processor, opens in browser)
uv run boox-to-computer gui

# process all pending PDFs in the inbox, then exit
uv run boox-to-computer sync

# continuous: watch the inbox and process PDFs as they arrive
uv run boox-to-computer watch

# process a single PDF
uv run boox-to-computer process "/path/to/exported note.pdf"

# show processed notes and OCR usage
uv run boox-to-computer status
```

## Transport options

How PDFs get from the tablet to your computer's inbox folder:

| method | how | automation |
|---|---|---|
| **Manual export** (simplest) | Share & Export -> PDF -> Google Drive / USB / AirDrop -> drop in inbox folder | per-note |
| **Google Drive sync** | Boox Notes -> Settings -> cloud sync -> Google Drive, folder `boox-inbox` | automatic (needs Google Drive for desktop) |
| **WebDAV** | Run [dufs](https://github.com/sigoden/dufs) on your computer, point Boox Notes WebDAV sync at it | automatic, fully local |
| **Syncthing** | Syncthing on both ends, sync the `/note/` folder | automatic, fully local |

## OCR backends

| backend | cost | quality | privacy |
|---|---|---|---|
| `gemini` (default) | $0 within free tier (250 pages/day) | excellent on handwriting | cloud |
| `mistral` | ~$0.05 per 100 pages | excellent, purpose-built OCR | cloud |
| `local` | $0, runs on your machine | good, needs 8GB+ free RAM | fully local |

For `local`: `brew install ollama && ollama pull qwen3-vl`, then set `backend: local` in `config.yaml`.

## Where notes land

`<vault>/Handwritten Boox Notes/<notebook>/<note-name>.md` with page images in an `attachments/` subfolder next to each note.
The vault's own sync (Obsidian Sync, iCloud, git, ...) carries the notes to your other devices.

## Requirements

- Python 3.11+ (managed automatically by [uv](https://docs.astral.sh/uv/))
- An Obsidian vault (just a folder of Markdown files)
- A Gemini API key (free) or another OCR backend

## License

MIT
