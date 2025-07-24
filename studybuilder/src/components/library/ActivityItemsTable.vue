<template>
  <div>
    <v-row class="activity-items-row">
      <v-col cols="12" class="activity-items-col px-0">
        <div class="section-header mb-1">
          <h3 class="text-h6 font-weight-bold text-primary">
            {{ $t('ActivityOverview.activity_items') }}
          </h3>
        </div>
        <div class="table-container">
          <NNTable
            ref="tableRef"
            :headers="itemHeaders"
            :items="activityItems"
            :export-object-label="t('activityItemsTable.exportLabel')"
            :hide-export-button="false"
            :hide-default-switches="true"
            :export-data-url="exportDataUrl"
            item-value="item_key"
            :disable-filtering="false"
            :hide-search-field="false"
            :modifiable-table="true"
            :no-padding="true"
            elevation="0"
            :loading="loading"
            :items-length="paginationTotal"
            :no-data-text="t('activityItemsTable.noItemsFound')"
            :use-cached-filtering="false"
            @filter="handleFilter"
            @update:options="updateTableOptions"
          >
            <template #[`item.name`]="{ item }">
              <div class="d-block">
                <span v-if="item.ct_terms && item.ct_terms.length > 0">
                  {{ item.ct_terms.map((term) => term.name).join(', ') }}
                </span>
                <span
                  v-else-if="
                    item.unit_definitions && item.unit_definitions.length > 0
                  "
                >
                  {{
                    item.unit_definitions.map((unit) => unit.name).join(', ')
                  }}
                </span>
                <span v-else>-</span>
              </div>
            </template>
            <template #[`item.item_type`]="{ item }">
              <div class="d-block">
                {{ item.activity_item_class?.data_type_name || '' }}
              </div>
            </template>
            <template #[`item.activity_item_class`]="{ item }">
              <div class="d-block">
                {{ item.activity_item_class?.name || '' }}
              </div>
            </template>
          </NNTable>
        </div>
      </v-col>
    </v-row>

    <!-- Show this only if there are genuinely no items at all, not just no search results -->
    <div v-if="activityItems.length === 0 && !loading" class="py-4 text-center">
      {{ t('activityItemsTable.noItemsAvailable') }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import activitiesApi from '@/api/activities'
import NNTable from '@/components/tools/NNTable.vue'

const route = useRoute()
const { t } = useI18n()

const props = defineProps({
  activityInstanceId: {
    type: String,
    required: true,
  },
  version: {
    type: String,
    required: false,
    default: '',
  },
})

const tableRef = ref(null)
const activityItems = ref([])
const allActivityItems = ref([]) // Store all items for client-side filtering
const loading = ref(false)
const paginationTotal = ref(0)
const currentSearch = ref('') // Track current search term
const tableOptions = ref({
  page: 1,
  itemsPerPage: 25,
  sortBy: [{ key: 'activity_item_class.name', order: 'asc' }],
})

// Define headers for the activity items table
const itemHeaders = [
  {
    title: t('activityItemsTable.headerDataType'),
    key: 'item_type',
    sortable: false,
    width: '25%',
  },
  {
    title: t('activityItemsTable.headerName'),
    key: 'name',
    sortable: false,
    width: '40%',
  },
  {
    title: t('activityItemsTable.headerActivityItemClass'),
    key: 'activity_item_class',
    sortable: false,
    width: '35%',
  },
]

const exportDataUrl = computed(() => {
  if (!props.activityInstanceId) return ''
  return `/concepts/activities/activity-instances/${props.activityInstanceId}/activity-items`
})

onMounted(() => {
  refresh()
})

// Watch for changes in the activityInstanceId or version
watch(
  [
    () => props.activityInstanceId,
    () => props.version,
    () => route.params.version,
  ],
  () => {
    refresh()
  }
)

// Initialize the component when mounted or props change
function refresh() {
  const version = props.version || route.params.version

  if (props.activityInstanceId) {
    fetchActivityItems(props.activityInstanceId, version, tableOptions.value)
  }
}

// Fetches activity items from API
async function fetchActivityItems(activityInstanceId, version, options = {}) {
  try {
    loading.value = true

    const params = {
      page_number: 1,
      page_size: 1000,
      total_count: true,
    }

    const response = await activitiesApi.getActivityInstanceItems(
      activityInstanceId,
      version,
      params
    )

    // Transform the response data to include item_key
    const items = (response.data || []).map((item, index) => ({
      ...item,
      item_key: `item-${index}`,
    }))

    allActivityItems.value = items

    // Apply search filter if there's a search term
    applySearchFilter(options.search || currentSearch.value)
  } catch (error) {
    console.error('Error fetching activity items:', error)
    activityItems.value = []
    allActivityItems.value = []
    paginationTotal.value = 0
  } finally {
    loading.value = false
  }
}

// Helper function to check if an item matches the search term
function itemMatchesSearch(item, searchTerm) {
  const term = searchTerm.toLowerCase()

  // Search in activity item class name, role, data type
  if (item.activity_item_class?.name?.toLowerCase().includes(term)) return true
  if (item.activity_item_class?.role_name?.toLowerCase().includes(term))
    return true
  if (item.activity_item_class?.data_type_name?.toLowerCase().includes(term))
    return true

  // Search in CT terms
  if (
    item.ct_terms?.some((ctTerm) => ctTerm.name?.toLowerCase().includes(term))
  )
    return true

  // Search in unit definitions
  if (
    item.unit_definitions?.some(
      (unit) =>
        unit.name?.toLowerCase().includes(term) ||
        unit.dimension_name?.toLowerCase().includes(term)
    )
  )
    return true

  // Search in ODM forms
  if (
    item.odm_forms?.some(
      (form) =>
        form.name?.toLowerCase().includes(term) ||
        form.oid?.toLowerCase().includes(term)
    )
  )
    return true

  return false
}

// Apply search filter to the items
function applySearchFilter(searchTerm) {
  currentSearch.value = searchTerm || ''

  if (!searchTerm || searchTerm.trim() === '') {
    // No search term, show all items with pagination
    const startIndex =
      (tableOptions.value.page - 1) * tableOptions.value.itemsPerPage
    const endIndex = startIndex + tableOptions.value.itemsPerPage
    activityItems.value = allActivityItems.value.slice(startIndex, endIndex)
    paginationTotal.value = allActivityItems.value.length
  } else {
    // Filter items based on search term
    const filteredItems = allActivityItems.value.filter((item) =>
      itemMatchesSearch(item, searchTerm)
    )

    // Apply pagination to filtered results
    const startIndex =
      (tableOptions.value.page - 1) * tableOptions.value.itemsPerPage
    const endIndex = startIndex + tableOptions.value.itemsPerPage
    activityItems.value = filteredItems.slice(startIndex, endIndex)
    paginationTotal.value = filteredItems.length
  }
}

// Handles filtering of activity items based on search term
function handleFilter(_, options) {
  // Handle search
  if (options && typeof options.search !== 'undefined') {
    // Reset to page 1 when searching
    tableOptions.value.page = 1
    applySearchFilter(options.search)
  }

  // Handle sorting changes
  if (options && options.sortBy && options.sortBy.length > 0) {
    tableOptions.value.sortBy = [...options.sortBy]
  }
}

// Handle table options changes (pagination and sorting)
function updateTableOptions(options) {
  if (!options) return

  // Check for pagination changes
  if (
    options.page !== tableOptions.value.page ||
    options.itemsPerPage !== tableOptions.value.itemsPerPage
  ) {
    tableOptions.value.page = options.page
    tableOptions.value.itemsPerPage = options.itemsPerPage

    // Reapply search filter with new pagination
    applySearchFilter(currentSearch.value)
  }
}
</script>

<style scoped>
/* Table container styling */
.table-container {
  width: 100%;
  margin-bottom: 24px;
  border-radius: 4px;
  background-color: transparent;
  box-shadow: none;
  overflow: hidden;
}

/* Row container styling */
.activity-items-row {
  margin: 0 !important;
  width: 100%;
}

.activity-items-col {
  padding: 0 !important;
}

/* Adjusts the spacing for section headers */
.section-header {
  margin-top: 16px;
  margin-bottom: 8px;
  padding-left: 0;
}

/* Ensure card content takes full width */
.activity-items-row :deep(.v-card-text) {
  width: 100% !important;
  padding: 0 !important;
}

/* Force table to take full width */
.activity-items-row :deep(.v-data-table),
.activity-items-row :deep(.v-table),
.activity-items-row :deep(table) {
  width: 100% !important;
  table-layout: fixed !important;
}

/* Table styling overrides that penetrate component boundaries */
.activity-items-row :deep(.v-table) {
  background: transparent !important;
}

.activity-items-row :deep(.v-data-table__td) {
  background-color: white !important;
}

.activity-items-row :deep(.v-data-table__th) {
  background-color: rgb(var(--v-theme-nnTrueBlue)) !important;
}

.activity-items-row :deep(.v-data-table__tbody tr) {
  background-color: white !important;
}

.activity-items-row :deep(.v-card),
.activity-items-row :deep(.v-sheet) {
  background-color: transparent !important;
  box-shadow: none !important;
}
</style>
