<template>
  <v-card class="rounded-0">
    <v-card-title class="d-flex align-center py-4 px-6">
      <span class="text-h6 font-weight-bold">
        {{ $t('StudyDataStandardVersionsView.tab2_title') }}
      </span>
      <v-spacer />
      <v-btn
        class="ml-2"
        size="small"
        variant="outlined"
        color="nnBaseBlue"
        :title="$t('NNTableTooltips.history')"
        icon="mdi-history"
        data-cy="show-dictionary-history"
        @click="openGlobalHistory"
      />
    </v-card-title>

    <v-card-text class="px-6 pb-6">
      <div v-if="loading" class="d-flex justify-center align-center py-8">
        <v-progress-circular indeterminate color="primary" />
      </div>

      <div v-else-if="items.length === 0" class="py-6 text-center">
        <v-alert
          type="info"
          variant="tonal"
          class="mb-0"
        >
          No Controlled Terminology standard versions are configured for this study. Please select a CDISC Controlled Terminology package in the "Controlled Terminology" tab first to configure dictionary versions.
        </v-alert>
      </div>

      <v-table v-else class="dictionary-table border">
        <thead>
          <tr>
            <th class="text-left font-weight-bold" style="width: 20%">
              {{ $t('CTStandardVersionsTable.ct_catalogue') }}
            </th>
            <th class="text-left font-weight-bold" style="width: 20%">
              {{ $t('CTStandardVersionsTable.cdisc_ct_package') }}
            </th>
            <th class="text-left font-weight-bold" style="width: 15%">
              SNOMED Version
            </th>
            <th class="text-left font-weight-bold" style="width: 15%">
              MED-RT Version
            </th>
            <th class="text-left font-weight-bold" style="width: 15%">
              UNII Version
            </th>
            <th class="text-left font-weight-bold" style="width: 15%">
              UCUM Version
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.uid">
            <td class="font-weight-medium">
              {{ item.ct_package?.catalogue_name }}
            </td>
            <td>
              {{ item.ct_package?.extends_package || item.ct_package?.name }}
            </td>
            <td>
              <v-select
                v-model="item.snomed_version"
                :items="snomedOptions"
                :disabled="isReadOnly"
                density="compact"
                hide-details
                variant="outlined"
                color="primary"
                @update:model-value="saveItem(item, 'snomed_version')"
              />
            </td>
            <td>
              <v-select
                v-model="item.medrt_version"
                :items="medrtOptions"
                :disabled="isReadOnly"
                density="compact"
                hide-details
                variant="outlined"
                color="primary"
                @update:model-value="saveItem(item, 'medrt_version')"
              />
            </td>
            <td>
              <v-select
                v-model="item.unii_version"
                :items="uniiOptions"
                :disabled="isReadOnly"
                density="compact"
                hide-details
                variant="outlined"
                color="primary"
                @update:model-value="saveItem(item, 'unii_version')"
              />
            </td>
            <td>
              <v-select
                v-model="item.ucum_version"
                :items="ucumOptions"
                :disabled="isReadOnly"
                density="compact"
                hide-details
                variant="outlined"
                color="primary"
                @update:model-value="saveItem(item, 'ucum_version')"
              />
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card-text>
  </v-card>

  <v-dialog
    v-model="showHistory"
    persistent
    :fullscreen="$globals.historyDialogFullscreen"
    @keydown.esc="closeHistory"
  >
    <HistoryTable
      :title="historyTitle"
      :headers="historyHeaders"
      :items="historyItems"
      @close="closeHistory"
    />
  </v-dialog>
</template>

<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import { useAccessGuard } from '@/composables/accessGuard'
import HistoryTable from '@/components/tools/HistoryTable.vue'
import api from '@/api/study.js'

const { t } = useI18n()
const studiesGeneralStore = useStudiesGeneralStore()
const notificationHub = inject('notificationHub')
const roles = inject('roles')
const { checkPermission } = useAccessGuard()

const items = ref([])
const historyItems = ref([])
const loading = ref(true)
const showHistory = ref(false)

const snomedOptions = ['SNOMED-CT-2024-01', 'SNOMED-CT-2023-01', 'SNOMED-CT-2022-03']
const medrtOptions = ['MED-RT-2023-05', 'MED-RT-2022-05']
const uniiOptions = ['UNII-2023-12', 'UNII-2021-12']
const ucumOptions = ['UCUM-1.4', 'UCUM-1.3']

const selectedStudyVersion = computed(
  () => studiesGeneralStore.selectedStudyVersion
)

const isReadOnly = computed(() => {
  return !checkPermission(roles.STUDY_WRITE) || selectedStudyVersion.value !== null
})

const historyTitle = computed(() => {
  return t('CTStandardVersionsTable.history_title', {
    study: studiesGeneralStore.selectedStudy.uid,
  })
})

const historyHeaders = [
  {
    title: t('CTStandardVersionsTable.ct_catalogue'),
    key: 'ct_package.catalogue_name',
  },
  {
    title: t('CTStandardVersionsTable.cdisc_ct_package'),
    key: 'ct_package.extends_package',
  },
  {
    title: t('_global.description'),
    key: 'description',
  },
  {
    title: 'SNOMED Version',
    key: 'snomed_version',
  },
  {
    title: 'MED-RT Version',
    key: 'medrt_version',
  },
  {
    title: 'UNII Version',
    key: 'unii_version',
  },
  {
    title: 'UCUM Version',
    key: 'ucum_version',
  },
  {
    title: t('_global.modified'),
    key: 'start_date',
  },
  {
    title: t('_global.modified_by'),
    key: 'author_username',
  },
]

function fetchItems() {
  loading.value = true
  api
    .getStudyStandardVersions(studiesGeneralStore.selectedStudy.uid)
    .then((resp) => {
      items.value = resp.data.map(item => ({
        ...item,
        snomed_version: item.snomed_version || 'SNOMED-CT-2024-01',
        medrt_version: item.medrt_version || 'MED-RT-2023-05',
        unii_version: item.unii_version || 'UNII-2023-12',
        ucum_version: item.ucum_version || 'UCUM-1.4',
      }))
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

async function saveItem(item, fieldChanged) {
  notificationHub.clearErrors()
  try {
    const payload = {
      ct_package_uid: item.ct_package?.uid,
      description: item.description,
      snomed_version: item.snomed_version,
      medrt_version: item.medrt_version,
      unii_version: item.unii_version,
      ucum_version: item.ucum_version,
    }

    await api.updateStudyStandardVersion(
      studiesGeneralStore.selectedStudy.uid,
      item.uid,
      payload
    )

    notificationHub.add({
      msg: 'Clinical dictionary version updated successfully.',
    })
  } catch (err) {
    // Reload items on error to revert dropdown state
    fetchItems()
  }
}

function openGlobalHistory() {
  api
    .getStudyStandardVersionsAuditTrail(studiesGeneralStore.selectedStudy.uid)
    .then((resp) => {
      historyItems.value = resp.data
      showHistory.value = true
    })
}

function closeHistory() {
  showHistory.value = false
}

onMounted(() => {
  fetchItems()
})
</script>

<style scoped>
.dictionary-table th {
  background-color: #f5f5f5;
  color: #333 !important;
}
</style>
