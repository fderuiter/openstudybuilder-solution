import { inject } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useAccessGuard() {
  const authStore = useAuthStore()

  function checkPermission(permission) {
    const $config = inject('$config')
    if ($config.OAUTH_ENABLED && $config.OAUTH_RBAC_ENABLED) {
      const roles = authStore.userInfo?.roles || []
      return Array.isArray(roles) && roles.includes(permission)
    }
    return true
  }

  return {
    userInfo: authStore.userInfo,
    checkPermission,
  }
}
