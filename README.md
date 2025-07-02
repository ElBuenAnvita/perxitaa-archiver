# perxitaa-archiver
A set of Python scripts designed to download, process, and archive Twitch VODs (with chat!) to the Internet Archive. What started as a simple favor became a surprisingly complex and fun personal project.

## Story behind
So, back in 2023, my gf at the time was a huge fan of the streamer Perxitaa, especially his GTA Roleplay series. Because of her studies, she'd often miss the live streams and would fall behind on the storyline. To help her out, I started manually downloading the VODs before they were deleted by Twitch after the 60-day mark.

Naturally, I thought, "I can automate this." So, I wrote a script using the awesome TwitchDownloaderCLI to do the job. But then came the first feature request: "It's not the same without the chat!"

...And that's how this simple downloader spiraled into a full-blown archiving project. It ended up fetching the VOD, downloading the chat, rendering the chat as a video, merging it with the VOD, and finally, uploading the whole thing to the Internet Archive for permanent storage (after realizing my Google Drive wouldn't cut it).

I'm pretty sure she never [watched most of them](https://archive.org/details/@katanaanvi), but hey, it was an interesting project to build!

## What It Does
This set of scripts automates the entire process of archiving a Twitch VOD:

* **📥 Add to Queue:** A script (`add_vod.py`) to fetch VOD details from the Twitch GQL API and add it to a master list (`Streams Perxitaa.txt`) with a `[--PENDNG--]` status.

* **✂️ Clip VODs:** You can specify start and end times to download only a specific segment of a VOD. This was useful for some VODs when Perxitaa played multiple games in the same stream.

* **⚙️ Process Queue:** The main script (`process_one_queue.py`) fetches the next pending VOD from the list and handles the entire workflow.

* **📹 Download VOD & Chat:** It uses TwitchDownloaderCLI to download the video (in the best available 720p quality) and its corresponding chat log.

* **🎨 Render Chat:** The chat log (`.json`) is rendered into a separate video file.

* **🎞️ Merge:** The VOD and the rendered chat video are merged side-by-side into a single file using FFmpeg.

* **☁️ Upload to Internet Archive:** The final merged video is automatically uploaded to a new item on the Internet Archive with generated metadata (title, description, date, etc.).

* **📝 Status Tracking:** The script updates the VOD's status in the master list as it moves through the process: `[--QUEUED--]`, `[--FINVOD--]`, `[--UPLDIN--]`, and finally `[--UPLDED--]`.

## How It Works (The Workflow)
The whole process is managed through a central text file and three main scripts.

### 1. **The Master List: `Streams Perxitaa.txt`**
This file is the brain of the operation. Each line represents a VOD and follows a specific format:

**Format with cut:**
```
[STATUS] [SHOW_CODE][#EPISODE][TIMESTAMP][DURATION] EPISODE_NAME - VOD_ID(START_TIME-END_TIME)
```

_Example:_
```
[--PENDNG--] [INF][#24.0][1678839354][05:15:30] El principio del fin - 1765471499(0h15m30s-05h31m00s)
```

### 2. The Scripts

#### `add_vod.py`
This is what you run to add a new VOD to the queue. It will ask for:

* The Twitch VOD ID.
* A 3-letter "show code" (e.g., INF for Infames RP).
* The episode number.
* A custom title for the episode.
* Whether the VOD needs to be cut, and the start/end times if so.

It then fetches the VOD data, saves a thumbnail for reference, formats the line, and appends it to `Streams Perxitaa.txt`.

#### `process_one_queue.py`
This is the main workhorse. When you run it, it finds the first VOD in `Streams Perxitaa.txt` with the `[--PENDNG--]` status and does everything:

* Changes status to `[--QUEUED--]`.
* Downloads the VOD and Chat.
* Renders the Chat.
* Merges the VOD and Chat.
* Changes status to `[--FINVOD--]`.
* Uploads the final file to the Internet Archive.
* Changes status to `[--UPLDIN--]` during the upload and `[--UPLDED--]` upon completion.

#### `upload_to_ia.py`
A utility script to manually re-trigger the upload for a VOD that is marked as `[--UPLDIN--]`. This is useful if the main script was interrupted during an upload.

## Requirements & Setup
You'll need a few things to get this running.

### Dependencies
* **Python 3.x**
* **TwitchDownloaderCLI:** The core tool for downloading. Download the latest release from [their GitHub page](https://github.com/lay295/TwitchDownloader/releases).
* **FFmpeg:** Required for merging the final videos. You must have it installed and available in your system's PATH.
* **Python Libraries:** You can install them via pip:

```bash
pip install requests termcolor internetarchive-api Pillow winsound
```

### Configuration
Before running, you must update the hardcoded paths inside the scripts:

1. `process_one_queue.py`, `add_vod.py`, `upload_to_ia.py`:
    * `CLI_PATH`: Set this to the full path of your `TwitchDownloaderCLI.exe`.
    * `TEXT_FILE`: The full path to your `Streams Perxitaa.txt` master list.

2. `add_vod.py`:
    * It uses an Arial font from `C:\WINDOWS\FONTS\ARIAL.TTF` to number thumbnails. You may need to change this path if you're not on Windows or if the font is located elsewhere.

### Folder Structure
The scripts expect a specific folder structure to save the output files. Follow the current folder structure that has this repository and run the scripts from the `.bat` files, or change the location of the file `shows.json` since the scripts expect this file to be relative from where it was executed.

### `shows.json` File
You need to have a `shows.json` file to map the 3-letter show codes to their full names for the Internet Archive metadata.

### Internet Archive Account
The `internetarchive` library requires you to be logged in. Run this command once in your terminal and follow the prompts:

```Bash
ia configure
```

## Usage Guide
1. **Setup:** Complete the configuration steps above.

2. **Queue a VOD:** Run `@ Añadir directo.bat` or `python add_vod.py` and answer the prompts to add a VOD to your `Streams Perxitaa.txt` file.

3. **Process the Queue:** Run `@ Procesar siguiente en espera.bat` or `python process_one_queue.py`. The script will pick up the first pending VOD and start its work. Grab a coffee, since this will take a while.

3. **Repeat:** Once a VOD is done, the script will make your pc beep (if Windows, else you might want to delete some code) and ask if you want to continue with the next one in the queue.

4. **(Optional) Retry Upload:** If an upload fails, run `@ Subir a IA inconclusos.bat` or `python upload_to_ia.py` to find the stuck VOD and re-initiate the upload process.

Enjoy your perfectly archived VODs!

# ⚠️ Warning: PROJECT ARCHIVED
This project is no longer actively maintained as of **2023**. Due to the time elapsed, it is very likely that parts of the code, especially those interacting with the Twitch API and `TwitchDownloaderCLI`, are broken.

You are free to fork this repository to repair, update or adapt it to your own needs.