import { reactive, ref } from 'vue'
import { deepClone } from './deepClone.js'
import assert from 'node:assert/strict'
import test, { describe } from 'node:test'

describe('deepClone Utility', () => {
  test('clones primitive values and null/undefined', () => {
    assert.equal(deepClone(42), 42)
    assert.equal(deepClone('hello'), 'hello')
    assert.equal(deepClone(true), true)
    assert.equal(deepClone(null), null)
    assert.equal(deepClone(undefined), undefined)
  })

  test('preserves Date objects', () => {
    const date = new Date('2026-08-25T10:00:00Z')
    const cloned = deepClone(date)
    assert.notEqual(cloned, date)
    assert.ok(cloned instanceof Date)
    assert.equal(cloned.getTime(), date.getTime())
    assert.equal(cloned.toISOString(), date.toISOString())
  })

  test('preserves RegExp objects', () => {
    const regex = /test-pattern/gi
    const cloned = deepClone(regex)
    assert.notEqual(cloned, regex)
    assert.ok(cloned instanceof RegExp)
    assert.equal(cloned.source, 'test-pattern')
    assert.equal(cloned.flags, 'gi')
  })

  test('preserves Map collections', () => {
    const map = new Map()
    const key = { id: 1 }
    const dateValue = new Date('2026-01-01')
    map.set(key, dateValue)

    const cloned = deepClone(map)
    assert.notEqual(cloned, map)
    assert.ok(cloned instanceof Map)
    assert.equal(cloned.size, 1)

    const [clonedKey, clonedValue] = Array.from(cloned.entries())[0]
    assert.notEqual(clonedKey, key)
    assert.deepEqual(clonedKey, { id: 1 })
    assert.ok(clonedValue instanceof Date)
    assert.equal(clonedValue.getTime(), dateValue.getTime())
  })

  test('preserves Set collections', () => {
    const set = new Set()
    const obj = { name: 'set-item' }
    set.add(obj)

    const cloned = deepClone(set)
    assert.notEqual(cloned, set)
    assert.ok(cloned instanceof Set)
    assert.equal(cloned.size, 1)

    const [clonedObj] = Array.from(cloned.values())
    assert.notEqual(clonedObj, obj)
    assert.deepEqual(clonedObj, { name: 'set-item' })
  })

  test('handles circular references safely without infinite recursion', () => {
    const parent = { name: 'parent' }
    parent.self = parent

    const cloned = deepClone(parent)
    assert.notEqual(cloned, parent)
    assert.equal(cloned.name, 'parent')
    assert.equal(cloned.self, cloned)
  })

  test('unwraps Vue 3 reactive proxies safely', () => {
    const state = reactive({
      title: 'Clinical Trial',
      startDate: new Date('2026-05-01'),
      metadata: reactive({
        tags: new Set(['phase1', 'pivotal']),
        mapping: new Map([['a', 100]]),
      }),
    })

    const cloned = deepClone(state)

    // Modification to cloned object should not affect original reactive state
    cloned.title = 'Updated Title'
    cloned.startDate.setFullYear(2030)
    cloned.metadata.tags.add('new-tag')

    assert.equal(state.title, 'Clinical Trial')
    assert.equal(state.startDate.getFullYear(), 2026)
    assert.equal(state.metadata.tags.has('new-tag'), false)

    // Types must be preserved
    assert.ok(cloned.startDate instanceof Date)
    assert.ok(cloned.metadata.tags instanceof Set)
    assert.ok(cloned.metadata.mapping instanceof Map)
  })

  test('unwraps Vue refs if passed as value', () => {
    const formRef = ref({
      name: 'Ref Form',
      created: new Date('2026-02-02'),
    })

    const cloned = deepClone(formRef.value)
    assert.equal(cloned.name, 'Ref Form')
    assert.ok(cloned.created instanceof Date)
  })
})
