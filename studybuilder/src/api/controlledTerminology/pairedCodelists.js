import repository from '../repository'

const resource = 'ct/paired-codelists'

export default {
  getCodelistTerms(codelistUid, params) {
    return repository.get(`${resource}/${codelistUid}/terms`, { params })
  },
}
