import gradio as gr
from gradio_canvas_component import CanvasComponent

example_data = {"name": "Podcast Generator", "nodes": [], "edges": []}

demo = gr.Interface(
    lambda x: x,
    CanvasComponent(value=example_data),
    CanvasComponent(),
)


if __name__ == "__main__":
    demo.launch()
