<template>
  <div class="link-detail link-detail__table-group">
    <DetailTable :data="data" :fields="linkFields"></DetailTable>
    <DetailTable
      :data="data?.source as GraphNode"
      :fields="nodeFields"
      title="Source"
    ></DetailTable>
    <DetailTable
      :data="data?.target as GraphNode"
      :fields="nodeFields"
      title="Target"
    ></DetailTable>
  </div>
</template>

<script lang="ts" setup>
import DetailTable from "@components/common/detail-table/DetailTable.vue";
import type { PropType } from "vue";
import type { GraphLink, GraphNode } from "@/types/graph";
import type { Field } from "@/types/detail-table";

const props = defineProps({
  data: {
    type: Object as PropType<GraphLink>,
  },
});

const linkFields = [
  { key: "type", label: "유형" },
  { key: "report_type", label: "리포트 유형" },
];

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

<style>
@import "./LinkDetail.css";
</style>
