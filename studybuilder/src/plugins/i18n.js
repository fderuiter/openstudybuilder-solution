import { createI18n } from 'vue-i18n'
import en from '@/locales/en.json'
import enUS from '@/locales/en-US.json'
import es from '@/locales/es.json'

const instance = createI18n({
  legacy: false,
  locale: import.meta.env.VUE_APP_I18N_LOCALE || 'en',
  fallbackLocale: import.meta.env.VUE_APP_I18N_FALLBACK_LOCALE || 'en',
  messages: {
    en: en,
    'en-US': enUS,
    es: es,
  },
})

export default instance
export const i18n = instance.global
