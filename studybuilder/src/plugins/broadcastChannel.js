import { eventBusEmit } from '@/plugins/eventBus'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import { useStudyActivitiesStore } from '@/stores/studies-activities'
import { useEpochsStore } from '@/stores/studies-epochs'
import { useStudiesObjectivesStore } from '@/stores/studies-objectives'
import { useStudiesEndpointsStore } from '@/stores/studies-endpoints'
import { useStudiesCompoundsStore } from '@/stores/studies-compounds'
import { useStudyDataSuppliersStore } from '@/stores/studies-data-suppliers'
import { useFootnotesStore } from '@/stores/studies-footnotes'

const CHANNEL_NAME = 'equipose_study_sync_channel'
const TAB_ID = Math.random().toString(36).substring(2) + Date.now().toString(36)

let channel = null

if (typeof window !== 'undefined' && 'BroadcastChannel' in window) {
  try {
    channel = new BroadcastChannel(CHANNEL_NAME)
  } catch (e) {
    console.error('Failed to initialize BroadcastChannel:', e)
  }
}

/**
 * Broadcasts a study update event across browser tabs.
 * @param {string} studyUid - The identifier of the study that was updated.
 */
export function broadcastStudyUpdate(studyUid) {
  if (!studyUid) return

  const payload = {
    type: 'STUDY_UPDATED',
    studyUid: String(studyUid),
    senderTabId: TAB_ID,
    timestamp: Date.now(),
  }

  if (channel) {
    try {
      channel.postMessage(payload)
    } catch (e) {
      console.error('Failed to broadcast study update:', e)
    }
  }
}

/**
 * Refetches active domain stores asynchronously in the background.
 * Preserves active route and uncommitted text input state.
 * @param {string} studyUid
 * @param {object} router
 */
