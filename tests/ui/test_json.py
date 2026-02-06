import gradio as gr
from playwright.sync_api import Page, expect

from daggr import FnNode, Graph
from tests.ui.helpers import launch_daggr_server, wait_for_graph_load


def test_json_input_and_output(page: Page, temp_db: str):
    def process_config(config):
        return {"processed": True, "original": config}

    node = FnNode(
        process_config,
        name="processor",
        inputs={"config": gr.JSON(label="Config")},
        outputs={"result": gr.JSON(label="Result")},
    )

    graph = Graph("JSON Test", nodes=[node], persist_key=False)
    server, url = launch_daggr_server(graph, temp_db)

    try:
        page.goto(url)
        wait_for_graph_load(page)

        nodes = page.locator(".node")
        expect(nodes).to_have_count(2)

        input_node = page.locator(".node:has(.type-badge:text('INPUT'))")
        expect(input_node).to_be_visible()

        json_textarea = input_node.locator("textarea.json-textarea")
        expect(json_textarea).to_be_visible()
        json_textarea.fill('{"name": "test", "count": 42}')

        run_btn = page.locator(".run-btn").first
        run_btn.click()

        page.wait_for_function(
            """() => {
                const jsonNodes = document.querySelectorAll('.json-string');
                for (const node of jsonNodes) {
                    if (node.textContent && node.textContent.includes('test')) {
                        return true;
                    }
                }
                return false;
            }""",
            timeout=15000,
        )
    finally:
        server.close()

