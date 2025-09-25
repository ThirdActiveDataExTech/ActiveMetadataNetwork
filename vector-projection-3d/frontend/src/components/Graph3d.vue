<template>
  <div ref="container" class="graph-container"></div>
  <PreviewDataModal
    v-if="isModalOpen"
    :linked-node-data="[...highlightNodes] as GraphNode[]"
    :selected-data="selectedData"
    :selected-data-mode="selectedDataMode"
    mode="connections"
    @close="selectedData = null"
  >
  </PreviewDataModal>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount, computed } from "vue";
import ForceGraph3D from "3d-force-graph";
import PreviewDataModal from "@components/modal/preview-data-modal/PreviewDataModal.vue";
import type { GraphNode, GraphLink, GraphData } from "@/types/graph";
import { API_BASE } from "@/config/env";
import { colorFromGroup } from "@/utils/color";

const container = ref(null);
let fg = null;
let resizeOff = () => {};
let timer = null;

// --- 하이라이트 상태 & 인덱스 ---
const highlightNodes = new Set(); // 노드 객체(Set)
const highlightLinks = new Set(); // 링크 객체(Set)
let lastClickedNode = null;

let adj = new Map(); // nodeId -> Set(neighborId)
let incidentLinks = new Map(); // nodeId -> Set(linkObj)

// 연결 성분 인덱스
let nodeIdToComp = new Map(); // nodeId -> compId
let compIdToNodeIds = new Map(); // compId -> Set(nodeId)
let compIdToLinks = new Map(); // compId -> Set(linkObj)

// 상단에 전역 상태 추가
let lastClickAt = 0;
let lastClickNodeRef = null;

// 카메라 이동 함수
function focusCameraOnNode(node: GraphNode, distance = 120, ms = 1000) {
  const distRatio =
    1 + distance / Math.hypot(node.x || 1, node.y || 1, node.z || 1);
  fg.cameraPosition(
    {
      x: (node.x || 0) * distRatio,
      y: (node.y || 0) * distRatio,
      z: (node.z || 0) * distRatio,
    },
    node,
    ms,
  );
}

function getNodeId(node: GraphNode) {
  return typeof node === "object" ? node.id : node;
}
function getEndIds(link: GraphLink) {
  const s = typeof link.source === "object" ? link.source.id : link.source;
  const t = typeof link.target === "object" ? link.target.id : link.target;
  return [s, t];
}

function computeComponents(data: GraphData) {
  nodeIdToComp = new Map();
  compIdToNodeIds = new Map();
  compIdToLinks = new Map();

  const visited = new Set();
  let compSeq = 0;

  for (const n of data.nodes) {
    if (visited.has(n.id)) continue;

    const cid = compSeq++;
    const q = [n.id];
    const nodeSet = new Set([n.id]);
    const linkSet = new Set();
    visited.add(n.id);
    nodeIdToComp.set(n.id, cid);

    while (q.length) {
      const u = q.shift();
      for (const v of adj.get(u) || []) {
        if (!visited.has(v)) {
          visited.add(v);
          nodeSet.add(v);
          nodeIdToComp.set(v, cid);
          q.push(v);
        }
      }
      for (const l of incidentLinks.get(u) || []) {
        const [a, b] = getEndIds(l);
        if (nodeSet.has(a) && nodeSet.has(b)) linkSet.add(l);
      }
    }

    compIdToNodeIds.set(cid, nodeSet);
    compIdToLinks.set(cid, linkSet);
  }
}

function highlightComponentByNode(node: GraphNode) {
  resetHighlight();
  if (!node) return;
  const data = fg.graphData();
  const cid = nodeIdToComp.get(node.id);
  if (cid === undefined) return;

  for (const nid of compIdToNodeIds.get(cid) || []) {
    const obj = data.nodes.find((n) => n.id === nid);
    if (obj) highlightNodes.add(obj);
  }
  for (const l of compIdToLinks.get(cid) || []) {
    highlightLinks.add(l);
  }
}

function highlightComponentByLink(link: GraphLink) {
  resetHighlight();
  if (!link) return;
  const data = fg.graphData();
  const [sId, tId] = getEndIds(link);
  const cid = nodeIdToComp.get(sId) ?? nodeIdToComp.get(tId);
  if (cid === undefined) return;
  for (const nid of compIdToNodeIds.get(cid) || []) {
    const obj = data.nodes.find((n) => n.id === nid);
    if (obj) highlightNodes.add(obj);
  }
  for (const l of compIdToLinks.get(cid) || []) highlightLinks.add(l);
}

function buildIndex(data: GraphData) {
  adj = new Map();
  incidentLinks = new Map();
  for (const n of data.nodes) {
    adj.set(n.id, new Set());
    incidentLinks.set(n.id, new Set());
  }
  for (const l of data.links) {
    const [a, b] = getEndIds(l);
    adj.get(a)?.add(b);
    adj.get(b)?.add(a);
    incidentLinks.get(a)?.add(l);
    incidentLinks.get(b)?.add(l);
  }
}
function resetHighlight() {
  highlightNodes.clear();
  highlightLinks.clear();
}
function activateNodeNeighborhood(node: GraphNode) {
  resetHighlight();
  if (!node) return;
  // 자신 + 이웃 노드
  highlightNodes.add(node);
  const nbs = adj.get(node.id) || new Set();
  for (const nbId of nbs) {
    const nbObj = fg.graphData().nodes.find((n) => n.id === nbId);
    if (nbObj) highlightNodes.add(nbObj);
  }
  // incident links
  for (const l of incidentLinks.get(node.id) || new Set()) {
    highlightLinks.add(l);
  }
}
function activateLinkNeighborhood(link: GraphLink) {
  resetHighlight();
  if (!link) return;
  const data = fg.graphData();
  const sId = typeof link.source === "object" ? link.source.id : link.source;
  const tId = typeof link.target === "object" ? link.target.id : link.target;
  const s = data.nodes.find((n) => n.id === sId);
  const t = data.nodes.find((n) => n.id === tId);
  if (s) {
    highlightNodes.add(s);
    for (const l of incidentLinks.get(s.id) || new Set()) highlightLinks.add(l);
  }
  if (t) {
    highlightNodes.add(t);
    for (const l of incidentLinks.get(t.id) || new Set()) highlightLinks.add(l);
  }
  highlightLinks.add(link); // 클릭한 링크 자체
}