export async function refetchActiveDomainStores(studyUid, router) {
  if (!studyUid) return

  // 1. Capture active input state to ensure uncommitted text inputs aren't lost
  const activeElem =
    typeof document !== 'undefined' ? document.activeElement : null
  let activeInputInfo = null

  if (
    activeElem &&
    (activeElem.tagName === 'INPUT' ||
      activeElem.tagName === 'TEXTAREA' ||
      /** @type {HTMLElement} */ (activeElem).isContentEditable)
  ) {
    const inputElem = /** @type {HTMLInputElement | HTMLTextAreaElement} */ (
      activeElem
    )
    activeInputInfo = {
      elem: inputElem,
      value: inputElem.value,
      selectionStart: inputElem.selectionStart,
      selectionEnd: inputElem.selectionEnd,
    }
  }

  const studiesGeneralStore = useStudiesGeneralStore()
  const refetchPromises = []

  // Always fetch general study info if available
  if (studiesGeneralStore.getStudy) {
    refetchPromises.push(
      studiesGeneralStore.getStudy(studyUid, true).catch(() => {})
    )
  }

  const currentRouteName = router?.currentRoute?.value?.name || ''
  const currentRoutePath = router?.currentRoute?.value?.path || ''

  // Refetch domain stores if active based on route or loaded store state
  const activitiesStore = useStudyActivitiesStore()
  const epochsStore = useEpochsStore()
  const objectivesStore = useStudiesObjectivesStore()
  const endpointsStore = useStudiesEndpointsStore()
  const compoundsStore = useStudiesCompoundsStore()
  const dataSuppliersStore = useStudyDataSuppliersStore()
  const footnotesStore = useFootnotesStore()

  const isActivitiesActive =
    currentRouteName.includes('Activity') ||
    currentRoutePath.includes('/activities') ||
    activitiesStore.studyActivities.length > 0

  const isStructureActive =
    currentRouteName.includes('Structure') ||
    currentRouteName.includes('Epoch') ||
    currentRouteName.includes('Visit') ||
    currentRoutePath.includes('/structure') ||
    epochsStore.studyEpochs.length > 0

  const isProtocolElementsActive =
    currentRouteName.includes('ProtocolElements') ||
    currentRouteName.includes('Objective') ||
    currentRouteName.includes('Endpoint') ||
    currentRoutePath.includes('/protocol-elements') ||
    objectivesStore.studyObjectives.length > 0 ||
    endpointsStore.studyEndpoints.length > 0

  const isInterventionsActive =
    currentRouteName.includes('Intervention') ||
    currentRouteName.includes('Compound') ||
    currentRoutePath.includes('/interventions') ||
    compoundsStore.studyCompounds.length > 0

  const isDataSuppliersActive =
    currentRouteName.includes('DataSupplier') ||
    currentRoutePath.includes('/data-suppliers') ||
    dataSuppliersStore.studyDataSuppliers.length > 0

  if (isActivitiesActive) {
    refetchPromises.push(
      activitiesStore.fetchStudyActivities({ studyUid }).catch(() => {})
    )
    refetchPromises.push(
      activitiesStore.fetchStudyActivityInstances({ studyUid }).catch(() => {})
    )
    if (studiesGeneralStore.getSoaPreferences) {
      refetchPromises.push(
        studiesGeneralStore.getSoaPreferences().catch(() => {})
      )
    }
  }

  if (isStructureActive || isActivitiesActive) {
    refetchPromises.push(
      epochsStore.fetchStudyEpochs({ studyUid }).catch(() => {})
    )
    refetchPromises.push(
      epochsStore.fetchStudyVisits(studyUid, { page_size: 0 }).catch(() => {})
    )
  }

  if (isProtocolElementsActive) {
    refetchPromises.push(
      objectivesStore.fetchStudyObjectives({ studyUid }).catch(() => {})
    )
    refetchPromises.push(
      endpointsStore.fetchStudyEndpoints({ studyUid }).catch(() => {})
    )
    refetchPromises.push(
      footnotesStore.fetchStudyFootnotes({ studyUid }).catch(() => {})
    )
  }

  if (isInterventionsActive) {
    refetchPromises.push(
      compoundsStore.fetchStudyCompounds({ studyUid }).catch(() => {})
    )
    refetchPromises.push(
      compoundsStore.fetchStudyCompoundDosings(studyUid).catch(() => {})
    )
  }

  if (isDataSuppliersActive) {
    refetchPromises.push(
      dataSuppliersStore.fetchStudyDataSuppliers({ studyUid }).catch(() => {})
    )
  }

  await Promise.allSettled(refetchPromises)

  // Notify component eventBus for tab-local UI refreshes
  eventBusEmit('study-remote-updated', { studyUid })

  // Restore input state and cursor selection if user was editing
  if (
    activeInputInfo &&
    activeInputInfo.elem &&
    document.activeElement === activeInputInfo.elem
  ) {
    const inputElem = /** @type {HTMLInputElement | HTMLTextAreaElement} */ (
      activeInputInfo.elem
    )
    if (inputElem.value !== activeInputInfo.value) {
      inputElem.value = activeInputInfo.value
    }
    try {
      if (typeof activeInputInfo.selectionStart === 'number') {
        inputElem.setSelectionRange(
          activeInputInfo.selectionStart,
          activeInputInfo.selectionEnd
        )
      }
    } catch {
      // ignore input types without setSelectionRange support
    }
  }
}

/**
 * Initializes the BroadcastChannel listener for cross-tab updates.
 * @param {object} router
 */
export function initBroadcastChannelListener(router) {
  if (!channel) return

  channel.onmessage = (event) => {
    const data = event.data
    if (!data || data.type !== 'STUDY_UPDATED') return

    // Requirement 5: Ignore event if sent from this tab instance
    if (data.senderTabId === TAB_ID) return

    const incomingStudyUid = data.studyUid
    if (!incomingStudyUid) return

    const studiesGeneralStore = useStudiesGeneralStore()
    const activeStudy = studiesGeneralStore.selectedStudy
    const activeStudyUid = activeStudy?.uid
    const activeStudyId =
      activeStudy?.current_metadata?.identification_metadata?.study_id ||
      studiesGeneralStore.studyId

    // Requirement 5: Tabs viewing a different study ignore broadcast events for unrelated study identifiers
    if (!activeStudyUid && !activeStudyId) return

    if (
      activeStudyUid !== incomingStudyUid &&
      activeStudyId !== incomingStudyUid
    ) {
      return
    }

    // Requirement 2 & 4: Refetch active domain store data in background
    refetchActiveDomainStores(incomingStudyUid, router)
  }
}

export default {
  broadcastStudyUpdate,
  initBroadcastChannelListener,
  refetchActiveDomainStores,
  TAB_ID,
}
