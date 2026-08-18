import { defineStore } from 'pinia'
import _isEqual from 'lodash/isEqual'

function deepClone(obj) {
  if (obj === null || obj === undefined) return obj
  return JSON.parse(JSON.stringify(obj))
}

export const useFormStore = defineStore('form', {
  state: () => ({
    form: null,
    history: [],
    future: [],
    checkpoints: [],
    _debounceTimeout: null,
  }),
  getters: {
    isEmpty: (state) => state.form === null,
    canUndo: (state) => state.history.length > 0,
    canRedo: (state) => state.future.length > 0,
    isDirty: (state) => state.history.length > 0,
  },
  actions: {
    save(form) {
      this.form = deepClone(form)
      this.history = []
      this.future = []
      this.checkpoints = []
    },
    reset() {
      this.form = {}
      this.history = []
      this.future = []
      this.checkpoints = []
    },
    isEqual(form) {
      return _isEqual(form, this.form)
    },
    pushState(state) {
      if (!state) return
      if (_isEqual(state, this.form)) return

      if (this._debounceTimeout) {
        clearTimeout(this._debounceTimeout)
      }

      const prevState = deepClone(this.form)

      this._debounceTimeout = setTimeout(() => {
        const lastHistoryState = this.history.length > 0 ? this.history[this.history.length - 1] : null
        if (prevState && !_isEqual(prevState, lastHistoryState)) {
          this.history.push(prevState)
          this.future = []
        }
        this._debounceTimeout = null
      }, 300)

      this.form = deepClone(state)
    },
    undo() {
      if (this._debounceTimeout) {
        clearTimeout(this._debounceTimeout)
        this._debounceTimeout = null
      }
      if (this.history.length > 0) {
        const prevState = this.history.pop()
        this.future.push(deepClone(this.form))
        this.form = deepClone(prevState)
        return this.form
      }
      return null
    },
    redo() {
      if (this.future.length > 0) {
        const nextState = this.future.pop()
        this.history.push(deepClone(this.form))
        this.form = deepClone(nextState)
        return this.form
      }
      return null
    },
    saveCheckpoint(state) {
      const stateToSave = state ? deepClone(state) : deepClone(this.form)
      this.checkpoints.push(stateToSave)
    },
    rollbackToCheckpoint() {
      if (this.checkpoints.length > 0) {
        const lastCheckpoint = this.checkpoints.pop()
        this.form = deepClone(lastCheckpoint)
        this.history = []
        this.future = []
        return this.form
      }
      return null
    },
    clearCheckpoints() {
      this.checkpoints = []
    }
  },
})
