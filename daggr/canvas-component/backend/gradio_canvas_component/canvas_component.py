"""Canvas component for displaying DAG workflows."""

from __future__ import annotations

from typing import Any, Callable, Literal

from gradio.components.base import Component
from gradio.events import Events


class CanvasComponent(Component):
    """
    A canvas component for displaying DAG-based workflows with nodes and edges.
    """

    EVENTS = [Events.change]

    def __init__(
        self,
        value: dict | Callable | None = None,
        *,
        label: str | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool | Literal["hidden"] = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        height: int | str | None = "100vh",
    ):
        """
        Parameters:
            value: Default graph data with 'name', 'nodes', and 'edges' keys.
            label: The label for this component.
            show_label: If True, will display label.
            container: If True, will place the component in a container.
            scale: Relative size compared to adjacent Components.
            min_width: Minimum pixel width.
            visible: If False, component will be hidden.
            elem_id: An optional string for the HTML DOM id.
            elem_classes: An optional list of strings for CSS classes.
            render: If False, component will not be rendered.
            height: The height of the canvas.
        """
        self.height = height
        super().__init__(
            label=label,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            value=value,
        )

    def preprocess(self, payload: dict | None) -> dict | None:
        """Pass through the canvas data."""
        return payload

    def postprocess(self, value: dict | None) -> dict | None:
        """Pass through the canvas data."""
        if value is None:
            return {"name": "workflow", "nodes": [], "edges": []}
        return value

    def example_payload(self) -> Any:
        return {"name": "Example Workflow", "nodes": [], "edges": []}

    def example_value(self) -> Any:
        return {"name": "Example Workflow", "nodes": [], "edges": []}

    def api_info(self) -> dict[str, Any]:
        return {
            "type": "object",
            "description": "Canvas data with name, nodes, and edges",
        }

    def get_block_name(self) -> str:
        return "canvascomponent"
