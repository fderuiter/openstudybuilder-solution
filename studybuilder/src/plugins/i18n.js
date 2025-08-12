import { createI18n } from 'vue-i18n'
import en from '@/locales/en.json'
import enUS from '@/locales/en-US.json'
import zhCN from '@/locales/zh-CN.json'
import es419 from '@/locales/es-419.json'
import deDE from '@/locales/de-DE.json'
import frFR from '@/locales/fr-FR.json'
import koKR from '@/locales/ko-KR.json'

const instance = createI18n({
  legacy: false,
  locale: import.meta.env.VUE_APP_I18N_LOCALE || 'en',
  fallbackLocale: import.meta.env.VUE_APP_I18N_FALLBACK_LOCALE || 'en',
  messages: {
    en: en,
    'en-US': enUS,
    zh: zhCN,
    'zh-CN': zhCN,
    es: es419,
    'es-419': es419,
    de: deDE,
    'de-DE': deDE,
    fr: frFR,
    'fr-FR': frFR,
    ko: koKR,
    'ko-KR': koKR,
  },
})

export default instance
export const i18n = instance.global
