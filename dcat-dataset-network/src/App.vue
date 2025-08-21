<script setup>
import GraphVisualizer from "@/components/GraphVisualizer.vue";
import GraphVisualizer2 from "@/components/GraphVisualizer2.vue";
import GraphVisualizer3 from "@/components/GraphVisualizer3.vue";
import GraphVisualizer4 from "@/components/GraphVisualizer4.vue";
import Cystoscape from "@/components/Cystoscape.vue";
import DcatKeywordGraph from "@/components/DcatKeywordGraph.vue";
</script>

<template>
  <main>
    <DcatKeywordGraph/>
<!--    <GraphVisualizer />-->
<!--    <GraphVisualizer2 />-->
<!--    <GraphVisualizer3 />-->
<!--    <GraphVisualizer4 />-->
<!--    <Cystoscape/>-->
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
