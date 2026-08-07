<template>
  <div class="px-4 py-2 fill-height conflicts-dashboard">
    <!-- Header / Title -->
    <div class="page-header d-flex align-center justify-space-between mb-4">
      <div class="d-flex align-center">
        <div data-cy="page-title" class="page-title d-flex align-center">
          CDISC Controlled Terminology Conflict Resolution Dashboard
          <HelpButton :help-text="'Audit and resolve staging database conflicts before finalization.'" />
        </div>
      </div>
      <div class="queue-status d-flex align-center">
        <v-chip color="error" class="font-weight-bold" variant="flat">
          {{ conflicts.length }} Unresolved Conflicts
        </v-chip>
      </div>
    </div>

    <!-- Main Workspace Split Pane -->
    <v-row class="fill-height">
      <!-- Left Column: Active Inconsistency Queue (List) -->
      <v-col cols="12" md="4" class="d-flex flex-column fill-height">
        <v-card class="flex-grow-1 d-flex flex-column overflow-hidden" elevation="2">
          <v-card-title class="bg-primary text-white d-flex align-center py-3">
            <v-icon class="mr-2">mdi-alert-octagon-outline</v-icon>
            Active Conflicts Queue
          </v-card-title>

          <!-- Search and Filter bar inside left panel -->
          <div class="px-3 pt-3 pb-1 border-bottom bg-grey-lighten-4">
            <v-text-field
              v-model="searchQuery"
              density="compact"
              placeholder="Search Concept ID or Description..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              hide-details
              class="mb-2"
            />
            <v-btn-toggle
              v-model="filterType"
              mandatory
              density="compact"
              color="primary"
              variant="outlined"
              class="w-100 d-flex"
            >
              <v-btn value="all" class="flex-grow-1">All</v-btn>
              <v-btn value="codelist" class="flex-grow-1">Codelists</v-btn>
              <v-btn value="term" class="flex-grow-1">Terms</v-btn>
            </v-btn-toggle>
          </div>

          <!-- Queue Items List -->
          <v-list class="overflow-y-auto flex-grow-1 pa-2 bg-grey-lighten-5 list-container" density="compact" nav>
            <div v-if="loadingQueue" class="d-flex flex-column align-center justify-center py-10">
              <v-progress-circular indeterminate color="primary" class="mb-2" />
              <span class="text-subtitle-2 text-grey-darken-1">Loading queue...</span>
            </div>

            <div v-else-if="filteredConflicts.length === 0" class="d-flex flex-column align-center justify-center py-10 text-center px-4">
              <v-icon size="48" color="grey-lighten-1" class="mb-2">mdi-checkbox-marked-circle-outline</v-icon>
              <span class="font-weight-bold text-grey-darken-1">All Clean!</span>
              <span class="text-caption text-grey">No unresolved conflicts match your criteria.</span>
            </div>

            <v-card
              v-for="conflict in filteredConflicts"
              v-else
              :key="conflict.id"
              :color="selectedConflict?.id === conflict.id ? 'primary-lighten-5' : 'white'"
              :class="['mb-2 border', selectedConflict?.id === conflict.id ? 'border-primary border-opacity-100 elevation-1' : '']"
              ripple
              style="cursor: pointer"
              @click="selectConflict(conflict)"
            >
              <div class="pa-3">
                <div class="d-flex align-center justify-space-between mb-1">
                  <span class="font-weight-bold text-subtitle-2 text-primary">
                    {{ conflict.conceptId }}
                  </span>
                  <v-chip
                    :color="conflict.type.startsWith('codelist') ? 'teal' : 'indigo'"
                    size="x-small"
                    class="text-uppercase"
                    variant="flat"
                  >
                    {{ conflict.type.startsWith('codelist') ? 'Codelist' : 'Term' }}
                  </v-chip>
                </div>

                <div v-if="conflict.parentName" class="text-caption text-grey-darken-2 font-weight-bold mb-1">
                  {{ conflict.parentName }}
                </div>

                <div class="d-flex align-center text-caption mb-2">
                  <v-icon size="14" class="mr-1" color="grey-darken-1">mdi-cube-outline</v-icon>
                  <span class="text-grey-darken-3 font-weight-bold">Property:</span>
                  <v-chip size="x-small" variant="outlined" color="primary" class="ml-1 font-weight-bold">
                    {{ conflict.property }}
                  </v-chip>
                </div>

                <v-divider class="my-1" />

                <div class="text-caption text-error font-italic mt-1">
                  {{ conflict.inconsistency }}
                </div>
              </div>
            </v-card>
          </v-list>
        </v-card>
      </v-col>

      <!-- Right Column: Interactive Resolution Workspace -->
      <v-col cols="12" md="8" class="fill-height">
        <v-card class="fill-height d-flex flex-column" elevation="2">
          <v-card-title class="bg-secondary text-white py-3 d-flex align-center">
            <v-icon class="mr-2">mdi-television-play</v-icon>
            Conflict Resolution Workspace
          </v-card-title>

          <!-- Empty State (No selection) -->
          <div v-if="!selectedConflict" class="flex-grow-1 d-flex flex-column align-center justify-center bg-grey-lighten-4 py-12 px-6 text-center">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-arrow-left-bold-circle-outline</v-icon>
            <h3 class="text-h6 font-weight-bold text-grey-darken-2 mb-2">No Conflict Selected</h3>
            <p class="text-body-2 text-grey-darken-1 max-width-500">
              Select a terminology conflict from the left sidebar queue to compare raw imports side-by-side and commit a resolution to the staging database.
            </p>
          </div>

          <!-- Active Workspace -->
          <div v-else class="flex-grow-1 overflow-y-auto pa-4 bg-grey-lighten-5 d-flex flex-column">
            <!-- Conflict Metadata Header -->
            <v-card class="mb-4 pa-4 border bg-white" variant="flat">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="d-flex align-center">
                  <v-icon color="warning" size="24" class="mr-2">mdi-alert</v-icon>
                  <span class="text-h6 font-weight-bold text-grey-darken-3">
                    Inconsistency for {{ selectedConflict.conceptId }}
                  </span>
                </div>
                <v-chip color="error" class="text-uppercase font-weight-bold">
                  {{ selectedConflict.type.startsWith('codelist') ? 'Codelist Conflict' : 'Term Conflict' }}
                </v-chip>
              </div>

              <v-divider class="my-2" />

              <v-row class="text-body-2 text-grey-darken-3 pt-1">
                <v-col cols="12" sm="6">
                  <strong>Target Concept ID:</strong> {{ selectedConflict.conceptId }}
                </v-col>
                <v-col cols="12" sm="6">
                  <strong>Conflicting Property:</strong>
                  <v-chip color="primary" variant="tonal" size="small" class="font-weight-bold ml-1">
                    {{ selectedConflict.property }}
                  </v-chip>
                </v-col>
                <v-col cols="12">
                  <strong>Error Message:</strong>
                  <span class="text-error font-weight-bold ml-1 font-italic bg-error-lighten-5 px-2 py-1 rounded">
                    {{ selectedConflict.inconsistency }}
                  </span>
                </v-col>
              </v-row>
            </v-card>

            <!-- Loading Side-by-side details -->
            <div v-if="loadingDetails" class="flex-grow-1 d-flex flex-column align-center justify-center py-12">
              <v-progress-circular indeterminate size="50" color="primary" class="mb-3" />
              <span class="text-subtitle-1 text-grey-darken-1 font-weight-bold">
                Querying staging database...
              </span>
              <span class="text-caption text-grey">
                Loading side-by-side definitions for concept {{ selectedConflict.conceptId }}
              </span>
            </div>

            <!-- Resolution Controls -->
            <div v-else class="flex-grow-1 d-flex flex-column">
              <!-- Comparison Cards Pane -->
              <h3 class="text-subtitle-1 font-weight-bold text-grey-darken-3 mb-2 d-flex align-center">
                <v-icon color="primary" size="20" class="mr-1">mdi-compare</v-icon>
                1. Side-by-Side Comparison (Source Raw Packages)
              </h3>

              <v-row class="mb-4">
                <v-col
                  v-for="source in details.sources"
                  :key="source.rawId"
                  cols="12"
                  :sm="details.sources.length === 1 ? '12' : details.sources.length === 2 ? '6' : '4'"
                >
                  <v-card class="fill-height border d-flex flex-column overflow-hidden" variant="flat">
                    <!-- Package Header -->
                    <div class="bg-grey-lighten-3 px-3 py-2 border-bottom d-flex align-center justify-space-between">
                      <span class="text-caption font-weight-bold text-grey-darken-3 text-truncate max-width-150" :title="source.packageName">
                        {{ source.packageName }}
                      </span>
                      <v-chip v-if="source.packageVersion" size="x-small" color="grey" class="font-weight-bold">
                        {{ source.packageVersion }}
                      </v-chip>
                    </div>

                    <!-- Property Value Container -->
                    <v-card-text class="pa-3 flex-grow-1 bg-white">
                      <!-- Render terms list structural mismatch -->
                      <div v-if="selectedConflict.property === 'terms' && Array.isArray(source.value)" class="terms-scroll-list">
                        <div class="text-caption font-weight-bold text-grey mb-1">
                          Terms defined in this release ({{ source.value.length }}):
                        </div>
                        <v-sheet border class="pa-2 rounded bg-grey-lighten-4 overflow-y-auto" max-height="180">
                          <div
                            v-for="(term, termIdx) in source.value"
                            :key="termIdx"
                            class="text-caption py-1 border-bottom"
                          >
                            {{ term }}
                          </div>
                        </v-sheet>
                      </div>

                      <!-- Render simple string property value -->
                      <div v-else>
                        <div class="text-caption font-weight-bold text-grey mb-1">
                          Value:
                        </div>
                        <div class="text-body-2 font-weight-mono bg-grey-lighten-4 pa-3 rounded border word-break-break-all text-grey-darken-4 font-weight-bold min-height-80">
                          {{ source.value === null || source.value === undefined ? '(null / empty)' : source.value }}
                        </div>
                      </div>
                    </v-card-text>

                    <!-- Pick Value Shortcut -->
                    <div class="pa-2 bg-grey-lighten-4 border-top text-center">
                      <v-btn
                        variant="tonal"
                        color="primary"
                        size="small"
                        density="compact"
                        class="w-100 font-weight-bold"
                        prepend-icon="mdi-check"
                        @click="selectValue(source.value)"
                      >
                        Choose This Value
                      </v-btn>
                    </div>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Select Resolution state -->
              <h3 class="text-subtitle-1 font-weight-bold text-grey-darken-3 mb-2 d-flex align-center">
                <v-icon color="primary" size="20" class="mr-1">mdi-gavel</v-icon>
                2. Choose Correct Resolution
              </h3>

              <v-card class="pa-4 border bg-white mb-4" variant="flat">
                <v-radio-group v-model="resolutionMode" hide-details class="mb-3">
                  <v-radio value="source" label="Pick one of the imported source values" />
                  <v-radio value="custom" label="Provide a custom overriding value" />
                </v-radio-group>

                <!-- Render source picker -->
                <div v-if="resolutionMode === 'source'" class="ml-6 pl-2 border-left mb-3">
                  <v-radio-group v-model="selectedValue" hide-details>
                    <v-radio
                      v-for="(source, idx) in details.sources"
                      :key="idx"
                      :value="formatValueForRadio(source.value)"
                      class="mb-2"
                    >
                      <template #label>
                        <div class="d-flex flex-column">
                          <span class="text-body-2 font-weight-bold text-grey-darken-4">
                            {{ formatDisplayValue(source.value) }}
                          </span>
                          <span class="text-caption text-grey">
                            From Package: {{ source.packageName }} {{ source.packageVersion }}
                          </span>
                        </div>
                      </template>
                    </v-radio>
                  </v-radio-group>
                </div>

                <!-- Render custom text input -->
                <div v-else class="ml-6 pl-2 border-left mb-3">
                  <v-textarea
                    v-model="customValue"
                    label="Enter custom resolved value..."
                    variant="outlined"
                    density="compact"
                    rows="3"
                    hide-details
                    class="font-weight-mono text-body-2"
                    placeholder="Type the corrected definition or term value here..."
                  />
                </div>
              </v-card>

              <!-- Action committing resolution -->
              <v-btn
                color="success"
                size="large"
                class="w-100 font-weight-bold"
                :loading="resolving"
                prepend-icon="mdi-content-save"
                elevation="2"
                @click="commitResolution"
              >
                Commit Resolution directly to Staging Database
              </v-btn>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Notification snackbars/alerts -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="4000">
      {{ snackbarText }}
      <template #actions>
        <v-btn variant="text" @click="snackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/repository'
