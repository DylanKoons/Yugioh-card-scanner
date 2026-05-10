# Yu-Gi-Oh Card Scanner

A real-time card scanner that uses your USB camera to detect set codes on Yu-Gi-Oh cards and automatically looks them up in the YGOProDeck database.

## Features

- **Real-time Camera Feed**: Live video from your USB camera
- **OCR Text Extraction**: Automatically reads set codes from card images
- **Live API Lookup**: Searches YGOProDeck database for card information
- **Multi-card Scanning**: Scan multiple cards in succession
- **Detailed Card Info**: Displays name, type, ATK/DEF, level, rarity, and description

## Setup

### Requirements

- Python 3.8+
- USB camera/webcam

### Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

The first time you run the app, it will download the OCR model (around 100MB), which may take a few minutes.

## Usage

1. Position your USB camera to view the card
2. Run the application:
```bash
python main.py
```

3. Click "Start Scanning" button
4. Show the set code part of the card to the camera
5. The app will automatically detect the set code and look up card information
6. Card details will appear in the results panel

## How It Works

1. **Camera Capture** (`camera.py`): Continuously captures frames from your USB camera
2. **OCR Processing** (`ocr.py`): Uses EasyOCR to extract text from the card image and identifies set code patterns
3. **API Lookup** (`api.py`): Searches the YGOProDeck API for matching cards
4. **GUI Display** (`main.py`): Tkinter-based interface showing live feed and results

## Set Code Format

Yu-Gi-Oh set codes follow patterns like:
- `BP01-EN123` (Burst of Destiny - English)
- `DIFO-JP001` (Burst of Destiny - Japanese)
- `PHNI-EN001` (Photon Hypernova - English)

The app automatically recognizes these patterns.

## Tips for Best Results

- Ensure good lighting on the card
- Position the camera so the set code is clearly visible
- Keep the card relatively steady for a moment
- The app will skip duplicate scans to avoid repeated lookups

## Troubleshooting

- **Camera not detected**: Check if your camera is properly connected and not in use by another app
- **OCR not finding set codes**: Ensure the set code is clearly visible and well-lit
- **API lookup failing**: Check your internet connection
