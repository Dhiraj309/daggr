import gradio as gr

from daggr import GradioNode

voice_description = gr.Textbox(
    label="Host Voice Description",
    value="Deep British voice that is very professional and authoritative...",
    lines=3,
)

text_to_speak = gr.Textbox(
    label="Text to Speak",
    value="Hi! I'm the host of podcast. It's going to be a great episode!",
)

qwen_voice = GradioNode(
    space_or_url="Qwen/Qwen3-TTS",
    api_name="/generate_voice_design",
    inputs={
        "voice_description": textbox,
        "language": "Auto",
        "text": text_to_speak,
    },
    outputs={
        "audio": gr.Audio(label="Host Voice"),
        "status": None,
    },
)

maya_voice = GradioNode(
    space_or_url="maya-research/maya1",
    api_name="/generate_speech",
    inputs={
        "preset_name": "Male American",
        "description": voice_description,
        "text": text_to_speak,
        "temperature": 0.4,
        "max_tokens": 1500,
    },
    outputs={
        "audio": gr.Audio(label="Host Voice"),
        "status": None,
    },
)


from gradio_client import Client

client = Client("")
result = client.predict(
    preset_name="Male American",
    description="Realistic male voice in the 20s age with a american accent. High pitch, raspy timbre, brisk pacing, neutral tone delivery at medium intensity, viral_content domain, short_form_narrator role, neutral delivery",
    text="And of course, the so-called easy hack didn't work at all.  What a surprise. <sigh>",
    temperature=0.4,
    max_tokens=1500,
    api_name="/",
)
print(result)


graph = Graph(
    name="Voice Designing Comparator",
    nodes=[],
)

graph.launch()
