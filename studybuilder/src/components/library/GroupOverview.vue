<template>
  <div class="group-overview-container">
    <BaseActivityOverview
      ref="overview"
      :source="'activity-groups'"
      :item-uid="itemUid"
      :transform-func="transformItem"
      :navigate-to-version="changeVersion"
      :history-headers="historyHeaders"
      :yaml-version="props.yamlVersion"
      :cosmos-version="props.cosmosVersion"
      v-bind="$attrs"
      @update:subgroups="handleSubgroupsUpdate"
    >
      <template #htmlContent>
        <!-- Group Details using ActivitySummary -->
        <div class="summary-section">
          <v-skeleton-loader
            v-if="!itemOverview?.group"
            type="card"
            class="group-activity-summary"
          />
          <ActivitySummary
            v-else
            :activity="itemOverview.group"
            :all-versions="allVersions(itemOverview)"
            :show-library="true"
            :show-nci-concept-id="false"
            :show-data-collection="false"
            :show-abbreviation="false"
            :show-author="true"
            class="group-activity-summary"
            @version-change="
              (value) => changeVersion(itemOverview.group, value)
            "
          />
        </div>

        <!-- Activity Subgroups using NNTable -->
        <div v-if="loadingSubgroups" class="my-5">
          <div class="section-header mb-1">
            <h3 class="text-h6 font-weight-bold text-primary">
              {{ $t('ActivityOverview.activity_subgroups') }}
            </h3>
          </div>
          <v-skeleton-loader type="table" />
        </div>
        <div v-else class="my-5">
          <div class="section-header mb-1">
            <h3 class="text-h6 font-weight-bold text-primary">
              {{ $t('ActivityOverview.activity_subgroups') }}
            </h3>
          </div>
          <NNTable
            :headers="subgroupsHeaders"
            :items="filteredSubgroups"
            :items-length="subgroupsTotal"
            :items-per-page="tableOptions.itemsPerPage"
            :hide-export-button="false"
            :hide-default-switches="true"
            :export-data-url="`concepts/activities/activity-groups/${route.params.id}/subgroups`"
            :disable-filtering="false"
            :hide-search-field="false"
            :modifiable-table="true"
            :no-padding="true"
            elevation="0"
            class="subgroups-table"
            item-value="uid"
            :initial-sort="initialSort"
            :disable-sort="false"
            :loading="false"
            :column-data-resource="'concepts/activities/activity-sub-groups'"
            :filters-modify-function="modifyFilters"
            :initial-column-data="getInitialColumnData()"
            @filter="handleFilter"
            @update:options="updateTableOptions"
            @click:column="handleColumnClick"
          >
            <template #[`item.name`]="{ item }">
              <router-link
                :to="{
                  name: 'SubgroupOverview',
                  params: { id: item.uid, version: item.version },
                }"
              >
                {{ item.name }}
              </router-link>
            </template>
            <template #[`item.status`]="{ item }">
              <StatusChip :status="item.status" />
            </template>
            <template #no-data>
              <div class="text-center py-4">
                <span class="text-body-1 text-grey-darken-1">{{
                  $t('ActivityOverview.no_subgroups')
                }}</span>
              </div>
            </template>
          </NNTable>
        </div>
      </template>
      <template #itemForm="{ show, item, close }">
        <v-dialog
          :model-value="show"
          persistent
          max-width="800px"
          content-class="top-dialog"
        >
          <ActivitiesGroupsForm
            ref="groupFormRef"
            :open="show"
            :subgroup="false"
            :edited-group-or-subgroup="item"
            @close="close"
          />
        </v-dialog>
      </template>
    </BaseActivityOverview>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import activities from '@/api/activities'
import columnData from '@/api/columnData'

import BaseActivityOverview from './BaseActivityOverview.vue'
import StatusChip from '@/components/tools/StatusChip.vue'
import ActivitySummary from '@/components/library/ActivitySummary.vue'
import NNTable from '@/components/tools/NNTable.vue'
import { defineAsyncComponent } from 'vue'

const ActivitiesGroupsForm = defineAsyncComponent(
  () => import('@/components/library/ActivitiesGroupsForm.vue')
)

