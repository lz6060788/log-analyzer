<template>
  <el-text v-if="!copied" @click="copyText" type="primary" class="cursor-pointer transition-colors">
    {{ text }}
  </el-text>
  <el-text v-else type="success">
    已复制!
  </el-text>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';

const props = defineProps<{
  text: string;
}>();

const copied = ref(false);

const copyText = async () => {
  try {
    await navigator.clipboard.writeText(props.text);
    copied.value = true;
    ElMessage.success('复制成功');

    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch (error) {
    ElMessage.error('复制失败');
    console.error('Copy failed:', error);
  }
};
</script>
