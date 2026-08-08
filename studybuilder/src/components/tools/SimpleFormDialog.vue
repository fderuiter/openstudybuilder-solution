<template>
  <v-dialog
    :model-value="open"
    :scrollable="scrollable"
    persistent
    :max-width="maxWidth"
    v-bind="$attrs"
    @keydown.esc="cancel"
  >
    <v-card data-cy="form-body" elevation="0" rounded="xl">
      <v-card-title class="d-flex align-center">
        <span class="dialog-title">{{ title }}</span>
        <HelpButtonWithPanels
          v-if="helpItems"
          :title="$t('_global.help')"
          :help-text="helpText"
          :items="helpItems"
        />
        <v-btn
          v-if="formUrl"
          color="secondary"
          class="ml-2 text-label-large"
          size="small"
          @click="copyUrl"
        >
          {{ $t('_global.copy_link') }}
        </v-btn>
        <v-spacer />
        <v-btn
          v-if="topRightCancel"
          icon="mdi-close"
          variant="text"
          @click="cancel"
        />
      </v-card-title>
      <v-divider />
      <v-card-text>
        <slot name="body" />
      </v-card-text>
      <v-divider />
      <v-card-actions class="pr-6 my-2">
        <v-spacer />
        <div>
          <slot name="actions" />
        </div>
        <div v-if="!noDefaultActions">
          <v-btn
            data-cy="cancel-button"
            :disabled="actionDisabled"
            variant="outlined"
            rounded
            class="mr-2"
            elevation="0"
            width="120px"
            @click="cancel"
          >
            {{ cancelLabel ?? $t('_global.cancel') }}
          </v-btn>
          <v-btn
            v-if="formStore.canUndo"
            data-cy="undo-button"
            color="primary"
            variant="outlined"
            rounded
            class="mr-2"
            elevation="0"
            @click="undo"
          >
            <v-icon class="mr-1">mdi-undo</v-icon>
            {{ $t('_global.undo') }}
          </v-btn>
          <v-btn
            v-if="formStore.canRedo"
            data-cy="redo-button"
            color="primary"
            variant="outlined"
            rounded
            class="mr-2"
            elevation="0"
            @click="redo"
          >
            <v-icon class="mr-1">mdi-redo</v-icon>
            {{ $t('_global.redo') }}
          </v-btn>
          <v-btn
            v-if="!noSaving"
            data-cy="save-button"
            color="secondary"
            variant="flat"
            min-width="120px"
            :loading="working"
            :disabled="actionDisabled"
            rounded
            @click="submit"
          >
            {{ actionButtonLabel }}
          </v-btn>
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <ConfirmDialog ref="confirmRef" :text-cols="6" :action-cols="5" />
</template>

<script setup>
import { computed, getCurrentInstance, ref, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useFormStore } from '@/stores/form'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels.vue'

const { t } = useI18n()

