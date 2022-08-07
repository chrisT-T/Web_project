<template>
  <div>
    a
    <variable-table :data='dat' />
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component'
// import webTerminal from '@/components/webTerminal.vue'
import VariableTable from '@/components/VariableTable.vue'

@Options({
  components: {
    VariableTable
  }
})
export default class terminalView extends Vue {
  dat = [
    {
      id: '1',
      label: '标签1',
      isPenultimate: true,
      children: [
        {
          id: '1',
          label: '标签1-1'
        },
        {
          id: '1-2',
          label: '标签1-2'
        }
      ]
    },
    {
      id: '2',
      label: '标签2',
      isPenultimate: true,
      children: [
        {
          id: '2-1',
          label: '标签2-1',
          isPenultimate: true,
          children: [
            {
              id: '2-1-1',
              label: '标签2-1-1'
            },
            {
              id: '2-1-2',
              label: '标签2-1-2'
            }
          ]
        },
        {
          id: '2-2',
          label: '标签2-2',
          isPenultimate: true,
          children: [
            {
              id: '2-2-1',
              label: '标签2-2-1'
            },
            {
              id: '2-2-2',
              label: '标签2-2-2'
            }
          ]
        }
      ]
    }
  ]
}
</script>
