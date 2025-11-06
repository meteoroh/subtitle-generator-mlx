# Subtitle Generator MLX

This project provides a Python script to automatically generate subtitles for audio and video files. It can also translate the subtitles into different languages. The script is optimized for Apple Silicon devices using the [MLX framework](https://github.com/ml-explore/mlx).

## Features

-   **Fast Transcription:** Utilizes `mlx-whisper` for efficient audio transcription on Apple Silicon.
-   **Translation:** Can translate subtitles into any target language using local LLMs with `lmstudio`.
-   **Subtitle Generation:** Creates subtitle files in `.srt` format.
-   **Batch Processing:** Can process multiple files at once.

## Requirements

-   Apple Silicon Mac
-   Python 3.13+
-   [uv](https://github.com/astral-sh/uv)
-   [LM Studio](https://lmstudio.ai/)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/yusung/subtitle_generator
    cd subtitle_generator
    ```

2.  **Install uv:**

    ```bash
    brew install uv
    ```

3.  **Install the dependencies:**

    ```bash
    uv sync
    ```

## Usage

1.  **Place your audio or video files** in a directory.

2.  **Modify the `main.py` script** to point to your files and set the desired options:

    ```python
    if __name__ == '__main__':
        # Initialize the generator with a Whisper model and an optional translator model
        generator = SubtitleGenerator('whisper-large-v3-mlx', 'google/gemma-3-12b')

        # --- Examples ---

        # 1. Transcribe a single file and save the transcription output as a JSON file
        # generator.transcribe('/path/to/your/audio.mp3', source_language='ja', log=True)

        # 2. Generate translated subtitles for a single file
        # generator.generate('/path/to/your/audio.mp3', translation=True, source_language='ja', target_language='en', log=True)

        # 3. Generate subtitles in the original language for a single file
        # generator.generate('/path/to/your/audio.mp3', source_language='ja')

        # 4. Generate translated subtitles for all mp4 files in a directory
        # generator.generate_all('/path/to/your/*.mp4', translation=True, source_language='ja', target_language='en')
    ```

3.  **Run the script:**

    ```bash
    uv run python main.py
    ```

    The generated subtitle files will be saved in the `results` directory.

### Parameters

Here are the parameters for the methods in the `SubtitleGenerator` class:

#### `__init__`

-   `whisper_model` (essential): The name of the Whisper model to use for transcription (e.g., `'whisper-large-v3-mlx'`).
-   `translator_model` (optional): The name of the translator model to use for translation (e.g., `'google/gemma-3-12b'`).

#### `transcribe`

-   `path` (essential): The path to the audio or video file.
-   `source_language` (optional): The source language of the audio. If not provided, it will be auto-detected.
-   `log` (optional): If `True`, it saves the raw transcription output as a JSON file in the `results` directory and sets the whisper model's `verbose` option to `True`, displaying the text being decoded to the console. Defaults to `True`.

#### `generate`

-   `path` (essential): The path to the audio or video file.
-   `translation` (optional): Whether to translate the subtitles. Defaults to `False`.
-   `source_language` (optional): The source language of the audio. If not provided, it will be auto-detected.
-   `target_language` (essential if `translation=True`): The target language for the translation.
-   `log` (optional): If `True`, it saves the raw transcription output as a JSON file in the `results` directory and sets the whisper model's `verbose` option to `True`, displaying the text being decoded to the console. Defaults to `False`.

#### `generate_all`

-   `path` (essential): A glob pattern for the files to process (e.g., `'/path/to/your/*.webm'`).
-   `translation` (optional): Whether to translate the subtitles. Defaults to `False`.
-   `source_language` (optional): The source language of the audio. If not provided, it will be auto-detected.
-   `target_language` (essential if `translation=True`): The target language for the translation.
-   `log` (optional): If `True`, it saves the raw transcription output as a JSON file in the `results` directory and sets the whisper model's `verbose` option to `True`, displaying the text being decoded to the console. Defaults to `False`.

## Models

This script uses two types of models:

1.  **Whisper Model:** For transcription. The model is downloaded from the Hugging Face Hub via `mlx-community`. The default model is `whisper-large-v3-mlx`. You can find more models [here](https://huggingface.co/collections/mlx-community/whisper).

2.  **Translator Model:** For translation. This script uses `lmstudio` to run a local LLM for translation. You need to have `lmstudio` installed and the desired model downloaded. The default model is `google/gemma-3-12b`.

## License

This project is licensed under the MIT License.