const props = defineProps({
  itemOverview: {
    type: Object,
    required: true,
  },
  itemUid: {
    type: String,
    required: true,
  },
  yamlVersion: {
    type: String,
    default: null,
  },
  cosmosVersion: {
    type: String,
    default: null,
  },
})
const emit = defineEmits(['refresh', 'update:itemOverview'])

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const overview = ref()
const groupFormRef = ref()

const filteredSubgroups = ref([])
const subgroupsTotal = ref(0)
const loadingSubgroups = ref(true)
const tableOptions = ref({
  search: '',
  sortBy: [],
  sortDesc: [],
  page: 1,
  itemsPerPage: 10,
})

// Set initial sort order for the table
const initialSort = ref([{ key: 'name', order: 'asc' }])

// Controlled sort state for the NNTable component
const sortBy = ref([])

const historyHeaders = [
  { title: t('_global.library'), key: 'library_name' },
  { title: t('_global.name'), key: 'name' },
  { title: t('_global.definition'), key: 'definition' },
  { title: t('_global.version'), key: 'version' },
  { title: t('_global.start_date'), key: 'start_date' },
  { title: t('_global.end_date'), key: 'end_date' },
  { title: t('_global.status'), key: 'status' },
]

const subgroupsHeaders = computed(() => [
  { title: t('_global.name'), key: 'name', align: 'start', sortable: true },
  {
    title: t('_global.definition'),
    key: 'definition',
    align: 'start',
    sortable: true,
  },
  {
    title: t('_global.version'),
    key: 'version',
    align: 'start',
    sortable: true,
  },
  { title: t('_global.status'), key: 'status', align: 'start', sortable: true },
])

// Returns all versions of the given item in descending order
function allVersions(item) {
  return [...item.all_versions].sort().reverse()
}

// Changes the version of the given group
async function changeVersion(group, version) {
  await router.push({
    name: 'GroupOverview',
    params: { id: group.uid, version },
  })
  emit('refresh')
}

// Transforms the given item for display
function transformItem(item) {
  item.item_key = item.uid

  // Map author_username to author field for ActivitySummary component
  if (item.group && item.group.author_username) {
    item.group.author = item.group.author_username
  }
}

// Checks if the given item matches the search term
function itemMatchesSearch(item, searchTerm) {
  if (!searchTerm || searchTerm === '') return true

  const term = searchTerm.toLowerCase()

  if (item.name?.toLowerCase().includes(term)) return true

  if (item.definition?.toLowerCase().includes(term)) return true

  if (item.version && item.version.toString().toLowerCase().includes(term))
    return true

  if (item.status?.toLowerCase().includes(term)) return true

  return false
}

// Handles column click event
function handleColumnClick(column) {
  if (!column.sortable) return

  const key = column.key
  const currentSortBy = tableOptions.value.sortBy[0] || ''
  const currentSortDesc = tableOptions.value.sortDesc[0] || false
  let newSortDesc
  if (currentSortBy !== key) {
    // New column clicked, default to ascending
    newSortDesc = false
  } else {
    // Same column clicked, toggle direction
    newSortDesc = !currentSortDesc
  }

  tableOptions.value.sortBy = [key]
  tableOptions.value.sortDesc = [newSortDesc]
  if (props.itemOverview?.subgroups) {
    // Get items array using the new format (items property) or the old format (direct array)
    const sourceItems =
      props.itemOverview.subgroups.items || props.itemOverview.subgroups
    let subgroupsToFilter = [...sourceItems]

    // Apply any active search filter
    if (tableOptions.value.search) {
      const searchTerm = tableOptions.value.search.toLowerCase()
      subgroupsToFilter = subgroupsToFilter.filter((item) =>
        itemMatchesSearch(item, searchTerm)
      )
    }

    // Sort the filtered data
    subgroupsToFilter.sort((a, b) => {
      let valA = a[key]
      let valB = b[key]

      // Handle undefined values
      valA = valA || ''
      valB = valB || ''

      // Compare based on type
      if (typeof valA === 'string' && typeof valB === 'string') {
        return newSortDesc ? valB.localeCompare(valA) : valA.localeCompare(valB)
      } else {
        return newSortDesc ? valB - valA : valA - valB
      }
    })

    // Update the filtered list
    filteredSubgroups.value = subgroupsToFilter
    subgroupsTotal.value = subgroupsToFilter.length
  }
}

