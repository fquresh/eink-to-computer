# eink-to-computer

Handwritten notes from any e-ink tablet, transcribed by a vision model and filed as searchable Markdown in Obsidian.

Works with Boox, reMarkable, Supernote, Kindle Scribe, and any device that can export notes as PDF.

## How it works

```
E-ink tablet --(export PDF)--> inbox folder (your computer)
  --> eink-to-computer
    --> render pages to images
    --> transcribe with a vision/OCR model
    --> write Markdown + page images into your Obsidian vault
```

Every PDF is SHA-256 hashed and recorded in a state file, so re-runs never duplicate notes or burn OCR quota.
The original page image is always embedded above the transcription, so nothing is lost even if OCR misreads something.

## Quick start

```sh
git clone https://github.com/fquresh/eink-to-computer.git
cd eink-to-computer
uv sync
cp config.example.yaml config.yaml
```

Edit `config.yaml`: set `vault` to your Obsidian vault path and choose an OCR backend (see below).

Export a note from your e-ink tablet as a PDF and drop it into your inbox folder.

```sh
# launch the web UI (one-button processor, opens in browser)
uv run eink-to-computer gui

# or process from the command line
uv run eink-to-computer sync
```

On macOS, double-click the bundled `E-Ink to Computer.app` to launch the GUI without a terminal.

## Choosing an OCR model

The backend needs to be a **vision-capable model** that can read handwriting from page images.
Any OCR or vision-language model that accepts images and outputs text will work.

### Cloud (default: Gemini, free)

| backend | cost | setup |
|---|---|---|
| `gemini` | $0 within free tier (250 pages/day) | API key from https://aistudio.google.com |
| `mistral` | ~$0.05 per 100 pages | API key from https://console.mistral.ai |

Set `backend: gemini` in `config.yaml` and paste your API key.
The free tier covers tens of pages per day with no payment info required.

### Fully local (no cloud, no API key)

Set `backend: local` in `config.yaml` and run a vision model through [Ollama](https://ollama.com):

```sh
brew install ollama
ollama pull qwen3-vl
```

Any vision-capable model in Ollama's library works.
Models improve over time, so check [ollama.com/search?q=vision](https://ollama.com/search?q=vision) for current options.
A few examples (not an exhaustive list):

- `qwen3-vl` - general vision-language model, decent on handwriting
- `llama3.2-vision` - Meta's vision model
- Any future model with image input and text output

Local models need 8GB+ of free RAM and run slower than cloud, but nothing leaves your machine.

## Getting PDFs from your tablet

Any method that gets a PDF into your inbox folder works:

- **Manual:** Share & Export -> PDF -> USB / AirDrop / cloud drive -> drop in inbox
- **Cloud sync:** Many e-ink tablets support Google Drive, Dropbox, or WebDAV sync. Point the sync folder at your inbox.
- **WebDAV:** Run a local WebDAV server like [dufs](https://github.com/sigoden/dufs) and configure your tablet to sync to it.

## Commands

```sh
eink-to-computer gui       # web UI with one-button processing
eink-to-computer sync      # process all pending PDFs, then exit
eink-to-computer watch     # watch inbox and process PDFs as they arrive
eink-to-computer process <pdf>  # process a single PDF
eink-to-computer status    # show processed notes and OCR usage
```

## Where notes land

`<vault>/Handwritten Notes/<notebook>/<note-name>.md` with page images in an `attachments/` subfolder.
The vault's own sync (Obsidian Sync, iCloud, git, etc.) carries notes to your other devices.

## Requirements

- Python 3.11+ (managed by [uv](https://docs.astral.sh/uv/))
- An Obsidian vault
- An OCR backend (Gemini API key, Mistral API key, or a local model via Ollama)

## License

MIT
