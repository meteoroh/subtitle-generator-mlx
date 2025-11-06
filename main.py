import os
import glob
import time
import json
import mlx_whisper
import lmstudio as lms
from tqdm import tqdm


def format_time(start: float, end: float) -> str:
    def convert_time(seconds):
        hour = int(seconds // 3600)
        minute = int((seconds % 3600) // 60)
        second = int(seconds % 60)
        millisecond = int((seconds % 1) * 1000)
        return f'{hour:02}:{minute:02}:{second:02},{millisecond:03}'
    return f'{convert_time(start)} --> {convert_time(end)}'


class SubtitleGenerator:
    def __init__(self, whisper_model, translator_model=None):
        self.whisper_model = whisper_model
        self.translator_model = translator_model

    def transcribe(self, path, source_language=None, log=True):
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        filename = os.path.basename(path)
        start_time = time.perf_counter()

        output = mlx_whisper.transcribe(path, path_or_hf_repo=f'mlx-community/{self.whisper_model}', language=source_language,
                                        temperature=0.0, logprob_threshold=-0.04, no_speech_threshold=0.3, condition_on_previous_text=False, word_timestamps=True, hallucination_silence_threshold=1, verbose=log)

        end_time = time.perf_counter()
        print(f'Transcribed {filename} in {end_time - start_time:.1f}s')

        if log:
            json_file = os.path.splitext(filename)[0] + '.json'
            
            json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'results', json_file)
            os.makedirs(os.path.dirname(json_path), exist_ok=True)

            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=4, ensure_ascii=False)
                
                if log:
                    print(f'Transcription output saved to {json_path}')
            except Exception as e:
                print(f'Failed to save JSON output: {e}')

        return output

    def generate(self, path, translation=False, source_language=None, target_language=None, log=False):
        output = self.transcribe(path, source_language, log)
        segments = output['segments']
        source_language = output['language'] if source_language is None else source_language

        time_stamps = []
        texts = {}

        if translation:
            if not target_language:
                raise ValueError('Target language is required.')

            if not self.translator_model:
                raise RuntimeError('Translator model is required.')
            
            translator = lms.llm(self.translator_model)
            print('Translator model loaded.')

            srt_file = os.path.basename(path).split('.')[0] + f'.{target_language}.srt'
            previous_text_original = 'N/A'
            previous_text_translated = 'N/A'
            
            for segment in tqdm(segments, desc=f'Generating {srt_file}, translated from {source_language}'):
                if segment['id'] == len(segments) - 1:
                    next_text_original = 'N/A'
                else:
                    next_text_original = segments[segment['id'] + 1]['text']

                prompt = f'''
                You are a professional subtitle translator tasked with translating the `[Text to Translate]` from `{source_language}` into natural, fluent `{target_language}`. (ISO 639-1 language codes)
                
                ## Strict Rules
                1. Input Correction: The [Text to Translate] is from automated AI transcription and may contain inaccuracies or typos. If the text seems nonsensical or grammatically incorrect, infer the intended meaning and translate that corrected version.            
                2. Language Requirement: You MUST translate into `{target_language}`. Returning untranslated or partially translated text is unacceptable.         
                3. Tone & Register: Identify and match the speaker's original tone and style (formal, casual, slang, etc.). Use the [Context] segments to maintain continuity across subtitle breaks.
                4. Exception: Keep person names, brand names, and most proper nouns in their original form unless there is a widely-accepted localized version in `{target_language}`.
                5. Output Format: Return ONLY the translated text with no explanations, notes, pronunciations, or extra quotation marks.

                ## Context
                - Previous Segment (Original): {previous_text_original}
                - Previous Segment (Translated): {previous_text_translated}
                - Next Segment (Original): {next_text_original}

                ## Text to Translate
                {segment['text']}
                '''
                
                previous_text_original = segment['text']
                previous_text_translated = text = str(translator.respond(prompt)).strip()
                
                time_stamp = format_time(segment['start'], segment['end'])
                time_stamps.append(time_stamp)
                texts[time_stamp] = text
            
            translator.unload()
            
        else:
            srt_file = os.path.basename(path).split('.')[0] + f'.{source_language}.srt'
            for segment in tqdm(segments, desc=f'Generating {srt_file}'):
                text = segment['text'].strip()
                time_stamp = format_time(segment['start'], segment['end'])

                time_stamps.append(time_stamp)
                texts[time_stamp] = text

        result = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'results', srt_file)
        os.makedirs(os.path.dirname(result), exist_ok=True)

        with open(result, 'w', encoding='utf-8') as f:
            for i, time_stamp in enumerate(time_stamps, start=1):
                f.write(str(i) + '\n')
                f.write(time_stamp + '\n')
                f.write(texts[time_stamp] + '\n\n')


    def generate_all(self, path, translation=False, source_language=None, target_language=None, log=False):
        files = glob.glob(path)
        if not files:
            raise FileNotFoundError(path)

        for num, file in enumerate(files, start=1):
            print(f'[{num}/{len(files)}]')
            self.generate(file, translation=translation, source_language=source_language, target_language=target_language, log=log)


if __name__ == '__main__':
    generator = SubtitleGenerator('whisper-large-v3-mlx', 'google/gemma-3-12b')

    generator.transcribe('/path/to/your/audio.mp3', source_language='ja', log=True)
    # generator.generate('/path/to/your/video.mp4', translation=True, source_language='ja', target_language='en', log=True)
    # generator.generate_all('/path/to/your/*.webm', translation=True, source_language='ja', target_language='en', log=False)