let lastSearchTerm = ''
let savedFilters = ref({})

// Handles filter event - Client-side filtering since API doesn't support it
function handleFilter(filters, options, filtersUpdated) {
  // Save filters if provided
  if (filters !== undefined) {
    savedFilters.value = filters
  }

  if (!options) {
    options = tableOptions.value
  }

  if (options && options.search === lastSearchTerm && !filtersUpdated) {
    return
  }

  if (options && options.search) {
    lastSearchTerm = options.search
  }

  if (!props.itemOverview || !props.itemOverview.subgroups) {
    return
  }

  // Get items array using the new format (items property) or the old format (direct array)
  const sourceItems =
    props.itemOverview.subgroups.items || props.itemOverview.subgroups

  let filteredItems = [...sourceItems]

  // Apply search filter
  if (options && options.search) {
    tableOptions.value.search = options.search
    const searchTerm = options.search.toLowerCase()
    filteredItems = filteredItems.filter((item) =>
      itemMatchesSearch(item, searchTerm)
    )
  } else if (options) {
    tableOptions.value.search = ''
  }

  // Apply column filters
  if (savedFilters.value && savedFilters.value !== '{}') {
    let filtersObj = savedFilters.value
    if (typeof filtersObj === 'string') {
      try {
        filtersObj = JSON.parse(filtersObj)
      } catch (e) {
        console.error('Error parsing filters string:', e)
        return
      }
    }

    // Skip column filters if this is a search filter (has '*' key with search term)
    if (filtersObj['*'] && filtersObj['*'].v && options && options.search) {
      // Don't apply column filters when it's just a search
    } else {
      // Check if filters is a column-specific filter object (from FilterAutocomplete)
      if (filtersObj.column && filtersObj.data) {
        const filterKey = filtersObj.column
        const filterValues = filtersObj.data

        if (filterValues && filterValues.length > 0) {
          filteredItems = filteredItems.filter((item) => {
            return applyFilter(item, filterKey, filterValues)
          })
        }
      }
      // If filters is a regular object with multiple filters
      else if (typeof filtersObj === 'object') {
        Object.keys(filtersObj).forEach((filterKey) => {
          // Get the filter values object
          const filterValueObj = filtersObj[filterKey]

          if (!filterValueObj) {
            // Skip empty filter
            return
          }

          // Check if the filter has 'v' property (from NNTable)
          if (filterValueObj.v && Array.isArray(filterValueObj.v)) {
            const filterValues = filterValueObj.v

            if (filterValues.length > 0) {
              filteredItems = filteredItems.filter((item) => {
                const matches = applyFilter(item, filterKey, filterValues)
                return matches
              })
            }
          }
          // Check if the filter has 'data' property
          else if (Array.isArray(filterValueObj.data)) {
            const filterValues = filterValueObj.data
            // Process filters from data property

            if (filterValues.length > 0) {
              filteredItems = filteredItems.filter((item) => {
                return applyFilter(item, filterKey, filterValues)
              })
            }
          }
        })
      }
    }
  }

  // Helper function to apply filter based on key and values
  function applyFilter(item, filterKey, filterValues) {
    const itemValue = item[filterKey]

    // Handle special case for status which might be different formats
    if (filterKey === 'status') {
      return filterValues.includes(item.status)
    }
    // Handle definition filtering
    else if (filterKey === 'definition') {
      // If the item has no definition, it should match only if null/empty is in filter values
      if (!item.definition) {
        return filterValues.includes(null) || filterValues.includes('')
      }
      // Otherwise check if definition is in filter values
      return filterValues.includes(item.definition)
    }
    // Handle version filtering
    else if (filterKey === 'version') {
      // Convert to string for comparison as filterValues might be strings
      return (
        filterValues.includes(item.version) ||
        filterValues.includes(String(item.version))
      )
    }
    // Handle name filtering - this is the one we need most often
    else if (filterKey === 'name') {
      const included = filterValues.includes(item.name)
      return included
    }
    // Generic handling for other fields
    else {
      return filterValues.includes(itemValue)
    }
  }

  if (options && options.sortBy && options.sortBy.length > 0) {
    const sortItem = options.sortBy[0]
    const key = sortItem.key
    const order = sortItem.order
    filteredItems.sort((a, b) => {
      let valA = a[key]
      let valB = b[key]

      // Handle undefined values
      valA = valA || ''
      valB = valB || ''

      // Compare based on type
      if (typeof valA === 'string' && typeof valB === 'string') {
        return order === 'asc'
          ? valA.localeCompare(valB)
          : valB.localeCompare(valA)
      } else {
        return order === 'asc' ? valA - valB : valB - valA
      }
    })

    // Update tableOptions with the current sort
    tableOptions.value.sortBy = [key]
    tableOptions.value.sortDesc = [order === 'desc']
    sortBy.value = [{ key, order }]
  }

  filteredSubgroups.value = filteredItems
  subgroupsTotal.value = filteredItems.length
}

