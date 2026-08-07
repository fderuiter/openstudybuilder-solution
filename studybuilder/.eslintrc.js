module.exports = {
  root: true,
  parserOptions: {
    sourceType: 'module',
    ecmaVersion: 2022,
  },
  globals: {
    globalThis: 'readonly',
  },
  env: {
    node: true,
  },
  extends: ['plugin:vue/vue3-recommended', 'eslint:recommended', 'plugin:vuejs-accessibility/recommended', 'prettier'],
  rules: {
    'vue/no-v-html': 'off',
    'vue/no-template-shadow': 'off',
    'vue/component-name-in-template-casing': [
      'error',
      'PascalCase',
      {
        registeredComponentsOnly: true,
        ignores: [],
      },
    ],
    'require-atomic-updates': 'off',
    'vuejs-accessibility/label-has-for': 'error',
    'vuejs-accessibility/click-events-have-key-events': 'error',
    'vuejs-accessibility/no-static-element-interactions': 'error',
    'vuejs-accessibility/mouse-events-have-key-events': 'error',
    'vuejs-accessibility/form-control-has-label': 'error',
  },
}
