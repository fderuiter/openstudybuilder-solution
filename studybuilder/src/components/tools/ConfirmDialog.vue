<template>
  <v-dialog
    :model-value="dialog"
    :max-width="options.width"
    persistent
    :style="{ zIndex: options.zIndex }"
    @keydown.esc="cancel"
  >
    <v-card :border="cardClasses" class="pa-1" style="border-radius: 20px">
      <v-card-title v-if="options.title" class="dialogText">
        {{ options.title }}
      </v-card-title>
      <v-card-text v-if="savedMessage" class="pt-2 dialogText">
        <v-row no-gutters class="align-center pa-2">
          <v-col cols="12">
            <slot name="body">
              <div
                class="text-body-large mt-1"
                v-html="sanitizeHTML(savedMessage)"
              />
            </slot>

            <!-- Affected Studies List Section -->
            <div
              v-if="options.affectedStudies && options.affectedStudies.length > 0"
              class="mt-4 mb-4"
            >
              <v-text-field
                v-model="searchQuery"
                density="compact"
                label="Search affected studies..."
                variant="outlined"
                clearable
                hide-details
                class="mb-3"
              />
              <div
                style="max-height: 250px; overflow-y: auto; border: 1px solid #ccc; border-radius: 8px;"
                class="pa-2 grey lighten-4"
              >
                <div
                  v-for="study in filteredStudies"
                  :key="study.uid"
                  class="py-1 border-bottom-1"
                  style="font-size: 14px; border-bottom: 1px solid #f0f0f0; color: inherit; text-align: left;"
                >
                  <strong>{{ study.acronym || 'No Acronym' }}</strong>
                  <span v-if="study.subpart_acronym"> / {{ study.subpart_acronym }}</span>
                  <span v-if="study.id" class="text-grey-darken-1"> (ID: {{ study.id }})</span>
                </div>
                <div
                  v-if="filteredStudies.length === 0"
                  class="text-center py-4 text-grey"
                >
                  No matching studies found
                </div>
              </div>
            </div>

            <!-- Mandatory Acknowledgement Checkbox -->
            <v-checkbox
              v-if="options.requireAcknowledgement"
              v-model="acknowledged"
              label="I acknowledge the impact of this cascading update on the listed studies"
              hide-details
              class="mt-3 mb-2"
            />
          </v-col>
        </v-row>
        <v-divider class="pa-2" />
        <v-row>
          <v-col class="text-center">
            <v-btn
              v-if="!options.noCancel"
              :color="options.cancelIsPrimaryAction ? btnClasses : ''"
              :variant="options.cancelIsPrimaryAction ? 'elevated' : 'outlined'"
              :disabled="props.cancelDisabled"
              data-cy="cancel-popup"
              class="mr-4"
              rounded="xl"
              @click="cancel"
            >
              {{ options.cancelLabel }}
            </v-btn>
            <slot name="actions">
              <v-btn
                v-if="options.redirect === null"
                :color="options.cancelIsPrimaryAction ? '' : btnClasses"
                :variant="
                  options.cancelIsPrimaryAction ? 'outlined' : 'elevated'
                "
                :disabled="props.agreeDisabled || (options.requireAcknowledgement && !acknowledged)"
                rounded="xl"
                data-cy="continue-popup"
                @click="agree"
              >
                {{ options.agreeLabel }}
              </v-btn>
              <v-btn
                v-else
                data-cy="continue-popup"
                :color="options.cancelIsPrimaryAction ? '' : btnClasses"
                :variant="
                  options.cancelIsPrimaryAction ? 'outlined' : 'elevated'
                "
                :disabled="props.agreeAndRedirectDisabled || (options.requireAcknowledgement && !acknowledged)"
                rounded="xl"
                @click="agreeAndRedirect"
              >
                {{ options.agreeLabel }}
              </v-btn>
            </slot>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { escapeHTML, sanitizeHTML } from '@/utils/sanitize'

const { t } = useI18n()
const router = useRouter()

const props = defineProps({
  cancelDisabled: { type: Boolean, default: false },
  agreeDisabled: { type: Boolean, default: false },
  agreeAndRedirectDisabled: { type: Boolean, default: false },
})

const dialog = ref(false)
let savedResolve = null
const savedMessage = ref(null)

const defaultOptions = {
  title: null,
  type: 'success',
  width: 450,
  zIndex: 3000,
  noCancel: false,
  agreeLabel: t('_global.continue'),
  cancelLabel: t('_global.cancel'),
  cancelIsPrimaryAction: false,
  redirect: null,
  affectedStudies: null,
  requireAcknowledgement: false,
}

const options = ref(Object.assign({}, defaultOptions))

const searchQuery = ref('')
const acknowledged = ref(false)

const filteredStudies = computed(() => {
  if (!options.value.affectedStudies) return []
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return options.value.affectedStudies
  return options.value.affectedStudies.filter((study) => {
    const acronym = (study.acronym || '').toLowerCase()
    const subpart = (study.subpart_acronym || '').toLowerCase()
    const id = (study.id || '').toLowerCase()
    const uid = (study.uid || '').toLowerCase()
    return acronym.includes(query) || subpart.includes(query) || id.includes(query) || uid.includes(query)
  })
})

const cardClasses = computed(() => {
  return btnClasses.value + ' lg opacity-100'
})
const btnClasses = computed(() => {
  if (options.value.type === 'error') {
    return 'error'
  } else if (options.value.type === 'warning') {
    return 'warning'
  } else if (options.value.type === 'info') {
    return 'info'
  } else {
    return 'success'
  }
})

const open = (messagePlain, extraOptions, callback) => {
  dialog.value = true
  acknowledged.value = false
  searchQuery.value = ''
  savedMessage.value = escapeHTML(messagePlain).replace(/\n+/g, '<br />')
  options.value = Object.assign({}, defaultOptions, extraOptions)

  callback?.()

  return new Promise((resolve) => {
    savedResolve = resolve
  })
}
const openHtml = (messageHtml, extraOptions, callback) => {
  dialog.value = true
  acknowledged.value = false
  searchQuery.value = ''
  savedMessage.value = messageHtml
  options.value = Object.assign({}, defaultOptions, extraOptions)

  callback?.()

  return new Promise((resolve) => {
    savedResolve = resolve
  })
}
const agree = () => {
  savedResolve(true)
  dialog.value = false
}
const agreeAndRedirect = () => {
  dialog.value = false
  router.push(options.value.redirect)
}
const cancel = () => {
  savedResolve(false)
  dialog.value = false
}

defineExpose({
  open,
  openHtml,
  cancel,
})
</script>
<style>
.dialogText {
  color: rgb(var(--v-theme-nnTrueBlue));
}
</style>
