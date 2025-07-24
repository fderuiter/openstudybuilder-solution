<template>
  <HorizontalStepperForm
    ref="stepper"
    :title="title"
    :steps="steps"
    :form-observer-getter="getObserver"
    :help-items="helpItems"
    :extra-step-validation="extraValidation"
    @close="close"
    @save="submit"
  >
    <template #[`step.activities`]>
      <v-form ref="activitiesForm">
        <v-row data-cy="instanceform-activity-class">
          <v-col cols="4">
            <v-autocomplete
              v-model="selectedActivity"
              :rules="[formRules.required]"
              :items="activities"
              :label="$t('ActivityForms.activity')"
              data-cy="instanceform-activity-dropdown"
              item-title="name"
              density="compact"
              clearable
              class="mt-4"
              return-object
              @update:model-value="clearGroupings"
              @update:search="updateActivities"
            />
          </v-col>
        </v-row>
        <v-alert
          v-if="selectedActivity && selectedActivity.status !== statuses.FINAL"
          density="compact"
          type="warning"
          class="text-white mb-4"
          :text="draftActivityAlert"
        />
        <v-row>
          <v-col>
            <v-data-table
              v-if="selectedActivity"
              v-model="selectedGroupings"
              class="mb-3 pb-3"
              show-select
              :headers="headers"
              item-value="activity_subgroup_uid"
              data-cy="instanceform-activitygroup-table"
              :items="selectedActivity.activity_groupings"
              return-object
            >
              <template #bottom />
            </v-data-table>
          </v-col>
        </v-row>
      </v-form>
      <v-spacer />
    </template>
    <template #[`step.type`]>
      <v-form ref="typeForm">
        <v-row data-cy="instanceform-instanceclass-class">
          <v-col cols="4">
            <v-select
              v-model="form.activity_instance_class_uid"
              :items="activityInstanceClasses"
              :label="$t('ActivityForms.instance_class')"
              data-cy="instanceform-instanceclass-dropdown"
              item-title="name"
              item-value="uid"
              density="compact"
              clearable
              class="mt-4"
              :rules="[formRules.required]"
            />
          </v-col>
        </v-row>
      </v-form>
    </template>
    <template #[`step.basicData`]>
      <v-form ref="basicDataForm">
        <v-row>
          <v-col cols="8">
            <v-text-field
              v-model="form.name"
              :label="$t('ActivityForms.activity_ins_name')"
              data-cy="instanceform-instancename-field"
              :rules="[formRules.required]"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="8">
            <SentenceCaseNameField
              v-model="form.name_sentence_case"
              :name="form.name"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="8">
            <v-textarea
              v-model="form.definition"
              :label="$t('ActivityForms.definition')"
              data-cy="instanceform-definition-field"
              auto-grow
              rows="2"
              :rules="[formRules.required]"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="8">
            <v-text-field
              v-model="form.nci_concept_id"
              :label="$t('ActivityTable.nci_concept_id')"
              data-cy="instanceform-nciconceptid-field"
              density="compact"
              clearable
            />
          </v-col>
          <v-col cols="8">
            <v-text-field
              v-model="form.nci_concept_name"
              :label="$t('ActivityTable.nci_concept_name')"
              data-cy="instanceform-nciconceptname-field"
              density="compact"
              clearable
            />
          </v-col>
        </v-row>
        <v-row v-if="checkIfNumericFindings">
          <v-col cols="8">
            <v-text-field
              v-model="form.molecular_weight"
              :label="$t('ActivityForms.molecular_weight')"
              data-cy="instanceform-molecularweight-field"
              type="number"
              clearable
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="8">
            <v-text-field
              v-model="form.topic_code"
              :label="$t('ActivityForms.topicCode')"
              data-cy="instanceform-topiccode-field"
              :rules="[formRules.required]"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="8">
            <v-text-field
              v-model="form.adam_param_code"
              :label="$t('ActivityForms.adamCode')"
              data-cy="instanceform-adamcode-field"
              hide-details
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-checkbox
              v-model="form.is_required_for_activity"
              :label="$t('ActivityForms.is_required_for_activity')"
              data-cy="instanceform-requiredforactivity-checkbox"
            />
            <v-checkbox
              v-model="form.is_default_selected_for_activity"
              :label="$t('ActivityForms.is_default_selected_for_activity')"
            />
            <v-checkbox
              v-model="form.is_research_lab"
              :label="$t('ActivityForms.is_research_lab')"
            />
          </v-col>
          <v-col>
            <v-checkbox
              v-model="form.is_data_sharing"
              :label="$t('ActivityForms.is_data_sharing')"
            />
            <v-checkbox
              v-model="form.is_legacy_usage"
              :label="$t('ActivityForms.is_legacy_usage')"
            />
          </v-col>
        </v-row>
      </v-form>
    </template>
  </HorizontalStepperForm>
  <ConfirmDialog ref="confirm" :text-cols="6" :action-cols="5" />
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import activityInstanceClassesApi from '@/api/activityInstanceClasses'
import activitiesApi from '@/api/activities'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import libraries from '@/constants/libraries'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm.vue'
import SentenceCaseNameField from '@/components/tools/SentenceCaseNameField.vue'
import { useFormStore } from '@/stores/form'
import statuses from '@/constants/statuses'
import parameters from '@/constants/parameters'

