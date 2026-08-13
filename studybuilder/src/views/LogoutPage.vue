<template>
  <div />
</template>

<script>
import { useStudiesGeneralStore } from '@/stores/studies-general'

export default {
  mounted() {
    const studiesGeneralStore = useStudiesGeneralStore()
    studiesGeneralStore.unselectStudy()
    this.$auth.oauthLogout()
  },
}
</script>
