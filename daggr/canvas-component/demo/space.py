
import gradio as gr
from app import demo as app
import os

_docs = {'CanvasComponent': {'description': 'A canvas component for displaying DAG-based workflows with nodes and edges.', 'members': {'__init__': {'value': {'type': 'dict | Callable | None', 'default': 'None', 'description': "Default graph data with 'name', 'nodes', and 'edges' keys."}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'The label for this component.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'If True, will display label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, will place the component in a container.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'Relative size compared to adjacent Components.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'Minimum pixel width.'}, 'visible': {'type': 'bool | "hidden"', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string for the HTML DOM id.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings for CSS classes.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not be rendered.'}, 'height': {'type': 'int | str | None', 'default': '"100vh"', 'description': 'The height of the canvas.'}}, 'postprocess': {'value': {'type': 'dict | None', 'description': None}}, 'preprocess': {'return': {'type': 'dict | None', 'description': None}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the CanvasComponent changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the CanvasComponent.'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'CanvasComponent': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_canvas_component`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

makes a canvas to display a DAG
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_canvas_component
```

## Usage

```python
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

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `CanvasComponent`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["CanvasComponent"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["CanvasComponent"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.



 ```python
def predict(
    value: dict | None
) -> dict | None:
    return value
```
""", elem_classes=["md-custom", "CanvasComponent-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          CanvasComponent: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
