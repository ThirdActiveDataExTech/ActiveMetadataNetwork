<template>
  <div>
    <h1>키워드 관계 그래프 (Sigma.js)</h1>
    <div id="sigma-container" style="width: 800px; height: 600px; margin-top: 20px;"></div>
  </div>
</template>

<script>
import Sigma from 'sigma';
import Graph from 'graphology';

export default {
  mounted() {
    // 그래프 데이터
    const nodes = [
      { id: '정치', label: '정치' },
      { id: '경제', label: '경제' },
      { id: '보건', label: '보건' },
      { id: '기술', label: '기술' },
      { id: '교육', label: '교육' },
      { id: '선거', label: '선거' },
      { id: '증권시장', label: '증권시장' },
      { id: '팬데믹', label: '팬데믹' },
      { id: '인공지능', label: '인공지능' },
      { id: '사이버보안', label: '사이버보안' },
      { id: '기후변화', label: '기후변화' },
      { id: '재생에너지', label: '재생에너지' },
      { id: '백신', label: '백신' },
      { id: '원격근무', label: '원격근무' },
      { id: '소셜미디어', label: '소셜미디어' },
      { id: '인플레이션', label: '인플레이션' },
      { id: '가상화폐', label: '가상화폐' },
      { id: '스타트업', label: '스타트업' },
      { id: '자동화', label: '자동화' },
      { id: '데이터프라이버시', label: '데이터프라이버시' }
    ];

    const edges = [
      { source: '정치', target: '선거' },
      { source: '경제', target: '증권시장' },
      { source: '보건', target: '팬데믹' },
      { source: '기술', target: '인공지능' },
      { source: '기술', target: '사이버보안' },
      { source: '기후변화', target: '재생에너지' },
      { source: '팬데믹', target: '백신' },
      { source: '원격근무', target: '소셜미디어' },
      { source: '인플레이션', target: '가상화폐' },
      { source: '스타트업', target: '자동화' },
      { source: '데이터프라이버시', target: '사이버보안' },
      { source: '기후변화', target: '정치' },
      { source: '증권시장', target: '경제' },
      { source: '가상화폐', target: '경제' },
      { source: '인공지능', target: '자동화' },
      { source: '소셜미디어', target: '데이터프라이버시' },
      { source: '원격근무', target: '기술' },
      { source: '백신', target: '보건' }
    ];

    // Sigma.js 그래프
    const graph = new Graph();

    nodes.forEach(node => {
      graph.addNode(node.id, {
        label: node.label,
        x: Math.random() * 10,
        y: Math.random() * 10,
        size: 20,
        color: '#0074D9'
      });
    });

    edges.forEach(edge => {
      graph.addEdge(edge.source, edge.target, {
        size: 1,
        color: '#FF4136'
      });
    });

    const container = document.getElementById('sigma-container');
    new Sigma(graph, container);
  }
};
</script>

<style scoped>
h1 {
  text-align: center;
  margin-bottom: 20px;
}

#sigma-container {
  border: 1px solid #ccc;
  margin: 0 auto;
}
</style>
