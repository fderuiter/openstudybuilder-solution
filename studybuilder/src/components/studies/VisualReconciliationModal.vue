<template>
  <v-dialog
    :value="value"
    max-width="1100px"
    persistent
    @input="$emit('input', $event)"
  >
    <v-card>
      <v-card-title class="headline grey lighten-2">
        <v-icon left color="primary">mdi-source-branch</v-icon>
        Template Visual Reconciliation Tool
        <v-spacer></v-spacer>
        <v-btn icon @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="pt-4">
        <v-alert
          v-if="isLocked"
          type="warning"
          dense
          outlined
          class="mb-4"
        >
          <strong>Study is Locked:</strong> Template updates can only be merged into unlocked study drafts. Unlock this study to enable selective merging.
        </v-alert>

        <v-alert
          v-if="lineage.sync_status === 'NEEDS_REVIEW'"
          type="info"
          dense
          outlined
          class="mb-4"
        >
          <strong>Parent Template Updated:</strong> Parent template ({{ lineage.parent_template_uid }}) has new updates. Review field diffs below to selectively merge.
        </v-alert>

        <v-alert
          v-if="lineage.sync_status === 'RETIRED'"
          type="error"
          dense
          outlined
          class="mb-4"
        >
          <strong>Parent Template Retired:</strong> Parent template ({{ lineage.parent_template_uid }}) has been retired.
        </v-alert>

        <v-tabs v-model="activeTab" class="mb-4">
          <v-tab>
            <v-icon left>mdi-compare</v-icon>
            Visual Diff Comparison ({{ diffs.length }})
          </v-tab>
          <v-tab>
            <v-icon left>mdi-history</v-icon>
            Audit History ({{ auditHistory.length }})
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="activeTab">
          <!-- Diff Comparison Tab -->
          <v-tab-item>
            <div v-if="loading" class="text-center py-6">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
              <div class="mt-2 text-subtitle-2">Loading field-level diffs...</div>
            </div>

            <div v-else-if="diffs.length === 0" class="text-center py-6">
              <v-icon size="48" color="success">mdi-check-circle-outline</v-icon>
              <div class="text-h6 mt-2">Study is In Sync</div>
              <div class="grey--text">No metadata or design differences found between active study draft and parent template.</div>
            </div>

            <div v-else>
              <div class="d-flex align-center mb-3">
                <v-btn
                  small
                  outlined
                  color="primary"
                  class="mr-2"
                  :disabled="isLocked"
                  @click="selectAll"
                >
                  Select All
                </v-btn>
                <v-btn
                  small
                  outlined
                  class="mr-4"
                  :disabled="isLocked"
                  @click="deselectAll"
                >
                  Deselect All
                </v-btn>
                <span class="text-caption grey--text">
                  Selected {{ selectedFields.length }} of {{ diffs.length }} differences for merge
                </span>
              </div>

              <v-simple-table dense class="elevation-1 border">
                <thead>
                  <tr>
                    <th style="width: 50px;">Merge</th>
                    <th>Category</th>
                    <th>Field Label</th>
                    <th>Change Type</th>
                    <th>Current Study Value</th>
                    <th>Parent Template Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in diffs" :key="item.field">
                    <td>
                      <v-checkbox
                        v-model="selectedFields"
                        :value="item.field"
                        dense
                        hide-details
                        class="ma-0"
                        :disabled="isLocked"
                      ></v-checkbox>
                    </td>
                    <td>
                      <v-chip x-small color="grey lighten-2">{{ item.category }}</v-chip>
                    </td>
                    <td class="font-weight-medium">{{ item.label }}</td>
                    <td>
                      <v-chip
                        x-small
                        :color="getChangeColor(item.change_type)"
                        dark
                      >
                        {{ item.change_type }}
                      </v-chip>
                    </td>
                    <td class="red--text text--darken-2 red lighten-5 px-2 py-1">
                      {{ formatValue(item.current_value) }}
                    </td>
                    <td class="green--text text--darken-2 green lighten-5 px-2 py-1">
                      {{ formatValue(item.template_value) }}
                    </td>
                  </tr>
                </tbody>
              </v-simple-table>

              <v-textarea
                v-model="comments"
                label="Reconciliation Comments / Reason for Change"
                rows="2"
                class="mt-4"
                dense
                outlined
                hide-details
                :disabled="isLocked"
              ></v-textarea>
            </div>
          </v-tab-item>

          <!-- Audit History Tab -->
          <v-tab-item>
            <v-data-table
              :headers="historyHeaders"
              :items="auditHistory"
              dense
              class="elevation-1"
            >
              <template #[`item.timestamp`]="{ item }">
                {{ formatDate(item.timestamp) }}
              </template>
              <template #[`item.decisions`]="{ item }">
                <v-chip
                  v-for="d in item.decisions"
                  :key="d.field"
                  x-small
                  :color="d.decision === 'ACCEPTED' ? 'success' : 'grey'"
                  class="mr-1 mb-1"
                >
                  {{ d.field }}: {{ d.decision }}
                </v-chip>
              </template>
            </v-data-table>
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn text @click="close">Cancel</v-btn>
        <v-btn
          color="primary"
          :disabled="isLocked || selectedFields.length === 0 || loading"
          :loading="merging"
          @click="submitReconciliation"
        >
          <v-icon left>mdi-merge</v-icon>
          Merge Selected ({{ selectedFields.length }})
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import studyApi from '@/api/study'

