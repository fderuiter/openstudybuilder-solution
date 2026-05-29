export function processSoaData(soaRows, soaVisitRow, keepDisplayState, existingDisplayState) {
  const currentSelectionMatrix = {}
  const rowsDisplayState = keepDisplayState ? { ...existingDisplayState } : {}
  const rowVisibilityIndex = {}

  let currentSoaGroup = null
  let currentGroup = null
  let currentSubGroup = null

  // Helper to determine if row is activity row. Need to replicate logic of scheduleMethods.isActivityRow
  const isActivityRow = (row) => {
    if (!row.cells || !row.cells[0]) return false
    const style = row.cells[0].style
    return ['activity', 'activityPlaceholder', 'activityPlaceholderSubmitted'].includes(style)
  }

  for (const row of soaRows) {
    const rowUid = row.cells[0].refs[0]?.uid
    const key = `row-${rowUid}`
    if (row.cells && row.cells.length) {
      if (row.cells[0].style === 'soaGroup') {
        if (!keepDisplayState) {
          rowsDisplayState[key] = { value: false }
        }
        currentGroup = null
        currentSubGroup = null
        currentSoaGroup = rowUid
      } else if (row.cells[0].style === 'group') {
        if (!keepDisplayState) {
          rowsDisplayState[key] = {
            value: false,
            parent: currentSoaGroup,
          }
        }
        currentSubGroup = null
        currentGroup = rowUid
      } else if (row.cells[0].style === 'subGroup') {
        if (!keepDisplayState) {
          rowsDisplayState[key] = {
            value: false,
            parent: currentGroup,
          }
        }
        currentSubGroup = rowUid
      } else if (isActivityRow(row)) {
        const scheduleCells = row.cells.slice(1)
        if (!keepDisplayState) {
          rowsDisplayState[key] = {
            value: false,
            parent: currentSubGroup,
          }
        }
        if (row.cells[0].refs && row.cells[0].refs.length) {
          currentSelectionMatrix[row.cells[0].refs[0].uid] = {}
          for (const [visitIndex, cell] of soaVisitRow.entries()) {
            let props
            if (
              scheduleCells[visitIndex] &&
              scheduleCells[visitIndex].refs &&
              scheduleCells[visitIndex].refs.length
            ) {
              if (cell.refs && cell.refs.length === 1) {
                props = {
                  value: true,
                  uid: scheduleCells[visitIndex].refs[0].uid,
                }
              } else {
                props = {
                  value: true,
                  uid: scheduleCells[visitIndex].refs.map((ref) => ref.uid),
                }
              }
            } else {
              props = { value: false, uid: null }
            }
            if (cell.refs) {
              currentSelectionMatrix[row.cells[0].refs[0].uid][
                cell.refs[0].uid
              ] = props
            }
          }
        }
      }
    }
  }

  // Precompute row visibility index for O(1) lookup
  for (const row of soaRows) {
    const uid = row.cells[0].refs[0]?.uid
    const key = `row-${uid}`
    let isVisible = true

    if (row.cells[0].style !== 'soaGroup') {
      let currentKey = key
      // prettier-ignore
      while (true) { // eslint-disable-line no-constant-condition
        const state = rowsDisplayState[currentKey]
        if (state && state.parent !== undefined && state.parent !== null) {
          const parentKey = `row-${state.parent}`
          const parentState = rowsDisplayState[parentKey]
          if (parentState && !parentState.value) {
            isVisible = false
            break
          }
          currentKey = parentKey
          continue
        }
        break
      }
    }
    
    rowVisibilityIndex[key] = isVisible
  }

  return { currentSelectionMatrix, rowsDisplayState, rowVisibilityIndex }
}

self.onmessage = function (e) {
  const { soaRows, soaVisitRow, keepDisplayState, existingDisplayState } = e.data
  const result = processSoaData(soaRows, soaVisitRow, keepDisplayState, existingDisplayState)
  self.postMessage(result)
}
