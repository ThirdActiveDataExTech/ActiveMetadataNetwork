<template>
  <div class="base-table-wrap">
    <table>
      <thead>
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            :aria-sort="ariaSort(col.key)"
            :style="col.width ? { width: col.width } : null"
          >
            <button
              v-if="col.sortable"
              :title="`Sort by ${col.label}`"
              class="sort-button"
              type="button"
              @click="toggleSort(col.key)"
            >
              <span>{{ col.label }}</span>
              <span
                :class="{
                  active: sortBy === col.key,
                  desc: sortBy === col.key && sortDir === 'desc',
                }"
                class="sort-caret"
              />
            </button>
            <span v-else>{{ col.label }}</span>
          </th>
        </tr>
      </thead>

      <tbody v-if="pagedRows.length">
        <tr
          v-for="(row, idx) in pagedRows"
          :key="row.id ?? idx"
          class="row"
          @click="emitRowClick(row)"
        >
          <td
            v-for="col in columns"
            :key="col.key"
            :class="col.align ? `td-${col.align}` : null"
          >
            <div :title="format(row[col.key], col)" class="ellipsis">
              <slot :data="row[col.key]" :name="col.key" :row="row">
                {{ format(row[col.key], col) }}
              </slot>
            </div>
          </td>
        </tr>
      </tbody>

      <tbody v-else>
        <tr>
          <td :colspan="columns.length" class="empty">No data</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from "vue";
import { TableColumn, TableRow } from "@/types/base-table.js";

const props = withDefaults(
  defineProps<{
    columns: TableColumn[];
    rows: TableRow[];
  }>(),
  {
    columns: () => ({}),
    rows: () => [],
  },
);

const page = defineModel("page", { type: Number, default: 1 });
const pageSize = defineModel("pageSize", { type: Number, default: 10 });

const emit = defineEmits(["row:click"]);

const sortBy = ref("");
const sortDir = ref("asc");

const toggleSort = (key: string) => {
  if (sortBy.value === key) {
    sortDir.value = sortDir.value === "asc" ? "desc" : "asc";
  } else {
    sortBy.value = key;
    sortDir.value = "asc";
  }
};
const ariaSort = (key: string) => {
  if (sortBy.value !== key) return "none";
  return sortDir.value === "asc" ? "ascending" : "descending";
};

const sortedRows = computed(() => {
  const arr = [...props.rows];
  const key = sortBy.value;
  if (!key) return arr;
  const dir = sortDir.value;
  return arr.sort((a, b) => {
    const va = a?.[key];
    const vb = b?.[key];
    if (va == null && vb == null) return 0;
    if (va == null) return 1;
    if (vb == null) return -1;
    if (typeof va === "number" && typeof vb === "number") {
      return dir === "asc" ? va - vb : vb - va;
    }
    const sa = String(va).toLowerCase();
    const sb = String(vb).toLowerCase();
    if (sa < sb) return dir === "asc" ? -1 : 1;
    if (sa > sb) return dir === "asc" ? 1 : -1;
    return 0;
  });
});

const pagedRows = computed(() => {
  const start = (page.value - 1) * pageSize.value;
  return sortedRows.value.slice(start, start + pageSize.value);
});

const format = (val: any, col: TableColumn) => {
  if (col?.format === "number") {
    return new Intl.NumberFormat().format(val ?? 0);
  }
  if (col?.format === "date" && val) {
    const d = new Date(val);
    if (!isNaN(d)) return d.toLocaleString();
  }
  return val ?? "";
};

const emitRowClick = (row: TableRow) => {
  emit("row:click", row);
};
</script>

<style>
@import "./BaseTable.css";
</style>
