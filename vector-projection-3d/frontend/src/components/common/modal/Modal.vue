<template>
  <!-- Main modal -->
  <div :class="[useOverlay ? 'modal-overlay' : 'modal-layer', placeClass]">
    <div class="modal-container">
      <!-- Modal content -->
      <div class="modal-content">
        <!-- Modal header -->
        <div class="modal-header">
          <slot name="header">
            <h3 class="modal-title">
              {{ props.title }}
            </h3>
          </slot>
          <button
            aria-label="close"
            class="modal-close"
            type="button"
            @click="closeModal"
          >
            <svg
              aria-hidden="true"
              class="icon"
              fill="none"
              viewBox="0 0 14 14"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
                stroke="currentColor"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
              />
            </svg>
          </button>
        </div>

        <!-- Modal body -->
        <div class="modal-body">
          <slot name="body"> </slot>
        </div>

        <!-- Modal footer -->
        <div v-if="showFooter" class="modal-footer">
          <slot name="footer">
            <button
              class="btn-primary"
              data-modal-hide="static-modal"
              type="button"
              @click="confirm"
            >
              Confirm
            </button>
            <button
              class="btn-secondary"
              data-modal-hide="static-modal"
              type="button"
              @click="closeModal"
            >
              Cancel
            </button>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from "vue";

const props = defineProps({
  useOverlay: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: "Title",
  },
  showFooter: {
    type: Boolean,
    default: true,
  },
  placement: {
    type: String,
    default: "center",
    validator: (v) =>
      [
        "top-left",
        "top-center",
        "top-right",
        "center-left",
        "center",
        "center-right",
        "bottom-left",
        "bottom-center",
        "bottom-right",
      ].includes(v),
  },
});

const placeClass = computed(
  () =>
    ({
      "top-left": "place-top-left",
      "top-center": "place-top-center",
      "top-right": "place-top-right",
      "center-left": "place-center-left",
      center: "place-center",
      "center-right": "place-center-right",
      "bottom-left": "place-bottom-left",
      "bottom-center": "place-bottom-center",
      "bottom-right": "place-bottom-right",
    })[props.placement],
);

const emit = defineEmits(["close", "confirm"]);

const confirm = () => {
  emit("confirm");
};

const closeModal = () => {
  emit("close");
};
</script>

<style>
@import "./Modal.css";
</style>