import HelpButton from '@/components/tools/HelpButton.vue'

// Reactive state
const conflicts = ref([])
const selectedConflict = ref(null)
const details = ref(null)
const loadingQueue = ref(false)
const loadingDetails = ref(false)
const resolving = ref(false)

// Search and filtering state
const searchQuery = ref('')
const filterType = ref('all')

// Resolution inputs state
const resolutionMode = ref('source') // 'source' or 'custom'
const selectedValue = ref('')
const customValue = ref('')

// Toast notifications
const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

// Compute filtered conflicts
const filteredConflicts = computed(() => {
  return conflicts.value.filter((conflict) => {
    // Search query matching
    const matchesSearch =
      searchQuery.value === '' ||
      conflict.conceptId.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      conflict.inconsistency.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (conflict.parentName && conflict.parentName.toLowerCase().includes(searchQuery.value.toLowerCase()))

    // Type filter matching
    let matchesType = true
    if (filterType.value === 'codelist') {
      matchesType = conflict.type.startsWith('codelist')
    } else if (filterType.value === 'term') {
      matchesType = conflict.type === 'term'
    }

    return matchesSearch && matchesType
  })
})

// Load Conflicts Queue from Backend API
async function fetchConflictsQueue() {
  loadingQueue.value = true
  try {
    const response = await api.get('/ct/conflicts')
    conflicts.value = response.data || []
  } catch (error) {
    console.error('Failed to load conflicts:', error)
    showToast('Failed to load conflicts from backend API.', 'error')
  } finally {
    loadingQueue.value = false
  }
}

