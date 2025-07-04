<template>
  <div>
    <RouterView />
  </div>
</template>

<script lang="ts" setup>
import { RouterView } from 'vue-router'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Promotion } from '@element-plus/icons-vue'
import type { UploadProps, UploadRawFile } from 'element-plus'
// import axios from 'axios'

</script>

<style scoped>
</style>
