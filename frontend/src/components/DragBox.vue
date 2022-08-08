<template>
  <div ref="dragBox" style="display:flex; width: 100%; height:100%">
    <slot></slot>
  </div>
</template>

<script lang="ts">

import { WidthProperty } from 'csstype'
import { Vue } from 'vue-class-component'

export default class DragBox extends Vue {
  startX = 0 as number
  curLen = 0 as number
  otherBoxWidth = 0 as number
  resizeBox !: HTMLDivElement
  currentBox !: HTMLDivElement
  rightBox ?: HTMLDivElement

  mounted () {
    this.setDragItemFlex()
    this.dragControlerDiv()
  }

  dragControlerDiv () {
    const resize = document.getElementsByClassName('resize')
    for (const i of resize) {
      i.addEventListener('mousedown', this.onMouseDown as EventListener)
    }
  }

  setDragItemFlex () {
    const dragBox = this.$refs.dragBox as HTMLDivElement
    // for (const node of dragBox.children ) {
    //   if (!(node as HTMLDivElement).style.width) {
    //     (node as HTMLDivElement).style.width = 1
    //   }
    // }
  }

  onMouseDown (e : MouseEvent) {
    this.resizeBox = e.target as HTMLDivElement & ChildNode
    this.currentBox = this.resizeBox.parentNode as HTMLDivElement
    this.rightBox = (this.getNextElement(this.currentBox) as HTMLDivElement)
    if (!this.rightBox) return
    this.curLen = this.currentBox.clientWidth
    this.otherBoxWidth = (this.$refs.dragBox as HTMLDivElement).clientWidth - this.curLen - this.rightBox.clientWidth
    this.resizeBox.style.background = '#818181'
    this.startX = e.clientX
    document.addEventListener('mousemove', this.onMouseMove)
    document.addEventListener('mouseup', this.onMouseUp)
  }

  onMouseMove (e : MouseEvent) {
    const endX = e.clientX
    const moveLen = endX - this.startX
    const curBoxLen = this.curLen + moveLen
    const rightBoxLen = (this.$refs.dragBox as HTMLDivElement).clientWidth - curBoxLen - this.otherBoxWidth
    // if (curBoxLen <= 200 || rightBoxLen <= 200) return
    this.currentBox.style.width = curBoxLen + 'px'
    this.resizeBox.style.left = curBoxLen + 'px'
    if (this.rightBox) {
      this.rightBox.style.width = rightBoxLen + 'px'
    }
  }

  onMouseUp (e : MouseEvent) {
    this.resizeBox.style.background = '#bbbbbb'
    document.removeEventListener('mousedown', this.onMouseDown)
    document.removeEventListener('mousemove', this.onMouseMove)
  }

  getNextElement (element : HTMLElement) {
    if (element.nextElementSibling) {
      return element.nextElementSibling
    } else {
      let next = element.nextSibling
      while (next && next.nodeType !== 1) {
        next = next.nextSibling
      }
      return next
    }
  }
}

</script>

<style scoped>
</style>
