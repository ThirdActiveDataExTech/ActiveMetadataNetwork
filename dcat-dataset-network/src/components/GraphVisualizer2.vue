<template>
  <div>
    <h1>키워드 관계 그래프 (D3.js)</h1>
    <div id="d3-container" style="width: 800px; height: 600px;"></div>
  </div>
</template>

<script>
import * as d3 from 'd3';

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

    // D3.js 그래프
    const d3Container = d3.select('#d3-container');
    const svg = d3Container.append('svg')
        .attr('width', 800)
        .attr('height', 600)
        .call(
            d3.zoom().on('zoom', (event) => {
              svg.attr('transform', event.transform);
            })
        )
        .append('g');

    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(edges).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(400, 300));

    const link = svg.append('g')
        .selectAll('line')
        .data(edges)
        .enter().append('line')
        .attr('stroke', '#999')
        .attr('stroke-width', 2);

    const node = svg.append('g')
        .selectAll('circle')
        .data(nodes)
        .enter().append('circle')
        .attr('r', 10)
        .attr('fill', '#0074D9')
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragged)
            .on('end', dragEnded));

    const labels = svg.append('g')
        .selectAll('text')
        .data(nodes)
        .enter().append('text')
        .text(d => d.label)
        .attr('x', 12)
        .attr('y', 3)
        .attr('fill', '#fff');

    simulation.on('tick', () => {
      link.attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y);

      node.attr('cx', d => d.x).attr('cy', d => d.y);
      labels.attr('x', d => d.x).attr('y', d => d.y);
    });

    function dragStarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragEnded(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

  }
};
</script>

<style scoped>
h1 {
  text-align: center;
  margin-bottom: 20px;
}

#d3-container{
  border: 1px solid #ccc;
  margin: 0 auto;
}
</style>