export default {
  name: 'VisualReconciliationModal',
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    studyUid: {
      type: String,
      required: true,
    },
    isLocked: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['input', 'reconciled'],
  data() {
    return {
      activeTab: 0,
      loading: false,
      merging: false,
      lineage: {},
      diffs: [],
      selectedFields: [],
      comments: '',
      auditHistory: [],
      historyHeaders: [
        { text: 'Timestamp', value: 'timestamp' },
        { text: 'User ID', value: 'user_id' },
        { text: 'Parent Template Version', value: 'parent_template_version' },
        { text: 'Field Decisions', value: 'decisions', sortable: false },
        { text: 'Comments', value: 'comments' },
      ],
    }
  },
  watch: {
    value(val) {
      if (val && this.studyUid) {
        this.fetchData()
      }
    },
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const [lineageRes, diffRes, historyRes] = await Promise.all([
          studyApi.getLineage(this.studyUid),
          studyApi.getReconciliationDiff(this.studyUid),
          studyApi.getReconciliationHistory(this.studyUid),
        ])
        this.lineage = lineageRes.data || {}
        this.diffs = diffRes.data?.diffs || []
        this.auditHistory = historyRes.data || []
        this.selectedFields = this.diffs.map((d) => d.field)
      } catch (err) {
        console.error('Failed to load reconciliation data', err)
      } finally {
        this.loading = false
      }
    },
    selectAll() {
      this.selectedFields = this.diffs.map((d) => d.field)
    },
    deselectAll() {
      this.selectedFields = []
    },
    getChangeColor(changeType) {
      if (changeType === 'ADDED') return 'success'
      if (changeType === 'REMOVED') return 'error'
      return 'warning'
    },
    formatValue(val) {
      if (val === null || val === undefined) return '(none)'
      if (typeof val === 'object') return JSON.stringify(val)
      return String(val)
    },
    formatDate(ts) {
      if (!ts) return ''
      return new Date(ts).toLocaleString()
    },
    async submitReconciliation() {
      if (this.isLocked) return
      this.merging = true
      try {
        await studyApi.reconcile(this.studyUid, {
          selected_fields: this.selectedFields,
          comments: this.comments,
        })
        this.$emit('reconciled')
        this.close()
      } catch (err) {
        console.error('Reconciliation failed', err)
      } finally {
        this.merging = false
      }
    },
    close() {
      this.$emit('input', false)
    },
  },
}
</script>