// Handles update options event
function updateTableOptions(options) {
  if (!options) return

  if (options.sortBy && options.sortBy.length > 0) {
    tableOptions.value.sortBy = [...options.sortBy]
    tableOptions.value.sortDesc = [...(options.sortDesc || [])]
    sortBy.value = options.sortBy
  }

  if (
    options.page !== tableOptions.value.page ||
    options.itemsPerPage !== tableOptions.value.itemsPerPage
  ) {
    tableOptions.value.page = options.page || 1
    tableOptions.value.itemsPerPage = options.itemsPerPage || 10

    // Need to fetch new data for pagination
    fetchSubgroups(tableOptions.value)
    return // Skip filtering, as fetchSubgroups will trigger a data update
  }

  // If this is a search update, let the handleFilter function handle it
  // This prevents duplicate processing of search
  if (options.search !== undefined) {
    // Only store the search value and skip additional filter call
    // The @filter event handler will take care of filtering
    tableOptions.value.search = options.search

    // If we don't have a filter event (direct call), then filter manually
    if (!options.fromFilterEvent) {
      handleFilter(null, options)
    }
    return
  }

  // For other changes like sorting, still apply filter
  if (!options.search) {
    handleFilter(null, tableOptions.value)
  }
}

// Function to get headers for the subgroups filter
function getSubgroupsHeaders() {
  const params = {
    field_name: 'name',
    search_string: '',
    page_size: 50,
  }

  return columnData.getHeaderData(
    params,
    'concepts/activities/activity-sub-groups'
  )
}

// Function to modify filters for subgroups
function modifyFilters(jsonFilter, params) {
  return {
    jsonFilter,
    params,
  }
}

// Function to get initial column data for filters
function getInitialColumnData() {
  if (!props.itemOverview?.subgroups) return {}

  const sourceItems =
    props.itemOverview.subgroups.items || props.itemOverview.subgroups
  if (!Array.isArray(sourceItems) || sourceItems.length === 0) return {}

  const columnData = {}

  // Extract unique values for each column from the actual table data
  subgroupsHeaders.value.forEach((header) => {
    if (header.key === 'actions' || header.noFilter) return

    const uniqueValues = [
      ...new Set(sourceItems.map((item) => item[header.key])),
    ].filter((val) => val !== undefined && val !== null && val !== '')

    if (uniqueValues.length > 0) {
      columnData[header.key] = uniqueValues
    }
  })

  return columnData
}

function handleSubgroupsUpdate(subgroupsData) {
  if (props.itemOverview) {
    emit('update:itemOverview', {
      ...props.itemOverview,
      subgroups: subgroupsData,
    })

    // IMPORTANT: The direct assignment is needed for the search functionality to work
    // eslint-disable-next-line vue/no-mutating-props
    props.itemOverview.subgroups = subgroupsData

    const items = subgroupsData?.items || subgroupsData || []

    // Check if we have an active search - if so, don't overwrite filtered results
    if (tableOptions.value.search) {
      subgroupsTotal.value = subgroupsData?.total || items.length || 0
    } else {
      filteredSubgroups.value = Array.isArray(items) ? [...items] : []
      subgroupsTotal.value =
        subgroupsData?.total || filteredSubgroups.value.length || 0
    }

    setTimeout(() => {
      loadingSubgroups.value = false
    }, 0)
  }
}

