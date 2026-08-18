<template>
  <v-dialog v-model="dialogVisible" max-width="550" persistent style="z-index: 9999;">
    <v-card class="pa-2" style="border-radius: 16px;">
      <v-card-title class="d-flex align-center dialogText">
        <v-icon color="warning" size="large" class="mr-2">mdi-alert-circle-outline</v-icon>
        {{ t('_session.expired_title') }}
      </v-card-title>
      <v-card-text class="pt-2">
        <p class="text-body-1 mb-4">
          {{ t('_session.expired_message') }}
        </p>
      </v-card-text>
      <v-divider class="mb-4" />
      <v-card-actions class="d-flex justify-end ga-2 flex-wrap">
        <v-btn
          variant="outlined"
          color="secondary"
          rounded="xl"
          prepend-icon="mdi-content-copy"
          data-cy="copy-unsaved-data"
          @click="copyUnsavedData"
        >
          {{ t('_session.copy_unsaved_data') }}
        </v-btn>
        <v-btn
          variant="elevated"
          color="primary"
          rounded="xl"
          prepend-icon="mdi-login"
          data-cy="reauthenticate-btn"
          @click="reauthenticate"
        >
          {{ t('_session.reauthenticate') }}
        </v-btn>
        <v-btn
          variant="text"
          rounded="xl"
          @click="close"
        >
          {{ t('_global.cancel') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, inject, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useFormStore } from '@/stores/form'
import { notificationHub } from '@/plugins/notificationHub'

const { t } = useI18n()
const dialogVisible = ref(false)
const targetRoute = ref(null)

const eventBus = inject('eventBus')
const $auth = inject('$auth')

if (eventBus) {
  watch(
    () => eventBus.value.get('showSessionExpirationModal'),
    (eventData) => {
      if (eventData) {
        targetRoute.value = eventData[0]?.to || null
      }
      dialogVisible.value = true
    }
  )
}

const copyUnsavedData = async () => {
  try {
    const formStore = useFormStore()
    const formContent = formStore.form ? JSON.stringify(formStore.form, null, 2) : ''
    await navigator.clipboard.writeText(formContent)
    notificationHub.add({
      msg: t('_session.data_copied'),
      type: 'success',
    })
  } catch (err) {
    console.error('Failed to copy unsaved data to clipboard:', err)
    notificationHub.add({
      msg: t('_session.copy_failed'),
      type: 'error',
    })
  }
}

const reauthenticate = () => {
  dialogVisible.value = false
  if ($auth && typeof $auth.signinRedirect === 'function') {
    $auth.signinRedirect(targetRoute.value)
  }
}

const close = () => {
  dialogVisible.value = false
}
</script>

<style scoped>
.dialogText {
  color: rgb(var(--v-theme-nnTrueBlue));
}
</style>
