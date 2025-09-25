<template>
  <div class="graph-inspector-link-detail">
    <NodeDetail v-if="isSelectedNode" :data="data as GraphNode"></NodeDetail>
    <LinkDetail v-else :data="data as GraphLink"></LinkDetail>
  </div>
</template>

<script lang="ts" setup>
import NodeDetail from "@components/modal/preview-data-modal/unit/node-detail/NodeDetail.vue";
import LinkDetail from "@components/modal/preview-data-modal/unit/link-detail/LinkDetail.vue";
import { PropType } from "vue";
import { GraphLink, GraphNode } from "@/types/graph";

const props = defineProps({
  isSelectedNode: {
    type: Boolean,
    default: true,
  },
  data: {
    type: Object as PropType<GraphNode | GraphLink>,
    default: () => {},
  },
});
</script>

<style></style>
