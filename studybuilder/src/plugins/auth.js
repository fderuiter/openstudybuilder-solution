import { eventBusEmit } from './eventBus'
import {
  UserManager,
  WebStorageStateStore,
  InMemoryWebStorage,
} from 'oidc-client-ts'
import roles from '@/constants/roles'
import { Buffer } from 'buffer'

let manager = null

function extractAndFlattenRoles(data) {
  const roles = new Set()

  if (data && data.roles) {
    if (Array.isArray(data.roles)) {
      data.roles.forEach((r) => roles.add(String(r)))
    } else if (typeof data.roles === 'string') {
      roles.add(data.roles)
    }
  }

  if (
    data &&
    data.realm_access &&
    typeof data.realm_access === 'object' &&
    data.realm_access !== null &&
    Array.isArray(data.realm_access.roles)
  ) {
    data.realm_access.roles.forEach((r) => roles.add(String(r)))
  }

  if (
    data &&
    data.resource_access &&
    typeof data.resource_access === 'object' &&
    data.resource_access !== null
  ) {
    for (const clientKey of Object.keys(data.resource_access)) {
      const clientConfig = data.resource_access[clientKey]
      if (
        clientConfig &&
        typeof clientConfig === 'object' &&
        clientConfig !== null &&
        Array.isArray(clientConfig.roles)
      ) {
        clientConfig.roles.forEach((r) => roles.add(String(r)))
      }
    }
  }

  return Array.from(roles)
}

const authInterface = {
  validateAccess: function (to) {
    manager.getUser().then((user) => {
      if (!user || user.expired) {
        if (to.name !== 'Login') {
          sessionStorage.setItem('next', to.name)
          sessionStorage.setItem('nextParams', JSON.stringify(to.params))
        }
        manager.signinRedirect()
      }
    })
  },
  oauthLoginCallback: function () {
    return manager.signinRedirectCallback().then(() => {
      eventBusEmit('userSignedIn')
    })
  },
  clear: function () {
    manager.clearStaleState()
  },
  getAccessToken: function () {
    return manager.getUser().then((user) => {
      if (!user) {
        return null
      }
      return user.access_token
    })
  },
  getUserInfo: function () {
    return manager.getUser().then((user) => {
      if (!user || user.expired) {
        return null
      }
      const userInfo = JSON.parse(
        Buffer.from(user.access_token.split('.')[1], 'base64').toString()
      )
      userInfo.roles = extractAndFlattenRoles(userInfo)
      return userInfo
    })
  },
  oauthLogout: async function () {
    await manager.removeUser()
    await manager.clearStaleState()
    return manager.signoutRedirect()
  },
}

export default {
  install: (app, options) => {
    manager = new UserManager({
      metadataUrl: options.config.OAUTH_METADATA_URL,
      authority: 'studybuilder-frontend',
      client_id: options.config.OAUTH_UI_APP_ID,
      redirect_uri: location.origin + '/oauth-callback',
      response_type: 'code',
      response_mode: 'fragment',
      post_logout_redirect_uri: location.origin,
      userStore: new WebStorageStateStore({ store: new InMemoryWebStorage() }),
      scope: `openid profile email api://${options.config.OAUTH_API_APP_ID}/API.call`,
    })
    app.config.globalProperties.$auth = authInterface
    app.config.globalProperties.$roles = roles
    app.provide('roles', roles)
  },
}

export const auth = authInterface