const source = 'activity-instances'
const props = defineProps({
  editedActivity: {
    type: Object,
    default: null,
  },
})

const eventBusEmit = inject('eventBusEmit')
const formRules = inject('formRules')
const emit = defineEmits(['close'])
const { t } = useI18n()
const formStore = useFormStore()
const stepper = ref()
const activitiesForm = ref()
const typeForm = ref()
const basicDataForm = ref()

const form = ref({ activity_groupings: [] })
const activities = ref([])
const activityInstanceClasses = ref([])
const steps = ref(getInitialSteps())
const helpItems = [
  'ActivityFormsInstantiations.activities',
  'ActivityFormsInstantiations.activity_group',
  'ActivityFormsInstantiations.select_type',
  'ActivityFormsInstantiations.name',
  'ActivityFormsInstantiations.definition',
  'ActivityFormsInstantiations.nci_concept_id',
  'ActivityFormsInstantiations.topicCode',
  'ActivityFormsInstantiations.adamCode',
  'ActivityFormsInstantiations.is_required_for_activity',
  'ActivityFormsInstantiations.is_default_selected_for_activity',
  'ActivityFormsInstantiations.is_data_sharing',
  'ActivityFormsInstantiations.is_legacy_usage',
]
const headers = [
  {
    title: t('ActivityFormsInstantiations.activity_group'),
    key: 'activity_group_name',
  },
  {
    title: t('ActivityFormsInstantiations.activity_subgroup'),
    key: 'activity_subgroup_name',
  },
]
const selectedActivity = ref(null)
const previouslySelectedActivity = ref(null)
const selectedGroupings = ref([])

const checkIfNumericFindings = computed(() => {
  return (
    activityInstanceClasses.value.find(
      (instanceClass) =>
        instanceClass.uid === form.value.activity_instance_class_uid
    ).name === parameters.NUMERIC_FINDINGS
  )
})

const title = computed(() => {
  return props.editedActivity
    ? t('ActivityForms.editInstance')
    : t('ActivityForms.addInstance')
})

const draftActivityAlert = computed(() => {
  return props.editedActivity
    ? t('ActivityForms.draft_activity_edit_alert', {
        state: selectedActivity.value.status.toUpperCase(),
      })
    : t('ActivityForms.draft_activity_create_alert', {
        state: selectedActivity.value.status.toUpperCase(),
      })
})

watch(activities, () => {
  if (props.editedActivity) {
    setActivityGroupings()
  }
})

watch(
  () => props.editedActivity,
  (value) => {
    if (value) {
      activitiesApi.getObject(source, value.uid).then((resp) => {
        initForm(resp.data)
      })
    }
    if (props.editedActivity && activities.value.length > 0) {
      setActivityGroupings()
    }
  },
  { immediate: true }
)

watch(selectedActivity, () => {
  if (props.editedActivity && activities.value.length > 0) {
    setActivityGroupings()
  }
})

onMounted(() => {
  if (props.editedActivity) {
    initForm(props.editedActivity)
  }
  getActivities()
  activityInstanceClassesApi.getAll({ page_size: 0 }).then((resp) => {
    activityInstanceClasses.value = resp.data.items
  })
})

function initForm(value) {
  form.value = {
    name: value.name,
    activity_instance_class_uid: value.activity_instance_class.uid,
    name_sentence_case: value.name_sentence_case,
    nci_concept_id: value.nci_concept_id,
    nci_concept_name: value.nci_concept_name,
    molecular_weight: value.molecular_weight,
    definition: value.definition,
    change_description: value.change_description,
    activity_sub_groups: value.activity_sub_groups,
    topic_code: value.topic_code,
    adam_param_code: value.adam_param_code,
    is_research_lab: value.is_research_lab,
    is_required_for_activity: value.is_required_for_activity,
    is_default_selected_for_activity: value.is_default_selected_for_activity,
    is_data_sharing: value.is_data_sharing,
    is_legacy_usage: value.is_legacy_usage,
    activity_groupings: [],
  }
  formStore.save(form.value)
}

function getInitialSteps() {
  return [
    {
      name: 'activities',
      title: t('ActivityForms.select_activities'),
    },
    { name: 'type', title: t('ActivityForms.select_class') },
    { name: 'basicData', title: t('ActivityForms.addBasicData') },
  ]
}

