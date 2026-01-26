from daggr import GradioNode

from gradio_client import Client, handle_file


glm_image = GradioNode(
    "hf-applications/Z-Image-Turbo"
    api_name="/generate_image"
    inputs={
        "prompt": gr.Textbox(label="Prompt"),  # An input node is created for the prompt
        "height": 1024,  # Fixed value (does not appear in the canvas)
        "width": 1024,  # Fixed value (does not appear in the canvas)
        "seed": random.random,  # Functions are rerun every time the workflow is run (not shown in the canvas)
    },
    outputs={
        "image": gr.Image(label="Image"),  # Display the generated image in an Image component
    },
)

background_remover = GradioNode(
    "hf-applications/background-removal"
    api_name="/infer"
    inputs={
        "image": glm_image.image,  # Connect the output of the GLM Image node to the input of the background remover node
    },
    outputs={
        "image": gr.Image(label="Final Image"),  # Display the final result in an Image component
    },
)

graph = Graph(name="Transparent Background Image Generator", nodes=[glm_image, background_remover])

graph.launch()