const isHighlightActive = () => {
  return highlightNodes.size > 0 || highlightLinks.size > 0;
};

const isSelectedNode = (node: GraphNode) => {
  return node.id === selectedData.value?.id;
};

const loadGraph = async () => {
  const res = await fetch(`${API_BASE}/graph`);
  const data = await res.json();

  // 인덱스 먼저 준비
  buildIndex(data);
  computeComponents(data);

  // 처음 생성 시
  if (!fg) {
    const nodeColorFn = (node: GraphNode) => {
      const base = colorFromGroup(node.group);

      if (isHighlightActive()) {
        return highlightNodes.has(node)
          ? isSelectedNode(node)
            ? colorFromGroup(node.group, { s: 100, l: 70 }) // 클릭 노드 색상 설정
            : base
          : "#444"; // 비강조는 어둡게
      } else {
        return base;
      }
    };
    const nodeOpacityFn = () => 1;
    const nodeValFn = (node: GraphNode) => {
      return isSelectedNode(node) ? 8 : 1;
    };

    const linkColorFn = (link: GraphLink) => {
      if (highlightLinks.has(link)) return "#ffd166";
      return isHighlightActive() ? "#333a" : "#9aa";
    };
    const linkOpacityFn = (link: GraphLink) => {
      if (!isHighlightActive()) return 0.2 + 0.6 * (link.weight || 0);
      return highlightLinks.has(link) ? 0.95 : 0.08;
    };
    const linkWidthFn = (link: GraphLink) =>
      highlightLinks.has(link) ? 3 : 0.5 + 2.5 * (link.weight || 0);

    const createFG = ForceGraph3D as unknown as (el?: HTMLElement) => any;
    fg = createFG()(container.value)
      .backgroundColor("#000")
      .nodeColor(nodeColorFn)
      .nodeOpacity(nodeOpacityFn())
      .nodeVal(nodeValFn)
      .nodeLabel((node: GraphNode) => `Node ${node.id} (${node.summary})`)
      .linkColor(linkColorFn)
      .linkOpacity(linkOpacityFn)
      .linkWidth(linkWidthFn)
      .linkDirectionalParticles((l) => (highlightLinks.has(l) ? 2 : 0))
      .linkDirectionalParticleSpeed(0.004)
      .showNavInfo(false)
      .graphData(data)
      .linkLabel(
        (link: GraphLink) =>
          `MST (${link.report_type}) • sim=${(link.weight || 0).toFixed(2)}`,
      );

    // 좌표 고정
    fg.cooldownTime(0);

    // 노드 클릭 → 연결 성분 전체 하이라이트
    fg.onNodeClick((node: GraphNode) => {
      // modal data setting
      selectedDataMode.value = "node";

      if (lastClickedNode === node && isHighlightActive()) {
        resetHighlight();
        lastClickedNode = null;
        selectedData.value = null;
      } else {
        highlightComponentByNode(node); // ✨ 여기로 변경
        lastClickedNode = node;
        selectedData.value = node;
      }
      fg.refresh();

      // --- 더블클릭 감지 ---
      const now = performance.now();
      const isSameNode = lastClickNodeRef === node;
      if (isSameNode && now - lastClickAt < 300) {
        // 더블클릭으로 판단 → 카메라 이동
        focusCameraOnNode(node, /*distance=*/ 120, /*ms=*/ 1000);
        // 리셋
        lastClickAt = 0;
        lastClickNodeRef = null;
      } else {
        lastClickAt = now;
        lastClickNodeRef = node;
      }
    });

    // 링크 클릭 → 연결 성분 전체 하이라이트  ✅
    fg.onLinkClick((link: GraphLink) => {
      // modal data setting
      selectedDataMode.value = "link";
      selectedData.value = link;

      highlightComponentByLink(link);
      fg.refresh();
    });

    // 빈 공간 클릭 → 하이라이트 해제
    fg.onBackgroundClick(() => {
      resetHighlight();
      lastClickedNode = null;
      selectedData.value = null;
      fg.refresh();
    });

    // 리사이즈
    const resize = () => {
      const { width, height } = container.value.getBoundingClientRect();
      fg.width(width).height(height);
    };
    window.addEventListener("resize", resize);
    resizeOff = () => window.removeEventListener("resize", resize);
    setTimeout(resize);
  }

  // 그래프 갱신 시 인덱스도 다시
  fg.graphData(data);
  buildIndex(data);
  computeComponents(data);
  fg.refresh();
};

/*** 모달 설정 ***/
const selectedDataMode = ref<"node" | "link">("node");
const selectedData = ref<GraphNode | GraphLink | null>(null);
const isModalOpen = computed(() => {
  return selectedData.value !== null;
});

onMounted(async () => {
  await loadGraph();
  // timer = setInterval(loadGraph, 5000)
});

onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
  resizeOff();
  if (container.value) container.value.innerHTML = "";
});
</script>

<style scoped></style>