// Watches for changes in itemOverview
watch(
  () => props.itemOverview,
  (newItemOverview) => {
    if (newItemOverview === null) {
      loadingSubgroups.value = true
      filteredSubgroups.value = []
      subgroupsTotal.value = 0
      return
    }

    // If subgroups is null, we need to fetch them
    if (newItemOverview?.subgroups === null) {
      loadingSubgroups.value = true
      // Fetch subgroups when itemOverview changes with null subgroups
      fetchSubgroups(tableOptions.value)
      return
    }

    loadingSubgroups.value = !newItemOverview?.subgroups

    // If we have subgroups data and an active search or filters, re-apply them
    if (newItemOverview?.subgroups) {
      const sourceItems =
        newItemOverview.subgroups.items || newItemOverview.subgroups
      subgroupsTotal.value = sourceItems.length

      // If there's an active search or filters, re-apply them
      if (
        tableOptions.value.search ||
        (savedFilters.value && Object.keys(savedFilters.value).length > 0)
      ) {
        handleFilter(savedFilters.value, tableOptions.value)
      } else {
        // Only update directly if there's no active search or filters
        filteredSubgroups.value = sourceItems
      }
    }
  },
  { immediate: true }
)

// Watches for changes in itemOverview.subgroups
watch(
  () => props.itemOverview?.subgroups,
  (newSubgroups) => {
    // If subgroups is null, keep loading state and let route watcher fetch
    if (newSubgroups === null) {
      return
    }

    loadingSubgroups.value = false

    if (newSubgroups) {
      const items = newSubgroups.items || newSubgroups
      const initialSubgroups = [...items]
      subgroupsTotal.value = newSubgroups.total || items.length

      // Always apply filters if there's an active search or saved filters
      if (
        tableOptions.value.search ||
        (savedFilters.value && Object.keys(savedFilters.value).length > 0) ||
        (tableOptions.value.sortBy && tableOptions.value.sortBy.length > 0)
      ) {
        // Apply filters which will handle search, column filters, and sorting
        handleFilter(savedFilters.value, tableOptions.value)
      } else {
        // Only set directly if there's no search, filters, or custom sorting
        if (initialSort.value.length > 0) {
          const sortKey = initialSort.value[0].key
          const sortDesc = initialSort.value[0].order === 'desc'
          // Sort the data based on initialSort configuration
          initialSubgroups.sort((a, b) => {
            let valA = a[sortKey] || ''
            let valB = b[sortKey] || ''

            if (typeof valA === 'string' && typeof valB === 'string') {
              return sortDesc
                ? valB.localeCompare(valA)
                : valA.localeCompare(valB)
            } else {
              return sortDesc ? valB - valA : valA - valB
            }
          })
          filteredSubgroups.value = initialSubgroups
        } else {
          filteredSubgroups.value = initialSubgroups
        }
      }
    } else {
      filteredSubgroups.value = []
      subgroupsTotal.value = 0
    }
  },
  { immediate: true }
)

// Fetches subgroups data
const fetchSubgroups = async (options = {}) => {
  // Prevent additional calls if already loading or missing required params
  if (!route.params.id || !route.params.id.trim()) {
    return
  }

  try {
    // Set loading state
    loadingSubgroups.value = true

    const params = {
      page_number: options.page || tableOptions.value.page,
      page_size: options.itemsPerPage || tableOptions.value.itemsPerPage,
      total_count: true,
    }

    const result = await activities.getActivityGroupSubgroups(
      route.params.id,
      route.params.version || '',
      params
    )

    if (result && result.data) {
      // For empty arrays, ensure filteredSubgroups is properly set
      if (Array.isArray(result.data.items)) {
        filteredSubgroups.value = [...result.data.items]
      } else if (Array.isArray(result.data)) {
        filteredSubgroups.value = [...result.data]
      } else {
        filteredSubgroups.value = []
      }

      // Set the total
      subgroupsTotal.value =
        result.data.total || filteredSubgroups.value.length || 0

      // Update the parent component
      handleSubgroupsUpdate(result.data)
    } else {
      filteredSubgroups.value = []
      subgroupsTotal.value = 0
      loadingSubgroups.value = false
    }
  } catch (error) {
    console.error('Error fetching subgroups:', error)
    loadingSubgroups.value = false
    filteredSubgroups.value = []
    subgroupsTotal.value = 0
  } finally {
    // Always ensure loading is false when done
    loadingSubgroups.value = false
  }
}

