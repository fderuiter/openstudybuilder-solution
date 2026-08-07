<template>
  <div>
    <SimpleFormDialog
      ref="formRef"
      :title="title"
      :help-items="helpItems"
      :open="open"
      @close="close"
      @submit="submit"
    >
      <template #body>
        <v-form ref="observer">
          <v-row data-cy="groupform-activity-group-class">
            <v-col>
              <v-text-field
                v-model="form.name"
                :label="
                  subgroup
                    ? $t('ActivityForms.subgroup_name')
                    : $t('ActivityForms.group_name')
                "
                data-cy="groupform-activity-group-field"
                :rules="[formRules.required]"
              />
            </v-col>
          </v-row>
          <SentenceCaseNameField
            v-model="form.name_sentence_case"
            :name="form.name"
          />
          <v-row>
            <v-col>
              <v-text-field
                v-model="form.abbreviation"
                :label="$t('ActivityForms.abbreviation')"
                data-cy="groupform-abbreviation-field"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-autocomplete
                v-model:search="nciSearchQuery"
                :items="nciConcepts"
                item-title="displayName"
                item-value="code"
                :label="$t('ActivityForms.nci_lookup_search') || 'NCI Concept Lookup (Search)'"
                placeholder="Type 3+ characters to search NCI..."
                :loading="loadingNci"
                clearable
                no-filter
                return-object
                data-cy="groupform-nci-lookup"
                @update:model-value="onNciConceptSelected"
              >
                <template #no-data>
                  <v-list-item v-if="nciError">
                    <v-list-item-title class="text-error">
                      API connection failure. Please try again or fill manually.
                    </v-list-item-title>
                  </v-list-item>
                  <v-list-item v-else-if="nciSearchQuery && nciSearchQuery.length >= 3 && !loadingNci">
                    <v-list-item-title>No results found</v-list-item-title>
                  </v-list-item>
                  <v-list-item v-else>
                    <v-list-item-title>Type at least 3 characters...</v-list-item-title>
                  </v-list-item>
                </template>
              </v-autocomplete>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-text-field
                v-model="form.nci_concept_id"
                :label="$t('ActivityForms.nci_concept_id')"
                data-cy="groupform-nci-concept-id-field"
                clearable
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-text-field
                v-model="form.nci_concept_name"
                :label="$t('ActivityForms.nci_concept_name')"
                data-cy="groupform-nci-concept-name-field"
                clearable
              />
            </v-col>
          </v-row>
          <v-row data-cy="groupform-definition-class">
            <v-col>
              <v-textarea
                v-model="form.definition"
                :label="$t('ActivityForms.definition')"
                data-cy="groupform-definition-field"
                auto-grow
                rows="1"
                :rules="[formRules.required]"
              />
            </v-col>
          </v-row>
          <v-row v-if="editing">
            <v-col>
              <v-textarea
                v-model="form.change_description"
                :label="$t('ActivityForms.change_description')"
                data-cy="groupform-change-description-field"
                auto-grow
                rows="1"
                :rules="[formRules.required]"
              />
            </v-col>
          </v-row>
        </v-form>
      </template>
    </SimpleFormDialog>
    <ConfirmDialog ref="confirm" :text-cols="6" :action-cols="5" />
  </div>
</template>

<script setup>
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import _isEmpty from 'lodash/isEmpty'
import activities from '@/api/activities'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog.vue'
import SentenceCaseNameField from '@/components/tools/SentenceCaseNameField.vue'
import { useFormStore } from '@/stores/form'
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const formStore = useFormStore()
const notificationHub = inject('notificationHub')
const formRules = inject('formRules')
const emit = defineEmits(['close'])
const formRef = ref()
const observer = ref()

import repository from '@/api/repository'

const nciSearchQuery = ref('')
const nciConcepts = ref([])
const loadingNci = ref(false)
const nciError = ref(false)

