<template>
  <v-card color="bg-dfltBackground">
    <v-card-actions>
      <v-card-title class="dialog-about-title">
        {{ props.title }}
      </v-card-title>
      <v-spacer />
      <v-btn
        variant="outlined"
        rounded
        elevation="0"
        color="nnBaseBlue"
        class="mr-4"
        @click="emit('close')"
      >
        {{ $t('_global.close') }}
      </v-btn>
    </v-card-actions>
    <v-card-text>
      <span id="license" v-html="sanitizeHTML(licenseContent)" />
    </v-card-text>
  </v-card>
</template>

<script setup>
import { marked } from 'marked'
import { sanitizeHTML } from '@/utils/sanitize'
import { computed } from 'vue'

const props = defineProps({
  rawMarkdown: {
    type: String,
    default: '',
  },
  title: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['close'])

const licenseContent = computed(() => {
  return marked.parse(props.rawMarkdown)
})
</script>
<style>
#license {
  pre {
    white-space: break-spaces;
  }
}
</style>
