<template>
  <div class="px-4">
    <div class="page-title d-flex align-center">
      {{ $t('StudyManageView.title') }}
      <HelpButton :help-text="$t('_help.SelectOrAddStudyTable.general')" />
    </div>
    <NavigationTabs
      ref="navigationTabs"
      :tabs="tabs"
      :breadcrumbs-level="2"
      @tab-changed="clearFilters()"
    >
      <template #default="{ tabKeys }">
        <v-window-item :key="`active-${tabKeys.active}`" value="active">
          <StudyTable
            ref="activeStudiesTable"
            v-bind="$attrs"
            :items="paginatedStudies"
            :items-length="totalActiveStudies"
            @filter="fetchActiveStudies"
            @refresh-studies="reloadStudies"
            @enable-filtering="openFiltering = !openFiltering"
            
          >
            <template #customSearch>
              <v-text-field
                v-model="searchString"
                clearable
                clear-icon="mdi-close"
                prepend-inner-icon="mdi-magnify"
                :label="$t('_global.search')"
                single-line
                color="nnBaseBlue"
                hide-details
                style="min-width: 240px; max-width: 300px"
                autocomplete="off"
                class="searchFieldLabel ml-0"
                data-cy="search-field"
              />
            </template>
            <template #customFiltering>
              <v-toolbar
                v-if="openFiltering"
                flat
                class="filteringBar pt-1"
                color="nnGray200"
              >
                <v-slide-group show-arrows class="mb-5">
                  <v-autocomplete
                    v-for="header in headers"
                    :key="header.key"
                    ref="select"
                    v-model="columnFilters[header.key]"
                    clearable
                    multiple
                    width="240px"
                    :label="header.title"
                    color="nnBaseBlue"
                    bg-color="nnWhite"
                    class="filterAutocompleteLabel ml-1"
                    :items="getHeaderFilterData(header.key)"
                    clear-on-select
                    hide-details
                    autocomplete="off"
                    single-line
                    @update:model-value="activeStudiesTable.filter()"
                  >
                    <template #selection="{ index }">
                      <div v-if="index === 0">
                        <span class="items-font-size">{{
                          typeof columnFilters[header.key][0] !== 'boolean' &&
                          typeof columnFilters[header.key][0] !== 'number' &&
                          columnFilters[header.key][0].length > 12
                            ? columnFilters[header.key][0].substring(0, 12) +
                              '...'
                            : columnFilters[header.key][0]
                        }}</span>
                      </div>
                      <span
                        v-if="index === 1"
                        class="text-grey text-body-small mr-1"
                      >
                        (+{{ columnFilters[header.key].length - 1 }})
                      </span>
                    </template>
                  </v-autocomplete>
                </v-slide-group>
                <v-spacer />
                <v-btn
                  prepend-icon="mdi-close"
                  color="nnWhite"
                  variant="flat"
                  class="mr-3 mb-5 clearAllBtn"
                  rounded
                  :text="$t('NNTableTooltips.clear_filters_content')"
                  @click="clearFilters()"
                />
              </v-toolbar>
            </template>
          </StudyTable>
        </v-window-item>
        <v-window-item :key="`deleted-${tabKeys.deleted}`" value="deleted">
          <StudyTable
            ref="deletedStudiesTable"
            :items="paginatedStudies"
            :items-length="totalDeletedStudies"
            read-only
            @filter="fetchDeletedStudies"
            @refresh-studies="reloadStudies"
            @enable-filtering="openFiltering = !openFiltering"
            
          >
            <template #customSearch>
              <v-text-field
                v-model="searchString"
                clearable
                clear-icon="mdi-close"
                prepend-inner-icon="mdi-magnify"
                :label="$t('_global.search')"
                single-line
                color="nnBaseBlue"
                hide-details
                style="min-width: 240px; max-width: 300px"
                class="searchFieldLabel ml-0"
                data-cy="search-field"
              />
            </template>
            <template #customFiltering>
              <v-toolbar
                v-if="openFiltering"
                flat
                class="filteringBar pt-1"
                color="nnGray200"
              >
                <v-slide-group show-arrows class="mb-5">
                  <v-autocomplete
                    v-for="header in headers"
                    :key="header.key"
                    ref="select"
                    v-model="columnFilters[header.key]"
                    clearable
                    multiple
                    width="240px"
                    :label="header.title"
                    color="nnBaseBlue"
                    bg-color="nnWhite"
                    class="filterAutocompleteLabel ml-1"
                    :items="getHeaderFilterData(header.key)"
                    hide-details
                    autocomplete="off"
                    single-line
                    @update:model-value="deletedStudiesTable.filter()"
                  >
                    <template #selection="{ index }">
                      <div v-if="index === 0">
                        <span class="items-font-size">{{
                          typeof columnFilters[header.key][0] !== 'boolean' &&
                          typeof columnFilters[header.key][0] !== 'number' &&
                          columnFilters[header.key][0].length > 12
                            ? columnFilters[header.key][0].substring(0, 12) +
                              '...'
                            : columnFilters[header.key][0]
                        }}</span>
                      </div>
                      <span
                        v-if="index === 1"
                        class="text-grey text-body-small mr-1"
                      >
                        (+{{ columnFilters[header.key].length - 1 }})
                      </span>
                    </template>
                  </v-autocomplete>
                </v-slide-group>
                <v-spacer />
                <v-btn
                  prepend-icon="mdi-close"
                  color="nnWhite"
                  variant="flat"
                  class="mr-3 mb-5 clearAllBtn"
                  rounded
                  :text="$t('NNTableTooltips.clear_filters_content')"
                  @click="clearFilters()"
                />
              </v-toolbar>
            </template>
          </StudyTable>
        </v-window-item>
      </template>
    </NavigationTabs>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '@/api/study'
