<template>
  <svg-icon 
    type="mdi" 
    :path="iconPath" 
    :size="size" 
    :color="color" 
    :aria-hidden="ariaLabel ? undefined : 'true'"
    :aria-label="ariaLabel"
    :role="ariaLabel ? 'img' : undefined"
  ></svg-icon>
</template>

<script>
import SvgIcon from '@jamescoyle/vue-icon';
import * as mdiIcons from '@mdi/js'; // This imports ALL icons

export default {
  components: {
    SvgIcon
  },
  props: {
    icon: {
      type: String,
      required: true
    },
    size: {
      type: Number,
      default: 30
    },
    color: {
      type: String,
      default: '#719BDD'
    },
    ariaLabel: {
      type: String,
      default: undefined
    }
  },
  computed: {
    iconPath() {
      // This dynamically resolves ANY icon name
      const camelCase = this.icon
        .split('-')
        .map((word, index) => 
          index === 0 ? word : word.charAt(0).toUpperCase() + word.slice(1)
        )
        .join('');
      
      return mdiIcons[camelCase] || mdiIcons.mdiHelp;
    }
  }
}
</script>
