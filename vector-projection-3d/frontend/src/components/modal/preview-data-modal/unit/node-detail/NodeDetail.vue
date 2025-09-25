<template>
  <div class="node-detail">
    <DetailTable :data="data" :fields="nodeFields"></DetailTable>
  </div>
</template>

<script lang="ts" setup>
import DetailTable from "@components/common/detail-table/DetailTable.vue";
import type { PropType } from "vue";
import type { GraphNode } from "@/types/graph";
import type { Field } from "@/types/detail-table";

const props = defineProps({
  data: {
    type: Object as PropType<GraphNode>,
  },
});

const nodeFields = [
  { key: "id", label: "ID", mono: true, format: "text" },
  { key: "group", label: "그룹" },
  { key: "report_type", label: "리포트 유형" },
  {
    key: "summary",
    label: "요약",
    clamp: true,
    clampLines: 4,
    scrollOnClamp: true,
  },
] as Field[];
</script>

<style></style>
