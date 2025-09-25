<template>
  <Modal
    :height="modalHeight"
    :show-footer="false"
    class="preview-data-modal"
    placement="top-right"
    title="Preview Data"
    @close="closeModal"
  >
    <template v-slot:body>
      <GraphInspectorLinkDetail
        v-if="mode === 'link-detail'"
        :data="selectedData"
        :is-selected-node="isSelectedNode"
      ></GraphInspectorLinkDetail>
      <GraphInspectorConnections
        v-else
        :data="selectedData as GraphNode"
        :is-selected-node="isSelectedNode"
        :linked-data-list="linkedNodeData"
      ></GraphInspectorConnections>
    </template>
  </Modal>
</template>
<script lang="ts" setup>
import { computed } from "vue";
import Modal from "@components/common/modal/Modal.vue";
import GraphInspectorConnections from "@components/modal/preview-data-modal/unit/graph-inspector-connections/GraphInspectorConnections.vue";
import GraphInspectorLinkDetail from "@components/modal/preview-data-modal/unit/graph-inspector-link-detail/GraphInspectorLinkDetail.vue";
import type { GraphNode, GraphLink } from "@/types/graph";
import { PropType } from "vue";

const props = defineProps({
  /**
   * 노드/링크 클릭 시 동작 모드.
   *
   * - "connections": 노드 클릭 → 노드 상세
   *                  링크 클릭 → 연결된 모든 노드 목록
   *                  목록 행 선택 → 노드 상세
   * - "link-detail": 노드 클릭 → 노드 상세
   *                  링크 클릭 → 링크 상세
   */
  mode: {
    type: String as PropType<"connections" | "link-detail">,
    default: "link-detail",
  },
  selectedDataMode: {
    type: String as PropType<"node" | "link">,
    default: "node",
  },
  selectedData: {
    type: Object as PropType<GraphNode | GraphLink>,
    default: () => {},
  },
  linkedNodeData: {
    type: Array as PropType<GraphNode[]>,
    default: () => [],
  },
});

const modalHeight = () => {
  return props.mode === "link-detail" || isSelectedNode.value
    ? "auto"
    : "370px";
};

const isSelectedNode = computed(() => {
  return props.selectedDataMode === "node";
});

const emit = defineEmits(["close"]);

const closeModal = () => {
  emit("close");
};
</script>
