<template>
  <div ref="container" class="graph-container"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import ForceGraph3D from '3d-force-graph'

const API_BASE = 'http://localhost:8800'
const container = ref(null)
let fg = null
let resizeOff = () => {}
let timer = null

// --- 하이라이트 상태 & 인덱스 ---
const highlightNodes = new Set()     // 노드 객체(Set)
const highlightLinks = new Set()     // 링크 객체(Set)
let lastClickedNode = null

let adj = new Map()           // nodeId -> Set(neighborId)
let incidentLinks = new Map() // nodeId -> Set(linkObj)

// 연결 성분 인덱스
let nodeIdToComp = new Map();    // nodeId -> compId
let compIdToNodeIds = new Map(); // compId -> Set(nodeId)
let compIdToLinks = new Map();   // compId -> Set(linkObj)

// 상단에 전역 상태 추가
let lastClickAt = 0;
let lastClickNodeRef = null;

// 카메라 이동 함수
function focusCameraOnNode(node, distance = 120, ms = 1000) {
  const distRatio = 1 + distance / Math.hypot(node.x || 1, node.y || 1, node.z || 1);
  fg.cameraPosition(
      { x: (node.x || 0) * distRatio, y: (node.y || 0) * distRatio, z: (node.z || 0) * distRatio },
      node,
      ms
  );
}

function getNodeId(n) {
  return typeof n === 'object' ? n.id : n
}
function getEndIds(l) {
  const s = typeof l.source === 'object' ? l.source.id : l.source
  const t = typeof l.target === 'object' ? l.target.id : l.target
  return [s, t]
}

function computeComponents(data) {
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
      for (const v of (adj.get(u) || [])) {
        if (!visited.has(v)) {
          visited.add(v);
          nodeSet.add(v);
          nodeIdToComp.set(v, cid);
          q.push(v);
        }
      }
      for (const l of (incidentLinks.get(u) || [])) {
        const [a, b] = getEndIds(l);
        if (nodeSet.has(a) && nodeSet.has(b)) linkSet.add(l);
      }
    }

    compIdToNodeIds.set(cid, nodeSet);
    compIdToLinks.set(cid, linkSet);
  }
}

function highlightComponentByNode(node) {
  resetHighlight();
  if (!node) return;
  const data = fg.graphData();
  const cid = nodeIdToComp.get(node.id);
  if (cid === undefined) return;

  for (const nid of (compIdToNodeIds.get(cid) || [])) {
    const obj = data.nodes.find(n => n.id === nid);
    if (obj) highlightNodes.add(obj);
  }
  for (const l of (compIdToLinks.get(cid) || [])) {
    highlightLinks.add(l);
  }
}

function highlightComponentByLink(link) {
  resetHighlight();
  if (!link) return;
  const data = fg.graphData();
  const [sId, tId] = getEndIds(link);
  const cid = nodeIdToComp.get(sId) ?? nodeIdToComp.get(tId);
  if (cid === undefined) return;
  for (const nid of (compIdToNodeIds.get(cid) || [])) {
    const obj = data.nodes.find(n => n.id === nid);
    if (obj) highlightNodes.add(obj);
  }
  for (const l of (compIdToLinks.get(cid) || [])) highlightLinks.add(l);
}


function buildIndex(data) {
  adj = new Map()
  incidentLinks = new Map()
  for (const n of data.nodes) {
    adj.set(n.id, new Set())
    incidentLinks.set(n.id, new Set())
  }
  for (const l of data.links) {
    const [a, b] = getEndIds(l)
    adj.get(a)?.add(b)
    adj.get(b)?.add(a)
    incidentLinks.get(a)?.add(l)
    incidentLinks.get(b)?.add(l)
  }
}
function resetHighlight() {
  highlightNodes.clear()
  highlightLinks.clear()
}
function activateNodeNeighborhood(node) {
  resetHighlight()
  if (!node) return
  // 자신 + 이웃 노드
  highlightNodes.add(node)
  const nbs = adj.get(node.id) || new Set()
  for (const nbId of nbs) {
    const nbObj = fg.graphData().nodes.find(n => n.id === nbId)
    if (nbObj) highlightNodes.add(nbObj)
  }
  // incident links
  for (const l of (incidentLinks.get(node.id) || new Set())) {
    highlightLinks.add(l)
  }
}
function activateLinkNeighborhood(link) {
  resetHighlight()
  if (!link) return
  const data = fg.graphData()
  const sId = typeof link.source === 'object' ? link.source.id : link.source
  const tId = typeof link.target === 'object' ? link.target.id : link.target
  const s = data.nodes.find(n => n.id === sId)
  const t = data.nodes.find(n => n.id === tId)
  if (s) {
    highlightNodes.add(s)
    for (const l of (incidentLinks.get(s.id) || new Set())) highlightLinks.add(l)
  }
  if (t) {
    highlightNodes.add(t)
    for (const l of (incidentLinks.get(t.id) || new Set())) highlightLinks.add(l)
  }
  highlightLinks.add(link) // 클릭한 링크 자체
}
function isHighlightActive() {
  return highlightNodes.size > 0 || highlightLinks.size > 0
}