// Select a conflict to review
async function selectConflict(conflict) {
  selectedConflict.value = conflict
  loadingDetails.value = true
  details.value = null
  resolutionMode.value = 'source'
  selectedValue.value = ''
  customValue.value = ''

  try {
    const response = await api.get('/ct/conflicts/' + conflict.id)
    details.value = response.data

    // Preset selection to the first non-empty option
    if (details.value?.sources?.length > 0) {
      const firstVal = details.value.sources[0].value
      selectValue(firstVal)
    }
  } catch (error) {
    console.error('Failed to load conflict details:', error)
    showToast('Failed to load conflict details.', 'error')
    selectedConflict.value = null
  } finally {
    loadingDetails.value = false
  }
}

// Set resolution value selection shortcut
function selectValue(val) {
  resolutionMode.value = 'source'
  selectedValue.value = formatValueForRadio(val)
}

// Commit resolution to staging database
async function commitResolution() {
  if (!selectedConflict.value) return

  let finalValue
  if (resolutionMode.value === 'custom') {
    finalValue = customValue.value
  } else {
    // Deserialize selectedValue
    try {
      finalValue = JSON.parse(selectedValue.value)
    } catch {
      finalValue = selectedValue.value
    }
  }

  resolving.value = true
  try {
    const response = await api.post('/ct/conflicts/' + selectedConflict.value.id + '/resolve', {
      value: finalValue,
    })

    if (response.data.status === 'success') {
      showToast('Conflict successfully resolved and committed directly to staging database!', 'success')
      
      // Reactive updates: splice the resolved conflict out of the active list
      const resolvedId = selectedConflict.value.id
      conflicts.value = conflicts.value.filter((c) => conflictIdToInt(c.id) !== conflictIdToInt(resolvedId))

      // Auto-select the next conflict in the queue if any exist
      if (filteredConflicts.value.length > 0) {
        selectConflict(filteredConflicts.value[0])
      } else {
        selectedConflict.value = null
        details.value = null
      }
    } else {
      showToast(response.data.message || 'Failed to resolve conflict.', 'error')
    }
  } catch (error) {
    console.error('Failed to submit resolution:', error)
    showToast('Failed to write resolution state directly to staging database.', 'error')
  } finally {
    resolving.value = false
  }
}