import filteringParameters from '@/utils/filteringParameters'
import StudyTable from '@/components/studies/StudyTable.vue'
import HelpButton from '@/components/tools/HelpButton.vue'
import NavigationTabs from '@/components/tools/NavigationTabs.vue'
import { useStudiesManageStore } from '@/stores/studies-manage'
import { useI18n } from 'vue-i18n'

const studiesManageStore = useStudiesManageStore()
const { t } = useI18n()

const activeStudies = ref([])
const deletedStudies = ref([])
const totalActiveStudies = ref(0)
const totalDeletedStudies = ref(0)
const savedFilters = ref('')
const searchString = ref('')
const filteredStudies = ref([])
const paginatedStudies = ref([])
const columnFilters = ref({})
const openFiltering = ref(false)
const fullRefresh = ref(false)

const headers = [
  {
    title: t('StudyTable.clinical_programme'),
    key: 'clinical_programme_name',
  },
  {
    title: t('StudyTable.project_id'),
    key: 'project_number',
  },
  {
    title: t('StudyTable.project_name'),
    key: 'project_name',
  },
  {
    title: t('StudyTable.number'),
    key: 'number',
  },
  {
    title: t('StudyTable.id'),
    key: 'id',
  },
  {
    title: t('StudyTable.subpart_id'),
    key: 'subpart_id',
  },
  {
    title: t('StudyTable.acronym'),
    key: 'acronym',
  },
  {
    title: t('StudyTable.subpart_acronym'),
    key: 'subpart_acronym',
  },
  {
    title: t('StudyTable.title'),
    key: 'title',
  },
  {
    title: t('_global.status'),
    key: 'version_status',
  },
  {
    title: t('StudyTable.lts_version'),
    key: 'version_number',
  },
  {
    title: t('StudyTable.lts_locked_ver'),
    key: 'latest_locked_version',
  },
  {
    title: t('StudyTable.lts_released_ver'),
    key: 'latest_released_version',
  },
  {
    title: t('StudyTable.data_completeness'),
    key: 'data_completeness_tags',
  },
  {
    title: t('_global.modified'),
    key: 'version_start_date',
  },
  {
    title: t('_global.modified_by'),
    key: 'version_author',
  },
]

const activeStudiesTable = ref()
const deletedStudiesTable = ref()
const navigationTabs = ref()

const tabs = [
  { tab: 'active', name: t('SelectOrAddStudyTable.tab1_title') },
  { tab: 'deleted', name: t('SelectOrAddStudyTable.tab2_title') },
]

watch(searchString, () => {
  filterTable()
})

function reloadStudies() {
  fullRefresh.value = true
  activeStudiesTable.value.filter()
}

async function fetchActiveStudies(filters, options, filtersUpdated) {
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
    totalActiveStudies.value = resp.data.total
  } catch (error) {
    console.error(error)
  }
}

function getHeaderFilterData(key) {
  const source =
    navigationTabs.value.tab === 'active'
      ? activeStudies.value
      : deletedStudies.value

  const values = source.flatMap((obj) => {
    const value = obj[key]

    if (Array.isArray(value)) {
      if (value.length === 0) {
        return []
      }
      return value
        .filter((item) => item !== null && item !== undefined)
        .map((item) => String(item))
    }

    return value !== null && value !== undefined ? [value] : []
  })

  return [...new Set(values)].sort()
}

function clearFilters() {
  columnFilters.value = {}
  filterTable()
}

async function fetchDeletedStudies(filters, options, filtersUpdated) {
  const params = filteringParameters.prepareParameters(
    options,
    savedFilters.value,
    filtersUpdated
  )
  params.deleted = true
  try {
    const resp = await api.get(params)
    paginatedStudies.value = resp.data.items
    totalDeletedStudies.value = resp.data.total
  } catch (error) {
    console.error(error)
  }
}

function filterTable() {
  if (navigationTabs.value.tab === 'active') {
    activeStudiesTable.value.filter()
  } else {
    deletedStudiesTable.value.filter()
  }
}

studiesManageStore.fetchProjects()
</script>
