import { defineStore } from 'pinia'

export const useTablesLayoutStore = defineStore('tablesLayout', {
  state: () => ({
    columns: {},
  }),

  actions: {
    initiateColumns() {
      let columnsFromLocalStorage = {}
      const rawColumns =
        localStorage.getItem('studybuilder:columns') ||
        localStorage.getItem('columns')
      if (rawColumns != null) {
        columnsFromLocalStorage = JSON.parse(rawColumns)
      }
      this.columns = columnsFromLocalStorage
    },
    setColumns(columns) {
      for (const [key, value] of columns) {
        this.columns[key] = value
      }
      localStorage.setItem('studybuilder:columns', JSON.stringify(this.columns))
    },
  },
})
