<template>
  <div class="d-flex align-center">
    <v-autocomplete
      v-model="studyById"
      :label="$t('StudyQuickSelectForm.study_id')"
      :items="studiesWithId"
      item-title="id"
      return-object
      :rules="[(value) => formRules.atleastone(value, studyByAcronym)]"
      variant="outlined"
      rounded="lg"
      density="compact"
      clearable
      :loading="loading"
      @update:model-value="autoPopulateAcronym"
    />
    <span class="mx-4">{{ $t('StudyQuickSelectForm.and_or') }}</span>
    <v-autocomplete
      v-model="studyByAcronym"
      :label="$t('StudyQuickSelectForm.study_acronym')"
      :items="studiesWithAcronym"
      item-title="acronym"
      return-object
      :rules="[(value) => formRules.atleastone(value, studyById)]"
      variant="outlined"
      rounded="lg"
      density="compact"
      clearable
      :loading="loading"
      @update:model-value="autoPopulateId"
    />
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import studyApi from '@/api/study'

// eslint-disable-next-line no-unused-vars
const props = defineProps({
  modelValue: {
    type: Object,
    default: null,
  },
})
const emit = defineEmits(['update:modelValue'])

const formRules = inject('formRules')

const studies = ref([])
const studyById = ref(null)
const studyByAcronym = ref(null)
const loading = ref(false)

const studiesWithId = computed(() => {
  let list = studies.value.filter((study) => study.id !== null)

  return list.sort((a, b) => {
    return a.id.localeCompare(b.id)
  })
})
const studiesWithAcronym = computed(() => {
  let list = studies.value.filter((study) => study.acronym !== null)

  return list.sort((a, b) => {
    return a.acronym.localeCompare(b.acronym)
  })
})

onMounted(() => {
  loading.value = true
  studyApi.getIds().then((resp) => {
    studies.value = resp.data
    loading.value = false
  })
})

function autoPopulateAcronym(study) {
  if (study && study.acronym) {
    studyByAcronym.value = study
  } else {
    studyByAcronym.value = null
  }
  emit('update:modelValue', study)
}
function autoPopulateId(study) {
  if (study && study.id) {
    studyById.value = study
  }
  emit('update:modelValue', study)
}
</script>
