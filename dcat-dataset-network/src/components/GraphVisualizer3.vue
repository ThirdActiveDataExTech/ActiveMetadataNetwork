<template>
  <div>
    <h1>키워드 관계 그래프 Vis.js</h1>
    <div id="vis-container" style="width: 800px; height: 600px; margin-top: 20px;"></div>
  </div>
</template>

<script>
import { Network } from 'vis-network';

export default {
  data() {
    return {
      nodes: [
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
      ],

      edges: [
        { from: '정치', to: '선거' },
        { from: '경제', to: '증권시장' },
        { from: '보건', to: '팬데믹' },
        { from: '기술', to: '인공지능' },
        { from: '기술', to: '사이버보안' },
        { from: '기후변화', to: '재생에너지' },
        { from: '팬데믹', to: '백신' },
        { from: '원격근무', to: '소셜미디어' },
        { from: '인플레이션', to: '가상화폐' },
        { from: '스타트업', to: '자동화' },
        { from: '데이터프라이버시', to: '사이버보안' },
        { from: '기후변화', to: '정치' },
        { from: '증권시장', to: '경제' },
        { from: '가상화폐', to: '경제' },
        { from: '인공지능', to: '자동화' },
        { from: '소셜미디어', to: '데이터프라이버시' },
        { from: '원격근무', to: '기술' },
        { from: '백신', to: '보건' }
      ],

      options: {
        manipulation: {
          enabled: true,
          initiallyActive: true,
        },
        nodes: {
          physics: true,
        }
      },
      container: "",
      network: null,
    };
  },
  computed: {
    graph_data() {
      return {
        nodes: this.nodes,
        edges: this.edges
      }
    }
  },
  mounted() {
    this.container = document.getElementById("vis-container");

    this.network = new Network(
        this.container,
        this.graph_data,
        this.options
    );
  },
};
</script>

<style scoped>
h1 {
  text-align: center;
  margin-bottom: 20px;
}

#vis-container {
  border: 1px solid #ccc;
  margin: 0 auto;
}
</style>
