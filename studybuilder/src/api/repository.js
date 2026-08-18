import axios from 'axios'

import { auth } from '@/plugins/auth'
import { notificationHub } from '@/plugins/notificationHub'
import { useGlobalConfig } from '@/main'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import { useErrorHandler } from '@/composables/errorHandler'
import { useFormStore } from '@/stores/form'

const _axios = axios.create()

const requestInterceptors = {
  onFulfilled: async function (config) {
    const studiesGeneralStore = useStudiesGeneralStore()
    if (config.method === 'get' && config.url.indexOf('studies/') !== -1) {
      config.params = config.params || {}

      if (
        config.params.specificStudyVersion !== undefined &&
        config.params.specificStudyVersion !== null
      ) {
        if (Number(config.params.specificStudyVersion) !== 0) {
          config.params.study_value_version = config.params.specificStudyVersion
        }
        delete config.params.specificStudyVersion
      } else {
        config.params.study_value_version =
          studiesGeneralStore.selectedStudyVersion
      }
    }

    const globalConfig = useGlobalConfig()
    config.baseURL = globalConfig.API_BASE_URL

    // the component used to display available rows per page uses -1 to describe all elements
    // but API expects 0 to be sent to fetch all items in a paginated query
    if (config?.params?.page_size === -1) {
      config.params.page_size = 0
    }
    const accessToken = await auth.getAccessToken()
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
      config.withCredentials = true
    } else {
      auth.clear()
    }

    // Check if we need to serialize filters
    if (
      config.method === 'get' &&
      config.params &&
      config.params.filters &&
      typeof config.params.filters !== 'string'
    ) {
      config.params.filters = JSON.stringify(config.params.filters)
    }

    return config
  },
  onRejected: function (error) {
    // Do something with request error
    return Promise.reject(error)
  },
}

const responseInterceptors = {
  onFulfilled: function (response) {
    // Just return unchanged response data
    return response
  },
  onRejected: function (error) {
    console.log(error)
    if (error.config && !error.config.ignoreErrors) {
      if (!error.response) {
        // We do not have a response, we don't know the tracing id, just display the error.message
        notificationHub.add({
          msg: error.message,
          type: 'error',
        })
      } else if (error.response.status === 401 || error.response.status === 403) {
        useErrorHandler(error)
      } else {
        // If status code is 422, display the validation error details from error.response.data.detail.
        // Otherwise, just display the error message contained in error.response.data.message.

        useErrorHandler(error)
      }

      // Revert local state to the most recent save-point if any API step fails
      try {
        const formStore = useFormStore()
        if (formStore.checkpoints && formStore.checkpoints.length > 0) {
          formStore.rollbackToCheckpoint()
        }
      } catch (e) {
        console.error('Failed to rollback on API error:', e)
      }
    }
    return Promise.reject(error)
  },
}

_axios.interceptors.request.use(
  requestInterceptors.onFulfilled,
  requestInterceptors.onRejected
)

// Add a response interceptor
_axios.interceptors.response.use(
  responseInterceptors.onFulfilled,
  responseInterceptors.onRejected
)

export default _axios
export { requestInterceptors, responseInterceptors }
