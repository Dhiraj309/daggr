# daggr

A Python package.

## Installation

This package requires [Python 3.10 or higher](https://www.python.org/downloads/). Install with `pip`:

```bash
pip install daggr
```

or with `uv`:

```bash
uv pip install daggr
```

## Usage

daggr allows you to build complex pipelines by connecting Gradio apps together.

### Basic Example

```python
from daggr import Workflow, GradioNode

# Create a workflow
workflow = Workflow(name="My Pipeline")

# Add Gradio app nodes (using Space IDs or URLs)
node1 = GradioNode(src="username/space-name", name="First App")
node2 = GradioNode(src="username/another-space", name="Second App")

# Add nodes to workflow
workflow.add_node(node1)
workflow.add_node(node2)

# Connect nodes (explicit output-to-input mapping)
workflow.connect(
    source=node1,
    source_output="0",  # First output of node1
    target=node2,
    target_input="text"  # Input parameter name of node2
)

# Mark interaction points where users can provide input
workflow.mark_interaction(node1)

# Launch the generated UI
workflow.launch()
```

### Test App

Run the included test app:

```bash
python test_app.py
```

This creates a simple pipeline connecting a text generator to a text summarizer.

## Development

To set up the package for development, clone this repository and run:

```bash
pip install -e ".[dev]"
```

## Testing

Run tests with:

```bash
pytest
```

## Code Formatting

Format code using Ruff:

```bash
ruff check --fix --select I && ruff format
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License
