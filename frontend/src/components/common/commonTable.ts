// commonTable.ts
import { computed, defineComponent, h, toRefs, useSlots, ref } from 'vue';
import { ElTable, ElTableColumn, ElPagination } from 'element-plus';

export default defineComponent({
  name: 'CommonTable',
  props: {
    data: {
      type: Array as () => Record<string, any>[],
      required: true,
      default: () => []
    }
  },
  setup(props) {
    const { data } = toRefs(props);
    const displayData = computed(() => {
      const start = (page.value - 1) * pageSize.value;
      const end = start + pageSize.value;
      return data.value.slice(start, end);
    });
    const page = ref(1);
    const pageSize = ref(10);
    const total = computed(() => props.data.length);
    
    // 计算所有列：遍历所有行收集所有可能的key
    const columns = computed(() => {
      if (props.data.length === 0) return [];
      
      const allKeys = new Set<string>();
      props.data.forEach(row => {
        if (row && typeof row === 'object') {
          Object.keys(row).forEach(key => {
            allKeys.add(key);
          });
        }
      });
      
      return Array.from(allKeys);
    });
    
    return () => {
      const slots = useSlots();

      return [
        h(ElTable, {
          data: displayData.value,
          style: { width: '100%' },
          maxHeight: '750px',
          border: true,
          stripe: true,
          size: 'small'
        }, () => [
          ...columns.value.map((key) => {
            return h(ElTableColumn, {
              key,
              prop: key,
              label: key.charAt(0).toUpperCase() + key.slice(1),
              showOverflowTooltip: true,
            }, {
              default: (scope: any) => slots[key] ? slots[key](scope) : scope.row[key]
            });
          }),
        ]),
        total.value > 10
        ? h(
            'div',
            {
              style: {
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'end',
                marginTop: '16px'
              },
            },
            [
              h(ElPagination, {
                total: total.value,
                layout: "total, sizes, prev, pager, next",
                'onUpdate:currentPage': (val: number) => {
                  page.value = val;
                },
                'onUpdate:pageSize': (val: number) => {
                  pageSize.value = val;
                },
                pageSize: pageSize.value,
                currentPage: page.value,
              }
              )
            ]
          )
        : undefined
      ];
    };
  }
});
