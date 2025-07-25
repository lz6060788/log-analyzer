<template>
  <el-dialog v-model="visible" title="JSON查看" width="60%" @close="onClose">
    <monaco-editor
      v-if="visible"
      v-model="jsonText"
      language="json"
      :readonly="true"
      height="400px"
    />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import MonacoEditor from './MonacoEditor.vue';

const props = defineProps<{
  modelValue: boolean;
  json: string;
}>();
const emit = defineEmits(['update:modelValue']);

const visible = ref(props.modelValue);
const jsonText = ref('');

watch(() => props.modelValue, (val) => {
  visible.value = val;
});
watch(() => props.json, (val) => {
  try {
    jsonText.value = JSON.stringify(JSON.parse(val), null, 2);
  } catch {
    jsonText.value = val;
  }
}, { immediate: true });

function onClose() {
  emit('update:modelValue', false);
}
</script> 
