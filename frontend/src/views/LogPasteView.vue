<template>
  <div class="log-paste-view">
    <p class="mb-2 text-gray-600">在此处粘贴日志内容，下方表格会进行解析并美化json内容</p>
    <MonacoEditor v-model="logText" height="400px" language="client-log" theme="client-log-theme" />
    <div class="log-list">
      <div class="w-full">
        <el-table :data="tableData" style="min-width: 800px; width: 100%" :default-sort="{prop: tableHeaders[0], order: 'ascending'}" border>
          <el-table-column v-if="hasAnyJson" label="操作" fixed="left" width="100">
            <template #default="{ row }">
              <el-button v-if="row.hasJson" size="small" @click="showJson(row.jsonStr)">查看JSON</el-button>
            </template>
          </el-table-column>
          <el-table-column v-if="hasAnyUuid" label="UUID" fixed="left" width="320">
            <template #default="{ row }">
              <copyText v-if="row.uuid" :text="row.uuid" />
            </template>
          </el-table-column>
          <el-table-column v-if="hasAnyMethod" label="Method" fixed="left" width="160">
            <template #default="{ row }">
              <copyText v-if="row.method" :text="row.method" />
            </template>
          </el-table-column>
          <el-table-column
            v-for="(header, idx) in tableHeaders"
            :key="idx"
            :prop="header.prop"
            :label="header.label"
            sortable
            :filters="header.filters"
            :filter-method="header.filterMethod"
            show-overflow-tooltip
            :width="200"
          >
            <template #default="{ row }">
              <div class="cell-ellipsis" :class="{highlight: row[header.prop + '_highlight']}" >{{ row[header.prop] }}</div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    <JsonViewerDialog v-model="jsonDialogVisible" :json="currentJson" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import MonacoEditor from '../components/common/MonacoEditor.vue';
import JsonViewerDialog from '../components/common/JsonViewerDialog.vue';
import { parseClientLogLines } from '../composable/clientLogParser';
import copyText from '../components/common/copyText.vue';

const props = defineProps<{
  logText?: string;
}>();

const logText = ref(props.logText || '');
const parsedLogs = computed(() => parseClientLogLines(logText.value));

// 生成表头及筛选项
const tableHeaders = computed(() => {
  if (parsedLogs.value.length > 0) {
    // 假设fields为[{value, highlight}...]
    const fieldCount = parsedLogs.value[0].fields.length;
    return Array.from({ length: fieldCount }, (_, idx) => {
      const prop = `field${idx+1}`;
      // 生成筛选项
      const values = Array.from(new Set(parsedLogs.value.map(log => log.fields[idx]?.value)));
      return {
        prop,
        label: `字段${idx+1}`,
        filters: values.map(v => ({ text: v, value: v })),
        filterMethod: (value: string, row: any) => row[prop] === value
      };
    });
  }
  return [];
});

// 适配el-table的数据结构
const tableData = computed(() => {
  return parsedLogs.value.map(log => {
    const obj: Record<string, any> = { hasJson: log.hasJson, jsonStr: log.jsonStr };
    if (log.uuid) obj.uuid = log.uuid;
    if (log.method) obj.method = log.method;
    log.fields.forEach((f, idx) => {
      obj[`field${idx+1}`] = f.value;
      obj[`field${idx+1}_highlight`] = f.highlight;
    });
    return obj;
  });
});

const hasAnyJson = computed(() => parsedLogs.value.some(log => log.hasJson));
const hasAnyUuid = computed(() => parsedLogs.value.some(log => !!log.uuid));
const hasAnyMethod = computed(() => parsedLogs.value.some(log => !!log.method));

const jsonDialogVisible = ref(false);
const currentJson = ref('');
function showJson(json: string | undefined) {
  if (json) {
    currentJson.value = json;
    jsonDialogVisible.value = true;
  }
}
</script>

<style scoped>
.log-list {
  margin-top: 24px;
}
.cell-ellipsis {
  width: 100%;
  display: block;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: bottom;
}
.highlight {
  color: #d97706;
  font-weight: bold;
}
</style>
