# Daggr API Proposals: Scatter/Gather & Workflow Definition

We're considering two different API styles for daggr. This document outlines both approaches for team feedback.

---

## The Problem

We need an API that supports:
1. **Scatter**: Run a node multiple times over a list of inputs (e.g., generate audio for each line of dialogue)
2. **Gather**: Collect outputs from scattered executions back into a list
3. **Clean workflow definition**: Make it easy to define complex DAGs with minimal boilerplate

---

## Option A: Explicit Node-Based API (Current)

Nodes are defined explicitly as objects, connected via port references, and registered with a Graph.

### Example: Podcast Generator

```python
import gradio as gr
from daggr import FnNode, GradioNode, Graph, InferenceNode

# Define nodes explicitly
host_voice = GradioNode(
    space_or_url="abidlabs/tts",
    api_name="/generate_voice_design",
    inputs={
        "voice_description": gr.Textbox(
            label="Host Voice Description",
            value="Deep British voice that is very professional...",
            lines=3,
        ),
        "language": "Auto",
        "text": "Hi! I'm the host of the podcast.",
    },
    outputs={
        "audio": gr.Audio(label="Host Voice"),
        "status": gr.Text(visible=False),
    },
)

guest_voice = GradioNode(
    space_or_url="abidlabs/tts",
    api_name="/generate_voice_design",
    inputs={
        "voice_description": gr.Textbox(
            label="Guest Voice Description",
            value="Energetic, friendly young voice...",
            lines=3,
        ),
        "language": "Auto",
        "text": "Hi! I'm the guest. Super excited to be here!",
    },
    outputs={
        "audio": gr.Audio(label="Guest Voice"),
        "status": gr.Text(visible=False),
    },
)

def generate_dialogue(topic: str, host_voice: str, guest_voice: str):
    dialogue = [
        {"voice": host_voice, "text": "Welcome to today's episode!"},
        {"voice": guest_voice, "text": "Thanks for having me!"},
    ]
    html = "<p>Dialogue generated...</p>"
    return dialogue, html

dialogue = FnNode(
    fn=generate_dialogue,
    inputs={
        "topic": gr.Textbox(label="Topic", value="AI in healthcare..."),
        "host_voice": host_voice.audio,      # Port reference
        "guest_voice": guest_voice.audio,    # Port reference
    },
    outputs={
        "json": gr.JSON(label="Dialogue", visible=False),
        "html": gr.HTML(label="Script"),
    },
)

# SCATTER: .each accessor signals "run once per item"
samples = InferenceNode(
    model="ResembleAI/chatterbox",
    inputs={
        "audio_prompt": dialogue.json.each["voice"],  # Extract "voice" from each item
        "text": dialogue.json.each["text"],           # Extract "text" from each item
    },
    outputs={
        "audio": gr.Audio(label="Sample"),
    }
)

def combine_audio(clips: list[str]) -> str:
    return clips[0] if clips else None

# GATHER: .all() collects scattered outputs into a list
full_audio = FnNode(
    fn=combine_audio,
    inputs={
        "clips": samples.audio.all(),  # Gather all audio outputs
    },
    outputs={
        "audio": gr.Audio(label="Full Episode"),
    },
)

# Register all nodes with graph
graph = Graph(
    name="Podcast Generator",
    nodes=[host_voice, guest_voice, dialogue, samples, full_audio]
)

graph.launch()
```

### Scatter/Gather API

```python
# Scatter: .each property + optional key access
dialogue.json.each           # Scatter the whole list
dialogue.json.each["text"]   # Scatter and extract "text" from each item

# Gather: .all() method
samples.audio.all()          # Collect all outputs into a list
```

### Pros
- **Explicit**: Every node and connection is visible
- **Debuggable**: Easy to inspect individual nodes, see the graph structure
- **Flexible**: Can build graphs programmatically, conditionally add nodes
- **No magic**: What you see is what you get

### Cons
- **Verbose**: Lots of boilerplate for simple workflows
- **Repetitive**: Similar patterns repeated (inputs/outputs dicts everywhere)
- **Node list**: Must remember to add all nodes to the Graph

---

## Option B: Prefect-Style Decorator API

Workflows are defined as decorated Python functions. The framework traces execution to build the DAG automatically.

### Example: Podcast Generator