async function extraValidation(step) {
  if (selectedActivity.value.status !== statuses.FINAL) {
    return false
  }
  if (step !== 1) {
    return true
  }
  if (selectedGroupings.value.length === 0) {
    eventBusEmit('notification', {
      msg: t('ActivityForms.grouping_selection_info'),
      type: 'info',
    })
    return false
  }
  return true
}

function close() {
  emit('close')
  form.value = { activity_groupings: [] }
  selectedActivity.value = null
  selectedGroupings.value = []
  formStore.reset()
  stepper.value.reset()
  stepper.value.loading = false
}

async function submit() {
  form.value.library_name = libraries.LIBRARY_SPONSOR
  form.value.activities = [form.value.activities]
  selectedGroupings.value = selectedGroupings.value.filter(function (val) {
    return val !== undefined
  })
  selectedGroupings.value.forEach((grouping) => {
    form.value.activity_groupings.push({
      activity_uid: selectedActivity.value.uid,
      activity_group_uid: grouping.activity_group_uid,
      activity_subgroup_uid: grouping.activity_subgroup_uid,
    })
  })
  if (form.value.molecular_weight === '') {
    form.value.molecular_weight = null
  }
  if (!props.editedActivity) {
    activitiesApi.create(form.value, source).then(
      () => {
        eventBusEmit('notification', {
          msg: t('ActivityForms.activity_created'),
        })
        close()
      },
      () => {
        stepper.value.loading = false
      }
    )
  } else {
    activitiesApi.update(props.editedActivity.uid, form.value, {}, source).then(
      () => {
        eventBusEmit('notification', {
          msg: t('ActivityForms.activity_updated'),
        })
        close()
      },
      () => {
        stepper.value.loading = false
      }
    )
  }
}

function getObserver(step) {
  if (step === 1) return activitiesForm.value
  if (step === 2) return typeForm.value
  if (step === 3) return basicDataForm.value
}

function getActivities(searchstring) {
  // Get filtered activities for search string in autocomplete
  const params = {
    page_size: 20,
    filters: {
      library_name: { v: [libraries.LIBRARY_SPONSOR] },
    },
  }
  if (searchstring) {
    params.filters.name = { v: [searchstring], op: 'co' }
  }
  activitiesApi.get(params, 'activities').then((resp) => {
    const fetched_activities = resp.data.items
    // Check if the selected activity is in the fetched activities, fetch it if not
    const params = {
      page_size: 2,
      filters: {
        uid: { v: [], op: 'eq' },
      },
    }
    if (
      props.editedActivity &&
      props.editedActivity.activities.length > 0 &&
      !fetched_activities.some(
        (act) => act.uid === props.editedActivity.activities[0].uid
      )
    ) {
      params.filters.uid.v.push(props.editedActivity.activities[0].uid)
    }
    if (
      selectedActivity.value &&
      !fetched_activities.some((act) => act.uid === selectedActivity.value.uid)
    ) {
      params.filters.uid.v.push(selectedActivity.value.uid)
    }
    if (params.filters.uid.v.length > 0) {
      // The selected activity is not in the fetched activities, fetch it
      activitiesApi.get(params, 'activities').then((resp) => {
        if (resp.data.items.length > 0) {
          fetched_activities.push(resp.data.items[0])
          activities.value = fetched_activities
        }
      })
    } else {
      activities.value = fetched_activities
    }
  })
}

function setActivityGroupings() {
  if (
    !selectedActivity.value &&
    props.editedActivity &&
    props.editedActivity.activities.length > 0
  ) {
    // editedActivity is set, but selectedActivity is not set.
    // This means that the form is newly opened to edit an existing instance.
    // Set selectedActivity to the activity of the edited instance.
    selectedActivity.value = activities.value.find(
      (act) => act.uid === props.editedActivity.activities[0].uid
    )
    previouslySelectedActivity.value = selectedActivity.value
    if (props.editedActivity.activity_groupings.length > 0) {
      selectedGroupings.value = []
      props.editedActivity.activity_groupings.forEach((grouping) => {
        selectedGroupings.value.push(
          selectedActivity.value.activity_groupings.find(
            (group) =>
              group.activity_group_uid === grouping.activity_group.uid &&
              group.activity_subgroup_uid === grouping.activity_subgroup.uid
          )
        )
      })
    }
  } else if (!selectedActivity.value) {
    // No activity is selected, clear groupings
    selectedGroupings.value = []
  }
}

function clearGroupings() {
  if (
    selectedActivity.value &&
    previouslySelectedActivity.value &&
    selectedActivity.value.uid === previouslySelectedActivity.value.uid
  ) {
    // No change, just return
    return
  }
  selectedGroupings.value = []
  previouslySelectedActivity.value = selectedActivity.value
}

function updateActivities(value) {
  if (selectedActivity.value && value === selectedActivity.value.name) {
    // The v-autocomplete got focus, which triggers a needless search with the current value.
    return
  }
  getActivities(value)
}
</script>
<style lang="scss" scoped>
.text-white {
  color: white !important;
}
</style>
