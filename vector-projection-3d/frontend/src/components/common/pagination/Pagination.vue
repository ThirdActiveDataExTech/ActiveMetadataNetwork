<template>
  <nav class="pagination-wrap">
    <div class="pagination-group">
      <button
        :disabled="disabled || page === 1"
        aria-label="첫 페이지"
        class="pagination-button"
        type="button"
        @click="goFirst"
      >
        «
      </button>
      <button
        :disabled="disabled || page === 1"
        aria-label="이전 페이지"
        class="pagination-button"
        type="button"
        @click="goPrev"
      >
        ‹
      </button>

      <button
        v-for="p in pageButtons"
        :key="p"
        :class="{ active: p === page }"
        :disabled="disabled"
        class="pagination-button"
        type="button"
        @click="updatePage(p)"
      >
        {{ p }}
      </button>

      <button
        :disabled="disabled || page === totalPages"
        aria-label="다음 페이지"
        class="pagination-button"
        type="button"
        @click="goNext"
      >
        ›
      </button>
      <button
        :disabled="disabled || page === totalPages"
        aria-label="마지막 페이지"
        class="pagination-button"
        type="button"
        @click="goLast"
      >
        »
      </button>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { computed } from "vue";

const props = defineProps({
  total: { type: Number, required: true },
  page: { type: Number, default: 1 },
  pageSize: { type: Number, default: 20 },
  maxButtons: { type: Number, default: 10 },
  disabled: { type: Boolean, default: false },
});

const emit = defineEmits(["update:page", "update:pageSize", "change"]);

const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.total / props.pageSize || 1)),
);

const page = computed(() =>
  Math.min(Math.max(1, props.page), totalPages.value),
);

const updatePage = (p: number) => {
  if (p === page.value) return;
  emit("update:page", p);
  emit("change", { page: p, pageSize: props.pageSize });
};

const goFirst = () => {
  updatePage(1);
};
const goPrev = () => {
  updatePage(Math.max(1, page.value - 1));
};
const goNext = () => {
  updatePage(Math.min(totalPages.value, page.value + 1));
};
const goLast = () => {
  updatePage(totalPages.value);
};

const pageButtons = computed(() => {
  const tp = totalPages.value;
  const cur = page.value;
  const win = Math.min(tp, Math.max(1, props.maxButtons)); // 보여줄 버튼 개수
  const half = Math.floor(win / 2);

  let start = cur - half;
  let end = start + win - 1;

  // 좌측 경계 보정
  if (start < 1) {
    start = 1;
    end = Math.min(tp, start + win - 1);
  }
  // 우측 경계 보정
  if (end > tp) {
    end = tp;
    start = Math.max(1, end - win + 1);
  }

  const arr = [];
  for (let i = start; i <= end; i++) arr.push(i);
  return arr;
});
</script>

<style scoped>
@import "./Pagination.css";
</style>
