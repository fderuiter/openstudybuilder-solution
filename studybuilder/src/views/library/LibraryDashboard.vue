<template>
  <div class="px-4">
    <div class="d-flex align-center page-title">
      {{ $t('Sidebar.library.dashboard') }}
    </div>
    <StudyTable
      ref="dashboardStudiesTable"
      :items="paginatedStudies"
      :items-length="totalStudies"
      :items-per-page-options="itemsPerPageOptions"
      @filter="fetchStudies"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StudyTable from '@/components/studies/StudyTable.vue'
import api from '@/api/study'
import filteringParameters from '@/utils/filteringParameters'

const paginatedStudies = ref([])
const totalStudies = ref(0)
const savedFilters = ref({})

const itemsPerPageOptions = [
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
  { value: 100, title: '100' },
  { value: 1000, title: '1000' },
]

async function fetchStudies(filters, options, filtersUpdated) {
  const params = filteringParameters.prepareParameters(
    options,
    savedFilters.value,
    filtersUpdated
  )
  try {
    const resp = await api.get(params)
    resp.data.items.forEach((study) => {
      if (study.latest_locked_version) {
        study.latest_locked_version = `${study.latest_locked_version.version_number} ${study.latest_locked_version.change_description ? study.latest_locked_version.change_description : ''}`
      }
      if (study.latest_released_version) {
        study.latest_released_version = `${study.latest_released_version.version_number} ${study.latest_released_version.change_description ? study.latest_released_version.change_description : ''}`
      }
    })
    paginatedStudies.value = resp.data.items
    totalStudies.value = resp.data.total
  } catch (error) {
    console.error(error)
  }
}
</script>