watch(nciSearchQuery, async (newVal) => {
  if (!newVal || newVal.trim().length < 3) {
    nciConcepts.value = []
    return
  }
  loadingNci.value = true
  nciError.value = false
  try {
    const response = await repository.get('integrations/nci/nci-lookup', {
      params: { q: newVal }
    })
    nciConcepts.value = (response.data || []).map(item => ({
      ...item,
      displayName: `[${item.code}] ${item.name}`
    }))
  } catch (err) {
    console.error('NCI lookup failed:', err)
    nciError.value = true
    nciConcepts.value = []
  } finally {
    loadingNci.value = false
  }
})

function onNciConceptSelected(concept) {
  if (concept) {
    form.value.nci_concept_id = concept.code
    form.value.nci_concept_name = concept.name
  } else {
    form.value.nci_concept_id = ''
    form.value.nci_concept_name = ''
  }
}

const props = defineProps({
  open: Boolean,
  editedGroupOrSubgroup: {
    type: Object,
    default: null,
  },
  subgroup: Boolean,
})

const form = ref({})
const editing = ref(false)
const helpItems = [
  'ActivityFormsGrouping.name',
  'ActivityFormsGrouping.definition',
]

const title = computed(() => {
  if (!props.subgroup) {
    return !_isEmpty(props.editedGroupOrSubgroup)
      ? t('ActivityForms.edit_group')
      : t('ActivityForms.add_group')
  } else {
    return !_isEmpty(props.editedGroupOrSubgroup)
      ? t('ActivityForms.edit_subgroup')
      : t('ActivityForms.add_subgroup')
  }
})

function initForm(value) {
  editing.value = true
  form.value = {
    name: value.name,
    name_sentence_case: value.name_sentence_case,
    definition: value.definition,
    change_description: '',
    abbreviation: value.abbreviation,
    nci_concept_id: value.nci_concept_id,
    nci_concept_name: value.nci_concept_name,
  }
  formStore.save(form.value)
}

watch(
  () => props.editedGroupOrSubgroup,
  (value) => {
    if (!_isEmpty(value)) {
      const source = props.subgroup ? 'activity-sub-groups' : 'activity-groups'
      activities.getObject(source, value.uid).then((resp) => {
        initForm(resp.data)
      })
    }
  },
  { immediate: true }
)

onMounted(() => {
  if (!_isEmpty(props.editedGroupOrSubgroup)) {
    initForm(props.editedGroupOrSubgroup)
  }
})

function close() {
  observer.value.reset()
  notificationHub.clearErrors()
  form.value = {}
  editing.value = false
  formRef.value.working = false
  formStore.reset()
  emit('close')
}

async function submit() {
  notificationHub.clearErrors()

  form.value.library_name = 'Sponsor' // Hardcoded for now at the Sinna and Mikkel request
  if (!props.editedGroupOrSubgroup) {
    if (!props.subgroup) {
      activities.create(form.value, 'activity-groups').then(
        () => {
          notificationHub.add({
            msg: t('ActivityForms.group_created'),
          })
          close()
        },
        () => {
          formRef.value.working = false
        }
      )
    } else {
      activities.create(form.value, 'activity-sub-groups').then(
        () => {
          notificationHub.add({
            msg: t('ActivityForms.subgroup_created'),
          })
          close()
        },
        () => {
          formRef.value.working = false
        }
      )
    }
  } else {
    if (!props.subgroup) {
      activities
        .update(
          props.editedGroupOrSubgroup.uid,
          form.value,
          {},
          'activity-groups'
        )
        .then(
          () => {
            notificationHub.add({
              msg: t('ActivityForms.group_updated'),
            })
            close()
          },
          () => {
            formRef.value.working = false
          }
        )
    } else {
      activities
        .update(
          props.editedGroupOrSubgroup.uid,
          form.value,
          {},
          'activity-sub-groups'
        )
        .then(
          () => {
            notificationHub.add({
              msg: t('ActivityForms.subgroup_updated'),
            })
            close()
          },
          () => {
            formRef.value.working = false
          }
        )
    }
  }
}
</script>
