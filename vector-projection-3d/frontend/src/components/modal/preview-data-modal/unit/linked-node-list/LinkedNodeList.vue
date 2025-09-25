<template>
  <div class="linked-node-list linked-node-list__board-wrap">
    <BaseTable
      v-model:page="page"
      v-model:pageSize="pageSize"
      :columns="columns"
      :rows="data"
      @row:click="rowClick"
    ></BaseTable>
    <Pagination
      v-model:page="page"
      v-model:pageSize="pageSize"
      :total="data.length"
    ></Pagination>
  </div>
</template>

<script lang="ts" setup>
import Pagination from "@components/common/pagination/Pagination.vue";
import BaseTable from "@components/common/base-table/BaseTable.vue";
import { PropType, ref, watch } from "vue";
import type { GraphNode } from "@/types/graph";

const props = defineProps({
  data: {
    type: Array as PropType<GraphNode[]>,
    default: () => [],
  },
});

const emit = defineEmits(["row:click"]);

watch(
  () => props.data,
  () => {
    page.value = 1;
  },
  { deep: true },
);

const page = ref(1);
const pageSize = ref(10);
const columns = [
  { key: "id", label: "ID", width: "60px", sortable: true },
  { key: "group", label: "그룹" },
  { key: "report_type", label: "리포트 유형" },
  {
    key: "summary",
    label: "요약",
    width: "320px",
  },
];

const rowClick = (row: GraphNode) => {
  emit("row:click", row);
};
</script>

<style>
@import "./LinkedNodeList.css";
</style>
