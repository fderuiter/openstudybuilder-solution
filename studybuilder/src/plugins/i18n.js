import { createI18n } from 'vue-i18n'
import en from '@/locales/en.json'
import enUS from '@/locales/en-US.json'
import zhCN from '@/locales/zh-CN.json'
import es419 from '@/locales/es-419.json'
import ptBR from '@/locales/pt-BR.json'

const instance = createI18n({
  legacy: false,
  locale: import.meta.env.VUE_APP_I18N_LOCALE || 'en',
  fallbackLocale: import.meta.env.VUE_APP_I18N_FALLBACK_LOCALE || 'en',
  messages: {
    en: en,
    'en-US': enUS,
    'zh-CN': zhCN,
    es: es419,
    'es-419': es419,
    pt: ptBR,
    'pt-BR': ptBR,
  },
})

export default instance
export const i18n = instance.global
