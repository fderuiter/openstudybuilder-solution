declare module '*.vue' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

import 'axios'
declare module 'axios' {
  export interface AxiosRequestConfig {
    ignoreErrors?: boolean;
  }
}

declare global {
  interface ImportMeta {
    readonly env: Record<string, any>;
    readonly glob: (pattern: string, options?: any) => Record<string, () => Promise<any>>;
  }
}

declare module '@/plugins/auth' {
  export const auth: any;
}
declare module '@/plugins/notificationHub' {
  export const notificationHub: any;
}
declare module '@/main' {
  export const useGlobalConfig: () => any;
}
declare module '@/stores/studies-general' {
  export const useStudiesGeneralStore: () => any;
}
declare module '@/composables/errorHandler' {
  export const useErrorHandler: (error: any) => any;
}
declare module '@/constants/study' {
  const content: any;
  export default content;
}
