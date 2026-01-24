<script lang="ts">
	import AudioPlayer from './AudioPlayer.svelte';
	import type { GradioComponentData } from '../types';

	interface Props {
		comp: GradioComponentData;
		nodeId: string;
		isInputNode: boolean;
		value: any;
		onchange?: (portName: string, value: any) => void;
	}

	let { comp, nodeId, isInputNode, value, onchange }: Props = $props();

	function handleInput(e: Event) {
		const target = e.target as HTMLInputElement | HTMLTextAreaElement;
		onchange?.(comp.port_name, target.value);
	}

	function handleNumberInput(e: Event) {
		const target = e.target as HTMLInputElement;
		onchange?.(comp.port_name, parseFloat(target.value));
	}

	function handleCheckboxChange(e: Event) {
		const target = e.target as HTMLInputElement;
		onchange?.(comp.port_name, target.checked);
	}
</script>

<div class="embedded-component">
	{#if comp.component === 'textbox' || comp.component === 'text'}
		<div class="gr-textbox-wrap">
			<span class="gr-label">{comp.props?.label || comp.port_name}</span>
			{#if comp.props?.lines && comp.props.lines > 1}
				<textarea
					class="gr-input"
					placeholder={comp.props?.placeholder || ''}
					rows={comp.props?.lines || 3}
					disabled={!isInputNode}
					{value}
					oninput={handleInput}
				></textarea>
			{:else}
				<input
					type="text"
					class="gr-input"
					placeholder={comp.props?.placeholder || ''}
					disabled={!isInputNode}
					{value}
					oninput={handleInput}
				/>
			{/if}
		</div>
	{:else if comp.component === 'number'}
		<div class="gr-textbox-wrap">
			<span class="gr-label">{comp.props?.label || comp.port_name}</span>
			<input
				type="number"
				class="gr-input"
				disabled={!isInputNode}
				{value}
				oninput={handleNumberInput}
			/>
		</div>
	{:else if comp.component === 'checkbox'}
		<label class="gr-checkbox-wrap">
			<input
				type="checkbox"
				disabled={!isInputNode}
				checked={value}
				onchange={handleCheckboxChange}
			/>
			<span class="gr-check-label">{comp.props?.label || comp.port_name}</span>
		</label>
	{:else if comp.component === 'markdown'}
		<div class="gr-textbox-wrap">
			<span class="gr-label">{comp.props?.label || comp.port_name}</span>
			<div class="gr-markdown">{@html comp.value || ''}</div>
		</div>
	{:else if comp.component === 'html'}
		<div class="gr-textbox-wrap">
			<span class="gr-label">{comp.props?.label || comp.port_name}</span>
			<div class="gr-html">{@html comp.value || ''}</div>
		</div>
	{:else if comp.component === 'json'}
		<div class="gr-textbox-wrap">
			<span class="gr-label">{comp.props?.label || comp.port_name}</span>
			<pre class="gr-json">{typeof comp.value === 'string' ? comp.value : JSON.stringify(comp.value, null, 2)}</pre>
		</div>
	{:else if comp.component === 'audio'}
		{@const audioSrc = comp.value?.url || comp.value}
		<div class="gr-audio-wrap">
			<span class="gr-label">{comp.props?.label || comp.port_name}</span>
			{#if audioSrc}
				<AudioPlayer src={audioSrc} id="{nodeId}_{comp.port_name}" />
			{:else}
				<div class="gr-empty">No audio</div>
			{/if}
		</div>
	{:else if comp.component === 'image'}
		<div class="gr-textbox-wrap">
			<span class="gr-label">{comp.props?.label || comp.port_name}</span>
			{#if comp.value}
				<img class="gr-image" src={comp.value?.url || comp.value} alt={comp.props?.label || ''} />
			{:else}
				<div class="gr-empty">No image</div>
			{/if}
		</div>
	{:else}
		<div class="gr-fallback">
			<span class="fallback-type">{comp.component}</span>
			{#if comp.value}
				<pre>{typeof comp.value === 'string' ? comp.value : JSON.stringify(comp.value, null, 2)}</pre>
			{/if}
		</div>
	{/if}
</div>

<style>
	.embedded-component {
		margin-bottom: 8px;
	}

	.embedded-component:last-child {
		margin-bottom: 0;
	}

	.gr-textbox-wrap {
		background: #1a1a1a;
		border: 1px solid #333;
		border-radius: 6px;
		overflow: hidden;
	}

	.gr-label {
		display: block;
		font-size: 10px;
		font-weight: 400;
		color: #888;
		padding: 6px 10px 0;
	}

	.gr-input {
		width: 100%;
		padding: 4px 10px 8px;
		font-size: 11px;
		font-family: inherit;
		color: #e5e7eb;
		background: transparent;
		border: none;
		outline: none;
		box-sizing: border-box;
	}

	.gr-input::placeholder {
		color: #555;
	}

	.gr-textbox-wrap:focus-within {
		border-color: #f97316;
	}

	.gr-input:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}

	textarea.gr-input {
		resize: none;
		min-height: 36px;
		line-height: 1.4;
	}

	.gr-checkbox-wrap {
		display: flex;
		align-items: center;
		gap: 8px;
		cursor: pointer;
		padding: 6px 0;
	}

	.gr-checkbox-wrap input[type="checkbox"] {
		width: 14px;
		height: 14px;
		accent-color: #f97316;
		cursor: pointer;
	}

	.gr-check-label {
		font-size: 11px;
		color: #e5e7eb;
	}

	.gr-markdown,
	.gr-html {
		font-size: 11px;
		color: #d1d5db;
		line-height: 1.4;
		padding: 6px 10px 8px;
		max-height: 100px;
		overflow: auto;
	}

	.gr-html :global(strong), .gr-html :global(b) {
		font-weight: 600;
		color: #f3f4f6;
	}

	.gr-html :global(em), .gr-html :global(i) {
		font-style: italic;
	}

	.gr-html :global(a) {
		color: #f97316;
		text-decoration: underline;
	}

	.gr-html :global(code) {
		font-family: 'SF Mono', Monaco, Consolas, monospace;
		background: rgba(249, 115, 22, 0.1);
		padding: 1px 4px;
		border-radius: 3px;
		font-size: 10px;
	}

	.gr-json {
		font-size: 10px;
		font-family: 'SF Mono', Monaco, Consolas, monospace;
		color: #9ca3af;
		padding: 6px 10px 8px;
		max-height: 100px;
		overflow: auto;
		margin: 0;
		white-space: pre-wrap;
		word-break: break-all;
	}

	.gr-audio-wrap {
		background: #1a1a1a;
		border: 1px solid #333;
		border-radius: 6px;
		overflow: hidden;
	}

	.gr-image {
		width: 100%;
		max-height: 80px;
		object-fit: contain;
	}

	.gr-empty {
		font-size: 11px;
		color: #555;
		font-style: italic;
		padding: 10px;
		text-align: center;
	}

	.gr-fallback {
		font-size: 10px;
		color: #9ca3af;
		background: #1a1a1a;
		border: 1px solid #333;
		padding: 8px 10px;
		border-radius: 6px;
	}

	.gr-fallback .fallback-type {
		display: inline-block;
		color: #666;
		font-style: italic;
		font-size: 9px;
		background: #2a2a2a;
		padding: 2px 6px;
		border-radius: 4px;
		margin-bottom: 4px;
	}

	.gr-fallback pre {
		margin: 0;
		font-size: 9px;
		white-space: pre-wrap;
		word-break: break-all;
		max-height: 60px;
		overflow: auto;
	}
</style>

