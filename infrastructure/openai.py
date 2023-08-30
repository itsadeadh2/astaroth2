import os

import openai


class OpenAi:

    @staticmethod
    def ask(prompt, model="gpt-3.5-turbo"):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        messages = [{"role": "user", "content": prompt}]

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0,
        )

        return response.choices[0].message["content"]

    @staticmethod
    def analize_video(transcript: str):
        with open('infrastructure/default_video_prompt.txt', 'rb') as file:
            analysis_prompt = file.read().decode('utf-8')
        full_prompt = analysis_prompt + '\n'
        full_prompt += transcript
        return OpenAi.ask(full_prompt, model='gpt-4')
