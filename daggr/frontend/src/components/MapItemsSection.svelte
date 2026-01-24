<script lang="ts">
	import AudioPlayer from './AudioPlayer.svelte';
	import type { MapItem } from '../types';

	interface Props {
		nodeId: string;
		nodeName: string;
		items: MapItem[];
		onReplayItem?: (nodeName: string, index: number) => void;
	}

	let { nodeId, nodeName, items, onReplayItem }: Props = $props();

	function handleReplay(e: MouseEvent, index: number) {
		e.stopPropagation();
		onReplayItem?.(nodeName, index);
	}
</script>

<div class="map-items-section">
	<div class="map-items-header">
		<span class="map-items-title">Items ({items.length})</span>
	</div>
	<div class="map-items-list">
		{#each items as item (item.index)}
			<div class="map-item" class:has-output={item.output}>
				<div class="map-item-content">
					{#if item.is_audio_output && item.output}
						<AudioPlayer 
							src={item.output} 
							id="{nodeId}_map_{item.index}" 
							compact={true}
						/>
					{:else if item.output}
						<span class="map-item-preview" title={item.output}>
							{item.output.length > 40 ? item.output.slice(0, 40) + '...' : item.output}
						</span>
					{:else}
						<span class="map-item-preview map-item-pending">Pending...</span>
					{/if}
				</div>
				<button 
					class="map-item-replay"
					onclick={(e) => handleReplay(e, item.index)}
					title={item.output ? "Replay this item" : "Run this item"}
				>
					{item.output ? '↻' : '▶'}
				</button>
			</div>
		{/each}
	</div>
</div>

<style>
	.map-items-section {
		border-top: 1px solid rgba(34, 197, 94, 0.2);
		background: rgba(34, 197, 94, 0.03);
	}

	.map-items-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 6px 10px;
		border-bottom: 1px solid rgba(34, 197, 94, 0.1);
	}

	.map-items-title {
		font-size: 10px;
		font-weight: 600;
		color: #22c55e;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.map-items-list {
		max-height: 300px;
		overflow-y: auto;
	}

	.map-item {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 10px;
		border-bottom: 1px solid rgba(34, 197, 94, 0.08);
	}

	.map-item:last-child {
		border-bottom: none;
	}

	.map-item-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.map-item-preview {
		flex: 1;
		font-size: 10px;
		color: #888;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.map-item.has-output .map-item-preview {
		color: #aaa;
	}

	.map-item-pending {
		color: #666;
		font-style: italic;
	}

	.map-item-replay {
		width: 20px;
		height: 20px;
		border: none;
		background: rgba(34, 197, 94, 0.15);
		color: #22c55e;
		font-size: 10px;
		border-radius: 4px;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.15s;
		flex-shrink: 0;
		align-self: flex-start;
		margin-top: 4px;
	}

	.map-item-replay:hover {
		background: rgba(34, 197, 94, 0.3);
	}
</style>