watch(
  [() => tableOptions.value.page, () => tableOptions.value.itemsPerPage],
  () => {
    if (route.params.id && !tableOptions.value.search) {
      fetchSubgroups(tableOptions.value)
    }
  }
)

// Fetch headers for filtering when component mounts
onMounted(() => {
  getSubgroupsHeaders()
    .then(() => {})
    .catch((error) => {
      console.error('Error loading subgroups headers:', error)
    })

  // Initial fetch of subgroups if not provided
  if (props.itemOverview?.subgroups === null) {
    fetchSubgroups(tableOptions.value)
  }
})

onMounted(() => {
  appStore.addBreadcrumbsLevel(
    t('Sidebar.library.concepts'),
    { name: 'Activities' },
    1,
    false
  )

  appStore.addBreadcrumbsLevel(
    t('Sidebar.library.activities'),
    { name: 'Activities' },
    2,
    true
  )

  appStore.addBreadcrumbsLevel(
    t('Sidebar.library.activities_groups'),
    { name: 'Activities', params: { tab: 'activity-groups' } },
    3,
    true
  )

  const groupName = props.itemOverview?.group?.name || t('_global.loading')

  appStore.addBreadcrumbsLevel(
    groupName,
    {
      name: 'GroupOverview',
      params: { id: route.params.id },
    },
    4,
    true
  )
})
</script>

<style scoped>
/* Group overview container styling */
.group-overview-container {
  width: 100%;
  background-color: transparent;
}

/* Summary section styling */
.summary-section {
  margin-bottom: 24px;
}

/* Subgroups table styling */
.subgroups-table {
  margin-top: 8px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: none;
  background-color: transparent;
}

/* Table styling */
.subgroups-table :deep(table) {
  border-collapse: collapse;
  width: 100%;
}

.subgroups-table :deep(th) {
  background-color: var(--semantic-system-brand, #001965);
  color: white;
  font-weight: 500;
  padding: 12px 16px;
  text-align: left;
}

.subgroups-table :deep(td) {
  padding: 8px 16px;
  border-bottom: 1px solid #e0e0e0;
  background-color: white !important;
}

.subgroups-table :deep(.v-card-text) {
  width: 100% !important;
  padding: 0 !important;
}

.subgroups-table :deep(.v-table__wrapper) {
  height: auto !important;
}

.subgroups-table :deep(.v-card-title) {
  padding: 8px 16px;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  background-color: transparent;
}

.subgroups-table :deep(.v-card__title .v-input) {
  max-width: 300px;
  margin-right: auto;
}

.subgroups-table :deep(.v-data-table-footer) {
  border-top: 1px solid #e0e0e0;
  background-color: transparent !important;
}

.group-overview-container :deep(.v-table),
.subgroups-table :deep(.v-table) {
  background: transparent !important;
}

.group-overview-container :deep(.v-data-table__th),
.subgroups-table :deep(.v-data-table__th) {
  background-color: rgb(var(--v-theme-nnTrueBlue)) !important;
}

.group-overview-container :deep(.v-data-table__tbody tr),
.subgroups-table :deep(.v-data-table__tbody tr) {
  background-color: white !important;
}

.group-overview-container :deep(.v-card),
.group-overview-container :deep(.v-sheet),
.subgroups-table :deep(.v-card),
.subgroups-table :deep(.v-sheet) {
  background-color: transparent !important;
  box-shadow: none !important;
}
</style>
