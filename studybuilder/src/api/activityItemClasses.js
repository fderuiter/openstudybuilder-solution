import baseCollection from './baseCollection'
import repository from './repository'

const resource = 'activity-item-classes'
const api = baseCollection(resource)

export default {
  ...api,

  getDatasetTerms(activityItemClassUid, datasetUid, params) {
    return repository.get(
      `${resource}/${activityItemClassUid}/datasets/${datasetUid}/terms`,
      {
        params,
      }
    )
  },
}
