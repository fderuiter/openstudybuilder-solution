import baseCollection from './baseCollection'
import repository from './repository'

const resource = 'activity-instance-classes'
const api = baseCollection(resource)

export default {
  ...api,

  getActivityItemClasses(activityInstanceClassUid) {
    return repository.get(
      `${resource}/${activityInstanceClassUid}/activity-item-classes`
    )
  },
  getModelMappingDatasets(params) {
    return repository.get(`${resource}/model-mappings/datasets`, { params })
  },
}
