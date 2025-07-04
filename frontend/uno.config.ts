// uno.config.ts
import { defineConfig, presetAttributify, presetIcons } from 'unocss'
import { presetWind3 } from '@unocss/preset-wind3'

export default defineConfig({
  presets: [
    presetWind3(), // 默认预设
    presetAttributify(),
    presetIcons(),
  ],
  rules: [
  ],
  // 快捷方式
  shortcuts: {
  },
})