```python
import gradio as gr
from daggr import node, graph
from gradio_client import Client

# Wrap external clients as nodes
tts = node(Client("abidlabs/tts"), api_name="/generate_voice_design")
chatterbox = node(Client("ResembleAI/chatterbox"), api_name="/generate")

# Decorate functions to make them nodes
@node
def generate_dialogue(topic: str, host_voice: str, guest_voice: str):
    dialogue = [
        {"voice": host_voice, "text": "Welcome to today's episode!"},
        {"voice": guest_voice, "text": "Thanks for having me!"},
    ]
    html = "<p>Dialogue generated...</p>"
    return dialogue, html

@node
def combine_audio(clips: list[str]) -> str:
    return clips[0] if clips else None

# Define workflow - function parameters become UI inputs
@graph
def podcast_generator(
    host_desc: str = gr.Textbox(
        label="Host Voice Description",
        value="Deep British voice that is very professional...",
        lines=3,
    ),
    guest_desc: str = gr.Textbox(
        label="Guest Voice Description", 
        value="Energetic, friendly young voice...",
        lines=3,
    ),
    topic: str = gr.Textbox(
        label="Episode Topic",
        value="AI in healthcare",
    ),
):
    # Looks like normal Python - but builds a DAG
    host_voice = tts(
        voice_description=host_desc,
        language="Auto",
        text="Hello, I'm your host.",
    )
    
    guest_voice = tts(
        voice_description=guest_desc,
        language="Auto", 
        text="Hi everyone!",
    )
    
    # Node calls return Future-like objects
    dialogue, html = generate_dialogue(
        topic=topic,
        host_voice=host_voice.audio,
        guest_voice=guest_voice.audio,
    )
    
    # SCATTER: .map() runs the node once per item
    line_audio = chatterbox.map(
        audio_prompt=dialogue.each["voice"],
        text=dialogue.each["text"],
    )
    
    # GATHER: .all() collects outputs
    final = combine_audio(line_audio.audio.all())
    
    # Returns become UI outputs
    return html, final.audio

# Launch!
podcast_generator.launch()
```

### Scatter/Gather API

```python
# Scatter: .map() method on node clients
line_audio = chatterbox.map(
    text=dialogue.each["text"],      # Each item's "text" field
    voice=dialogue.each["voice"],    # Each item's "voice" field  
)

# Gather: .all() method (same as Option A)
final = combine_audio(line_audio.audio.all())
```

### Pros
- **Concise**: Reads like normal Python code
- **Familiar**: Similar to Prefect, Airflow, Luigi patterns
- **Less boilerplate**: No explicit node registration, inputs/outputs dicts
- **Natural flow**: Control flow follows code structure

### Cons
- **Magic**: Tracing happens behind the scenes (harder to debug)
- **Two modes**: Code behaves differently during tracing vs execution
- **Edge cases**: Conditionals, loops, exceptions need special handling
- **Less explicit**: Harder to see the full graph structure

---

## Side-by-Side Comparison

| Aspect | Option A (Explicit) | Option B (Decorator) |
|--------|---------------------|----------------------|
| **Define external client** | `GradioNode(space_or_url=..., inputs={...}, outputs={...})` | `node(Client(...))` |
| **Define function node** | `FnNode(fn=..., inputs={...}, outputs={...})` | `@node` decorator |
| **Define workflow** | `Graph(nodes=[...])` | `@graph` decorator |
| **Connect nodes** | `node_b.input: node_a.output` | `result = node_a(...)` |
| **Scatter** | `.each["key"]` | `.map()` + `.each["key"]` |
| **Gather** | `.all()` | `.all()` |
| **UI inputs** | `gr.Textbox(...)` in node inputs | Function parameters with defaults |
| **UI outputs** | `outputs={...}` dict | Return values |
| **Lines of code** | ~60 | ~45 |

---

## Questions for Discussion

1. **Which API feels more natural for our use cases?**

2. **Do we value explicitness over conciseness?**

3. **Should we support both?** (Option B as sugar that generates Option A under the hood)

4. **How important is graph visualization/inspection?** (Option A makes this easier)

5. **What about error handling?** (Option A: errors at node level; Option B: errors during tracing vs execution)

6. **Scatter/Gather syntax preferences?**
   - Option A: `node.output.each["key"]` → `node.output.all()`
   - Option B: `node.map(x=source.each["key"])` → `node.output.all()`

---

## Implementation Complexity

| Component | Option A | Option B |
|-----------|----------|----------|
| Core implementation | ✅ Done | 🔨 Needs work |
| Scatter/gather | ✅ Done | Uses same primitives |
| UI generation | ✅ Done | Needs adaptation |
| Error messages | Straightforward | Requires source mapping |
| Testing | Easy to unit test | Need to test tracing |

---

## Recommendation

**Start with Option A** (explicit API) as the foundation, then consider adding **Option B as syntactic sugar** that compiles down to Option A. This gives users:

- Simple cases: Use `@node` and `@graph` decorators
- Complex cases: Drop down to explicit `FnNode`, `GradioNode`, `Graph`
- Debugging: Can always inspect the underlying explicit graph

The scatter/gather primitives (`.each`, `.all()`) work the same in both APIs.

