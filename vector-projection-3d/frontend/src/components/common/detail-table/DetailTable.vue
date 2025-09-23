<template>
  <div class="detail-wrap">
    <div v-if="showHeader" class="detail-head">
      <div class="detail-title">
        <slot name="title">
          {{ title }}
        </slot>
      </div>
      <div class="detail-head-extra">
        <slot name="header-extra" />
      </div>
    </div>
    <table class="detail-table">
      <tbody>
        <tr v-for="f in shownFields" :key="f.key" class="row">
          <!-- Label -->
          <th class="th">
            <slot :field="f" name="label">
              {{ f.label ?? f.key }}
            </slot>
          </th>

          <!-- Value -->
          <td
            :class="{
              'td-right': f.align === 'right',
              'td-center': f.align === 'center',
              mono: f.mono,
            }"
            class="td"
          >
            <slot :data="data" :field="f" :value="valOf(f)" name="cell">
              <template v-if="isEmpty(valOf(f))">
                <span class="muted">—</span>
              </template>

              <template v-else>
                <div
                  :class="{
                    clamp: isClamped(f) && !f.scrollOnClamp,
                    'clamp-scroll': isClamped(f) && f.scrollOnClamp,
                  }"
                  :style="clampStyleOf(f)"
                  class="value"
                >
                  {{ format(valOf(f), f) }}
                </div>
              </template>
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts" setup>
import { computed, useSlots } from "vue";
import type { Field, Formatter } from "@/types/detail-table";

const props = withDefaults(
  defineProps<{
    data?: Record<string, unknown>;
    fields?: Field[];
    title?: string;
  }>(),
  {
    data: () => ({}),
    fields: () => [],
    title: "",
  },
);

const slots = useSlots();
const showHeader = computed(
  () => !!props.title || !!slots.title || !!slots["header-extra"],
);

const shownFields = computed<Field[]>(() => {
  return props.fields && props.fields.length
    ? props.fields
    : Object.keys(props.data || {}).map((k) => ({ key: k, label: k }));
});

const valOf = (f: Field) => {
  return props.data?.[f.key];
};

const isEmpty = (v: any) => {
  return v == null || (typeof v === "string" && v.trim() === "");
};

/** 필드별 클램프/줄수/스크롤 계산 */
const isClamped = (f: Field) => {
  return f.clamp === true || typeof f.clampLines === "number";
};
const linesOf = (f: Field) => {
  return typeof f.clampLines === "number" && f.clampLines > 0
    ? f.clampLines
    : 3;
};
const clampStyleOf = (f: Field) => {
  return isClamped(f) ? { "--clamp": String(linesOf(f)) } : {};
};

/** 포맷 */
const inferFormat = (v: any): Formatter => {
  if (typeof v === "number") return "number";
  if (v instanceof Date) return "date";
  if (typeof v === "object" && v !== null) return "json";
  return "text";
};
const format = (v: any, f: Field): string => {
  const fmt = f.format ?? inferFormat(v);
  if (typeof fmt === "function") return String(fmt(v, f, props.data));

  if (fmt === "number") {
    const n = Number(v);
    if (!(typeof n === "number" && isFinite(n))) return String(v);
    return new Intl.NumberFormat().format(n) + (f.unit ? ` ${f.unit}` : "");
  }
  if (fmt === "date") {
    const d = new Date(v);
    return isNaN(+d) ? String(v) : d.toLocaleString();
  }
  if (fmt === "json") {
    try {
      return JSON.stringify(v, null, 2);
    } catch {
      return String(v);
    }
  }
  return String(v); // text
};
</script>

<style>
@import "./DetailTable.css";
</style>
