<template>
  <div>
    <h1>Keyword Relationship Graph</h1>
    <div id="cy" style="width: 800px; height: 600px;"></div>
  </div>
</template>

<script>
import cytoscape from 'cytoscape';

export default {
  mounted() {
    // 그래프 데이터: 키워드 간 관계
    const elements = [
      {data: {id: '정치', label: '정치', locked: true}},
      {data: {id: '경제', label: '경제'}},
      {data: {id: '보건', label: '보건'}},
      {data: {id: '기술', label: '기술'}},
      {data: {id: '교육', label: '교육'}},
      {data: {id: '선거', label: '선거'}},
      {data: {id: '증권시장', label: '증권시장'}},
      {data: {id: '팬데믹', label: '팬데믹'}},
      {data: {id: '인공지능', label: '인공지능'}},
      {data: {id: '사이버보안', label: '사이버보안'}},
      {data: {id: '기후변화', label: '기후변화'}},
      {data: {id: '재생에너지', label: '재생에너지'}},
      {data: {id: '백신', label: '백신'}},
      {data: {id: '원격근무', label: '원격근무'}},
      {data: {id: '소셜미디어', label: '소셜미디어'}},
      {data: {id: '인플레이션', label: '인플레이션'}},
      {data: {id: '가상화폐', label: '가상화폐'}},
      {data: {id: '스타트업', label: '스타트업'}},
      {data: {id: '자동화', label: '자동화'}},
      {data: {id: '데이터프라이버시', label: '데이터프라이버시'}},

      {data: {source: '정치', target: '선거'}},
      {data: {source: '경제', target: '증권시장'}},
      {data: {source: '보건', target: '팬데믹'}},
      {data: {source: '기술', target: '인공지능'}},
      {data: {source: '기술', target: '사이버보안', label: '보안 문제'}},
      {data: {source: '기후변화', target: '재생에너지', label: '에너지 해결책'}},
      {data: {source: '팬데믹', target: '백신', label: '대응 전략'}},
      {data: {source: '원격근무', target: '소셜미디어', label: '온라인 소통'}},
      {data: {source: '인플레이션', target: '가상화폐', label: '대안 투자'}},
      {data: {source: '스타트업', target: '자동화', label: '혁신 기술'}},
      {data: {source: '데이터프라이버시', target: '사이버보안', label: '프라이버시 보호'}},
      {data: {source: '기후변화', target: '정치', label: '환경 정책'}},
      {data: {source: '증권시장', target: '경제', label: '금융 흐름'}},
      {data: {source: '가상화폐', target: '경제', label: '디지털 자산'}},
      {data: {source: '인공지능', target: '자동화', label: 'AI 활용'}},
      {data: {source: '소셜미디어', target: '데이터프라이버시', label: '데이터 이슈'}},
      {data: {source: '원격근무', target: '기술', label: '기술 지원'}},
      {data: {source: '백신', target: '보건', label: '공중 보건'}},
    ];

    // 노드 크기를 연결된 엣지 수에 따라 설정
    const nodeSizes = {};
    elements.forEach(element => {
      if (element.data.source) {
        nodeSizes[element.data.source] = (nodeSizes[element.data.source] || 0) + 5;
        nodeSizes[element.data.target] = (nodeSizes[element.data.target] || 0) + 5;
      }
    });

    const cy = cytoscape({
      container: document.getElementById('cy'),
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#0074D9',
            'label': 'data(label)',
            'color': '#fff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'width': ele => 10 + (nodeSizes[ele.data('id')] || 0) * 2,
            'height': ele => 10 + (nodeSizes[ele.data('id')] || 0) * 2
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#e7c5c4',
            'target-arrow-color': '#e7c5c4',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'text-rotation': 'autorotate'
          }
        }
      ],
      layout: {
        name: 'concentric',
        padding: 10
      }


    });

    // 특정 노드 고정
    const lockedNode = cy.getElementById('정치');
    lockedNode.position({ x: 400, y: 300 }); // 고정 위치 설정
    lockedNode.lock(); // 노드 이동 금지
  }
};
</script>

<style scoped>
h1 {
  text-align: center;
  margin-bottom: 20px;
}

#cy {
  border: 1px solid #ccc;
  margin: 0 auto;
}
</style>
