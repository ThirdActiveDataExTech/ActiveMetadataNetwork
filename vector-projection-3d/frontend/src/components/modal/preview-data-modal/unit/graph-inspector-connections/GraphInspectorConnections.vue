<template>
  <div class="graph-inspector-connections">
    <LinkedNodeList
      v-if="showList"
      :data="linkedDataList"
      class="graph-inspector-connections__node-list"
      @row:click="rowClick"
    ></LinkedNodeList>
    <div v-else class="graph-inspector-connections__detail">
      <NodeDetail :data="selectedData"></NodeDetail>
      <div class="graph-inspector-connections__actions">
        <button class="btn-gray" type="button" @click="showList = true">
          목록
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch } from "vue";
import LinkedNodeList from "@components/modal/preview-data-modal/unit/linked-node-list/LinkedNodeList.vue";
import NodeDetail from "@components/modal/preview-data-modal/unit/node-detail/NodeDetail.vue";
import type { PropType } from "vue";
import type { GraphNode } from "@/types/graph";

const props = defineProps({
  isSelectedNode: {
    type: Boolean,
    default: true,
  },
  data: {
    type: Object as PropType<GraphNode>,
    default: () => {},
  },
  linkedDataList: {
    type: Array as PropType<GraphNode[]>,
    default: () => [],
  },
});

const showList = ref<boolean>(false);
const selectedData = ref<GraphNode>({});

const rowClick = (row: GraphNode) => {
  selectedData.value = row;
  showList.value = false;
};

watch(
  () => props.data,
  (val) => {
    selectedData.value = val;
  },
  { deep: true, immediate: true },
);

watch(
  () => props.isSelectedNode,
  (val) => {
    showList.value = !val;
  },
  { immediate: true },
);
</script>

<style>
@import "./GraphInspectorConnections.css";
</style>