const props = defineProps({
  actionLabel: {
    type: String,
    default: null,
  },
  title: {
    type: String,
    default: '',
  },
  helpItems: {
    type: Array,
    default: null,
  },
  helpText: {
    type: String,
    required: false,
    default: '',
  },
  open: Boolean,
  maxWidth: {
    type: String,
    default: '800px',
  },
  noSaving: {
    type: Boolean,
    default: false,
  },
  formUrl: {
    type: String,
    default: '',
  },
  scrollable: {
    type: Boolean,
    default: true,
  },
  noDefaultActions: {
    type: Boolean,
    default: false,
  },
  topRightCancel: {
    type: Boolean,
    default: false,
  },
  cancelLabel: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['close', 'submit'])

const confirmRef = ref(null)
const actionDisabled = ref(false)
const working = ref(false)
const instance = getCurrentInstance()

const actionButtonLabel = computed(() => {
  return props.actionLabel ? props.actionLabel : t('_global.save')
})

watch(
  () => props.open,
  (isOpen) => {
    working.value = false
    if (isOpen) {
      const formObj = getParentForm()
      if (formObj) {
        const rawForm = typeof formObj.value !== 'undefined' ? formObj.value : formObj
        formStore.save(rawForm)
      }
    } else {
      formStore.reset()
    }
  }
)

const formStore = useFormStore()

const getParentForm = () => {
  if (!instance || !instance.parent) return null
  const setupState = instance.parent.setupState
  if (setupState && setupState.form) {
    return setupState.form
  }
  const proxy = instance.parent.proxy
  if (proxy && proxy.form) {
    return proxy.form
  }
  return null
}

let isUpdatingFromStore = false

// Set up watcher on parent's form to push updates to formStore
watch(
  () => {
    const formObj = getParentForm()
    if (!formObj) return null
    return typeof formObj.value !== 'undefined' ? formObj.value : formObj
  },
  (newVal) => {
    if (isUpdatingFromStore) return
    if (newVal && props.open) {
      formStore.pushState(newVal)
    }
  },
  { deep: true }
)

// Watch for store form changes (like undo, redo, rollback) and apply back to parent
watch(
  () => formStore.form,
  (newStoreForm) => {
    const parentForm = getParentForm()
    if (parentForm) {
      const rawForm = typeof parentForm.value !== 'undefined' ? parentForm.value : parentForm
      if (newStoreForm && JSON.stringify(rawForm) !== JSON.stringify(newStoreForm)) {
        isUpdatingFromStore = true
        if (typeof parentForm.value !== 'undefined') {
          parentForm.value = JSON.parse(JSON.stringify(newStoreForm))
        } else {
          for (const key in parentForm) {
            delete parentForm[key]
          }
          Object.assign(parentForm, JSON.parse(JSON.stringify(newStoreForm)))
        }
        setTimeout(() => {
          isUpdatingFromStore = false
        }, 0)
      }
    }
  },
  { deep: true }
)

onMounted(() => {
  if (props.open) {
    const formObj = getParentForm()
    if (formObj) {
      const rawForm = typeof formObj.value !== 'undefined' ? formObj.value : formObj
      formStore.save(rawForm)
    }
  }
})

function undo() {
  const reverted = formStore.undo()
  if (reverted) {
    isUpdatingFromStore = true
    const formObj = getParentForm()
    if (formObj) {
      if (typeof formObj.value !== 'undefined') {
        formObj.value = JSON.parse(JSON.stringify(reverted))
      } else {
        for (const key in formObj) {
          delete formObj[key]
        }
        Object.assign(formObj, JSON.parse(JSON.stringify(reverted)))
      }
    }
    setTimeout(() => {
      isUpdatingFromStore = false
    }, 0)
  }
}

function redo() {
  const reverted = formStore.redo()
  if (reverted) {
    isUpdatingFromStore = true
    const formObj = getParentForm()
    if (formObj) {
      if (typeof formObj.value !== 'undefined') {
        formObj.value = JSON.parse(JSON.stringify(reverted))
      } else {
        for (const key in formObj) {
          delete formObj[key]
        }
        Object.assign(formObj, JSON.parse(JSON.stringify(reverted)))
      }
    }
    setTimeout(() => {
      isUpdatingFromStore = false
    }, 0)
  }
}

function copyUrl() {
  navigator.clipboard.writeText(props.formUrl)
}

function cancel() {
  working.value = false
  emit('close')
}

async function confirm(message, options) {
  return await confirmRef.value.open(message, options)
}

async function submit() {
  const observer = instance?.proxy?.$parent?.$refs?.observer
  if (observer) {
    const { valid } = await observer.validate()
    if (!valid) {
      return
    }
  }
  working.value = true

  // Record save-point before starting API operation
  const formObj = getParentForm()
  if (formObj) {
    const rawForm = typeof formObj.value !== 'undefined' ? formObj.value : formObj
    formStore.saveCheckpoint(rawForm)
  }

  emit('submit')
}

defineExpose({
  actionDisabled,
  working,
  copyUrl,
  cancel,
  confirm,
  submit,
})
</script>
