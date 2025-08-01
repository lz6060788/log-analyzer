import { ref, computed, onUnmounted } from 'vue'
import { debounce } from 'lodash-es'

// 拖拽配置接口
interface DraggableConfig {
  initialPosition: { x: number; y: number }
  boundary?: {
    minX?: number
    maxX?: number
    minY?: number
    maxY?: number
  }
  enabled?: boolean
  onDragStart?: () => void
  onDragMove?: (position: { x: number; y: number }) => void
  onDragEnd?: (position: { x: number; y: number }) => void
}

// 拖拽状态接口
interface DraggableState {
  position: { x: number; y: number }
  isDragging: boolean
  dragOffset: { x: number; y: number }
}

/**
 * 可复用的拖拽hook
 * @param config 拖拽配置
 * @returns 拖拽相关的状态和方法
 */
export function useDraggable(config: DraggableConfig) {
  // 响应式状态
  const position = ref(config.initialPosition)
  const isDragging = ref(false)
  const dragOffset = ref({ x: 0, y: 0 })
  const enabled = ref(config.enabled ?? true)

  // 计算样式 - 使用left/top定位
  const positionStyle = computed(() => ({
    left: `${position.value.x}px`,
    top: `${position.value.y}px`
  }))

  // 防抖处理位置更新
  const debouncedUpdatePosition = debounce((newX: number, newY: number) => {
    position.value = { x: newX, y: newY }
    // 调用回调
    config.onDragMove?.(position.value)
  }, 16, { leading: true, trailing: false, maxWait: 16 }) // 约60fps的更新频率

  // 开始拖拽
  const startDrag = (event: MouseEvent | TouchEvent) => {
    if (!enabled.value) return

    // 阻止默认行为，防止文本选择
    event.preventDefault()
    event.stopPropagation()

    isDragging.value = true
    const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
    const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY

    dragOffset.value = {
      x: clientX - position.value.x,
      y: clientY - position.value.y
    }

    // 添加事件监听器
    document.addEventListener('mousemove', onDrag)
    document.addEventListener('touchmove', onDrag, { passive: false })
    document.addEventListener('mouseup', stopDrag)
    document.addEventListener('touchend', stopDrag)

    // 调用回调
    config.onDragStart?.()
  }

  // 拖拽中 - 使用防抖优化
  const onDrag = (event: MouseEvent | TouchEvent) => {
    if (!isDragging.value) return

    // 阻止默认行为（如页面滚动）
    event.preventDefault()

    const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
    const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY

    let newX = clientX - dragOffset.value.x
    let newY = clientY - dragOffset.value.y

    // 边界限制
    const boundary = config.boundary || {}
    const minX = boundary.minX ?? 0
    const maxX = boundary.maxX ?? window.innerWidth
    const minY = boundary.minY ?? 0
    const maxY = boundary.maxY ?? window.innerHeight

    newX = Math.max(minX, Math.min(newX, maxX))
    newY = Math.max(minY, Math.min(newY, maxY))

    // 使用防抖更新位置
    debouncedUpdatePosition(newX, newY)
  }

  // 停止拖拽
  const stopDrag = () => {
    if (!isDragging.value) return

    isDragging.value = false

    // 取消防抖
    debouncedUpdatePosition.cancel()

    // 移除事件监听器
    document.removeEventListener('mousemove', onDrag)
    document.removeEventListener('touchmove', onDrag)
    document.removeEventListener('mouseup', stopDrag)
    document.removeEventListener('touchend', stopDrag)

    // 调用回调
    config.onDragEnd?.(position.value)
  }

  // 设置位置
  const setPosition = (newPosition: { x: number; y: number }) => {
    position.value = newPosition
  }

  // 启用/禁用拖拽
  const setEnabled = (enabledState: boolean) => {
    enabled.value = enabledState
  }

  // 组件卸载时清理事件监听器和防抖函数
  onUnmounted(() => {
    debouncedUpdatePosition.cancel()
    document.removeEventListener('mousemove', onDrag)
    document.removeEventListener('touchmove', onDrag)
    document.removeEventListener('mouseup', stopDrag)
    document.removeEventListener('touchend', stopDrag)
  })

  return {
    // 状态
    position: computed(() => position.value),
    isDragging: computed(() => isDragging.value),
    positionStyle,
    enabled: computed(() => enabled.value),

    // 方法
    startDrag,
    setPosition,
    setEnabled
  }
}