async function loadGraph() {
  const res = await fetch(`${API_BASE}/graph`)
  const data = await res.json()

  // 인덱스 먼저 준비
  buildIndex(data)
  computeComponents(data);

  // 처음 생성 시
  if (!fg) {
    // 1) 그룹 → 고정 색상 매핑 (문자/숫자 모두 OK)
    function hashString(str) {
      // 간단하고 빠른 djb2 해시
      let h = 5381;
      for (let i = 0; i < str.length; i++) h = ((h << 5) + h) + str.charCodeAt(i);
      return h >>> 0; // unsigned
    }
    function colorFromGroup(group) {
      const g = String(group ?? 'unknown');
      const h = hashString(g);
      // hue는 0~359로, s/l은 고정(보기 좋은 파스텔/비비드 조절)
      const hue = h % 360;
      const sat = 100;  // 60~75 추천
      const lig =50;  // 45~60 추천
      return `hsl(${hue}, ${sat}%, ${lig}%)`;
    }

    const nodeColorFn = n => {
      const base = colorFromGroup(n.group);
      if (!isHighlightActive()) return base;              // 평소엔 그룹 고정색
      return highlightNodes.has(n) ? base : '#444';       // 비강조는 어둡게
    };

    const nodeOpacityFn = () => 1;

    const linkColorFn = l => {
      if (highlightLinks.has(l)) return '#ffd166'
      return isHighlightActive() ? '#333a' : '#9aa'
    }
    const linkOpacityFn = l => {
      if (!isHighlightActive()) return 0.2 + 0.6 * (l.weight || 0)
      return highlightLinks.has(l) ? 0.95 : 0.08
    }

    const linkWidthFn = l => highlightLinks.has(l) ? 3 : (0.5 + 2.5 * (l.weight || 0))

    // console.log(new Set(data.nodes.map(n => n.group)));
    console.log(nodeOpacityFn)

    fg = ForceGraph3D()(container.value)
        .backgroundColor('#000')
        .nodeAutoColorBy('group')                            // report_type별 색상
        .nodeColor(nodeColorFn)
        .nodeOpacity(nodeOpacityFn())
        .nodeLabel(n => `Node ${n.id} (${n.summary})`)
        .linkColor(linkColorFn)
        .linkOpacity(linkOpacityFn)
        .linkWidth(linkWidthFn)
        .linkDirectionalParticles(l => (highlightLinks.has(l) ? 2 : 0))
        .linkDirectionalParticleSpeed(0.004)
        .showNavInfo(false)
        .graphData(data)
        .linkLabel(l => `MST (${l.report_type}) • sim=${(l.weight||0).toFixed(2)}`)

    // 좌표 고정
    fg.cooldownTime(0)

    // 노드 클릭 → 연결 성분 전체 하이라이트
    fg.onNodeClick(node => {
      if (lastClickedNode === node && isHighlightActive()) {
        resetHighlight();
        lastClickedNode = null;
      } else {
        highlightComponentByNode(node);   // ✨ 여기로 변경
        lastClickedNode = node;
      }
      fg.refresh();

      // --- 더블클릭 감지 ---
      const now = performance.now();
      const isSameNode = lastClickNodeRef === node;
      if (isSameNode && (now - lastClickAt) < 300) {
        // 더블클릭으로 판단 → 카메라 이동
        focusCameraOnNode(node, /*distance=*/120, /*ms=*/1000);
        // 리셋
        lastClickAt = 0;
        lastClickNodeRef = null;
      } else {
        lastClickAt = now;
        lastClickNodeRef = node;
      }
    });

// 링크 클릭 → 연결 성분 전체 하이라이트  ✅
    fg.onLinkClick(link => {
      highlightComponentByLink(link);
      fg.refresh();
    });

    // 빈 공간 클릭 → 하이라이트 해제
    fg.onBackgroundClick(() => {
      resetHighlight()
      lastClickedNode = null
      fg.refresh()
    })

    // 리사이즈
    const resize = () => {
      const { width, height } = container.value.getBoundingClientRect()
      fg.width(width).height(height)
    }
    window.addEventListener('resize', resize)
    resizeOff = () => window.removeEventListener('resize', resize)
    setTimeout(resize)
  }

  // 그래프 갱신 시 인덱스도 다시
  fg.graphData(data)
  buildIndex(data)
  computeComponents(data);
  fg.refresh()
}

onMounted(async () => {
  await loadGraph()
  // timer = setInterval(loadGraph, 5000)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  resizeOff()
  if (container.value) container.value.innerHTML = ''
})
</script>

<style scoped>
.graph-container {
  /* width: 100%; */
  /* height: 95vh; */
  outline: 1px solid #222;
}
</style>