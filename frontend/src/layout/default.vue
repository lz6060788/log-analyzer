<template>
  <div class="default-layout">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
</script>

<style scoped>
.default-layout {
  max-width: 1280px;
  margin: 0 auto;
  padding: 16px;
  width: 100%;
  box-sizing: border-box;
}
</style>