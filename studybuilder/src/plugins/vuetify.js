import 'vuetify/styles'
import '@/styles/global.scss'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import { themeColors } from './theme.generated.js'

const NNCustomLightTheme = {
  dark: false,
  colors: themeColors,
}

export default createVuetify({
  defaults: {
    VBtn: {
      class: 'text-uppercase',
    },
    VTextField: {
      variant: 'outlined',
      density: 'compact',
      rounded: 'lg',
    },
    VTextarea: {
      variant: 'outlined',
      density: 'compact',
      rounded: 'lg',
    },
    VSelect: {
      variant: 'outlined',
      density: 'compact',
      rounded: 'lg',
    },
    VAutocomplete: {
      variant: 'outlined',
      density: 'compact',
      rounded: 'lg',
    },
    VCombobox: {
      variant: 'outlined',
      density: 'compact',
      rounded: 'lg',
    },
    VFileInput: {
      variant: 'outlined',
      density: 'compact',
      rounded: 'lg',
    },
    VNumberInput: {
      variant: 'outlined',
      density: 'compact',
      rounded: 'lg',
    },
    VCheckbox: {
      density: 'compact',
      color: 'primary',
    },
    VCheckboxBtn: {
      density: 'compact',
      color: 'primary',
    },
    VRadio: {
      density: 'compact',
      color: 'primary',
    },
    VRadioGroup: {
      density: 'compact',
      color: 'primary',
    },
    VSwitch: {
      density: 'compact',
      color: 'primary',
    },
  },
  theme: {
    defaultTheme: 'NNCustomLightTheme',
    themes: {
      NNCustomLightTheme,
    },
  },
})