// Helpers
function conflictIdToInt(id) {
  return typeof id === 'string' ? parseInt(id, 10) : id
}

function formatValueForRadio(val) {
  if (Array.isArray(val)) {
    return JSON.stringify(val)
  }
  return typeof val === 'string' ? JSON.stringify(val) : String(val)
}

function formatDisplayValue(val) {
  if (val === null || val === undefined) return '(null / empty)'
  if (Array.isArray(val)) {
    return `[${val.join(', ')}]`
  }
  return String(val)
}

function showToast(text, color = 'success') {
  snackbarText.value = text
  snackbarColor.value = color
  snackbar.value = true
}

onMounted(() => {
  fetchConflictsQueue()
})
</script>

<style scoped>
.conflicts-dashboard {
  height: calc(100vh - 120px);
  min-height: 550px;
}
.list-container {
  height: calc(100vh - 300px);
  min-height: 350px;
}
.border {
  border: 1px solid #e0e0e0 !important;
  border-radius: 4px;
}
.border-bottom {
  border-bottom: 1px solid #e0e0e0 !important;
}
.border-left {
  border-left: 3px solid #1976d2 !important;
}
.word-break-break-all {
  word-break: break-all;
}
.min-height-80 {
  min-height: 80px;
}
.max-width-150 {
  max-width: 150px;
}
.max-width-500 {
  max-width: 500px;
}
.font-weight-mono {
  font-family: monospace, Courier, monospace;
}
.terms-scroll-list {
  max-height: 250px;
}
</style>
