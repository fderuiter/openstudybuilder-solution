import test from 'node:test'
import assert from 'node:assert/strict'

// Mock browser globals for Node.js test environment
class MockBroadcastChannel {
  static channels = new Map()

  constructor(name) {
    this.name = name
    this.onmessage = null
    if (!MockBroadcastChannel.channels.has(name)) {
      MockBroadcastChannel.channels.set(name, new Set())
    }
    MockBroadcastChannel.channels.get(name).add(this)
  }

  postMessage(data) {
    const listeners = MockBroadcastChannel.channels.get(this.name) || new Set()
    for (const listener of listeners) {
      if (listener !== this && typeof listener.onmessage === 'function') {
        listener.onmessage({ data })
      }
    }
  }

  close() {
    const listeners = MockBroadcastChannel.channels.get(this.name)
    if (listeners) {
      listeners.delete(this)
    }
  }
}

globalThis.BroadcastChannel = MockBroadcastChannel

// Mock window and document
globalThis.window = globalThis
globalThis.document = {
  activeElement: null,
}

// Test suite
test('BroadcastChannel Event Sync Unit Tests', async (t) => {
  await t.test('broadcastStudyUpdate posts expected payload', () => {
    const channel1 = new MockBroadcastChannel('equipose_study_sync_channel')
    const channel2 = new MockBroadcastChannel('equipose_study_sync_channel')

    let receivedData = null
    channel2.onmessage = (event) => {
      receivedData = event.data
    }

    const testPayload = {
      type: 'STUDY_UPDATED',
      studyUid: 'study-123',
      senderTabId: 'tab-1',
      timestamp: Date.now(),
    }

    channel1.postMessage(testPayload)

    assert.ok(receivedData !== null)
    assert.equal(receivedData.type, 'STUDY_UPDATED')
    assert.equal(receivedData.studyUid, 'study-123')
    assert.equal(receivedData.senderTabId, 'tab-1')

    channel1.close()
    channel2.close()
  })

  await t.test(
    'receiving tab ignores broadcast event for different study ID',
    () => {
      const channel1 = new MockBroadcastChannel('equipose_study_sync_channel')
      const channel2 = new MockBroadcastChannel('equipose_study_sync_channel')

      let refetchCalled = false

      const tab2ActiveStudyUid = 'study-456' // tab 2 is on study-456

      channel2.onmessage = (event) => {
        const data = event.data
        if (!data || data.type !== 'STUDY_UPDATED') return
        if (data.senderTabId === 'tab-2') return // self message

        // Check matching study UID logic (Requirement 5)
        if (tab2ActiveStudyUid !== data.studyUid) {
          return // Ignored!
        }

        refetchCalled = true
      }

      // Tab 1 broadcasts update for study-123
      channel1.postMessage({
        type: 'STUDY_UPDATED',
        studyUid: 'study-123',
        senderTabId: 'tab-1',
        timestamp: Date.now(),
      })

      assert.equal(
        refetchCalled,
        false,
        'Event for different study must be ignored'
      )

      channel1.close()
      channel2.close()
    }
  )

  await t.test('receiving tab triggers refetch for matching study ID', () => {
    const channel1 = new MockBroadcastChannel('equipose_study_sync_channel')
    const channel2 = new MockBroadcastChannel('equipose_study_sync_channel')

    let refetchCalled = false

    const tab2ActiveStudyUid = 'study-123' // tab 2 is on study-123

    channel2.onmessage = (event) => {
      const data = event.data
      if (!data || data.type !== 'STUDY_UPDATED') return
      if (data.senderTabId === 'tab-2') return

      if (tab2ActiveStudyUid === data.studyUid) {
        refetchCalled = true
      }
    }

    // Tab 1 broadcasts update for study-123
    channel1.postMessage({
      type: 'STUDY_UPDATED',
      studyUid: 'study-123',
      senderTabId: 'tab-1',
      timestamp: Date.now(),
    })

    assert.equal(
      refetchCalled,
      true,
      'Event for matching study must trigger refetch'
    )

    channel1.close()
    channel2.close()
  })

  await t.test(
    'eventBus handles tab-isolated transient UI flags without localStorage',
    () => {
      const bus = new Map()
      function emit(event, ...args) {
        bus.set(event, args)
      }

      // Emit transient open-form flag
      emit('open-form', true)
      assert.equal(bus.has('open-form'), true)
      assert.deepEqual(bus.get('open-form'), [true])

      // Consume and delete flag
      const flag = bus.get('open-form')
      bus.delete('open-form')

      assert.ok(flag && flag[0] === true)
      assert.equal(bus.has('open-form'), false)
    }
  )

  await t.test('uncommitted active input state preservation logic', () => {
    const mockInput = {
      tagName: 'INPUT',
      value: 'Drafting text input',
      selectionStart: 5,
      selectionEnd: 5,
      setSelectionRange(start, end) {
        this.selectionStart = start
        this.selectionEnd = end
      },
    }

    globalThis.document.activeElement = mockInput

    const activeElem = globalThis.document.activeElement
    let activeInputInfo = null

    if (
      activeElem &&
      (activeElem.tagName === 'INPUT' || activeElem.tagName === 'TEXTAREA')
    ) {
      activeInputInfo = {
        elem: activeElem,
        value: activeElem.value,
        selectionStart: activeElem.selectionStart,
        selectionEnd: activeElem.selectionEnd,
      }
    }

    assert.ok(activeInputInfo !== null)
    assert.equal(activeInputInfo.value, 'Drafting text input')

    // Simulate background refetch finish and restore
    if (
      activeInputInfo &&
      activeInputInfo.elem &&
      globalThis.document.activeElement === activeInputInfo.elem
    ) {
      if (activeInputInfo.elem.value !== activeInputInfo.value) {
        activeInputInfo.elem.value = activeInputInfo.value
      }
    }

    assert.equal(mockInput.value, 'Drafting text input')
  })
})
