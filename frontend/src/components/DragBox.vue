<template>
  <div ref="dragBox" style="display:flex; width: 100%; height:100%">
    <slot></slot>
  </div>
</template>

<script lang="ts">

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
      i.addEventListener('mousedown', this.onMouseDown)
    }
  }

  setDragItemFlex () {
    const dragBox = this.$refs.dragBox
    for (const node of dragBox.children) {
      if (!node.style.width) {
        node.style.width = 1
      }
    }
  }

  onMouseDown (e) {
    this.resizeBox = e.target
    this.currentBox = this.resizeBox.parentNode
    this.rightBox = this.getNextElement(this.currentBox)
    if (!this.rightBox) return
    this.curLen = this.currentBox.clientWidth
    this.otherBoxWidth = this.$refs.dragBox.clientWidth - this.curLen - this.rightBox.clientWidth
    this.resizeBox.style.background = '#818181'
    this.startX = e.clientX
    document.addEventListener('mousemove', this.onMouseMove)
    document.addEventListener('mouseup', this.onMouseUp)
  }

  onMouseMove (e) {
    const endX = e.clientX
    const moveLen = endX - this.startX
    const curBoxLen = this.curLen + moveLen
    const rightBoxLen = this.$refs.dragBox.clientWidth - curBoxLen - this.otherBoxWidth
    // if (curBoxLen <= 200 || rightBoxLen <= 200) return
    this.currentBox.style.width = curBoxLen + 'px'
    this.resizeBox.style.left = curBoxLen
    this.rightBox.style.width = rightBoxLen + 'px'
  }

  onMouseUp (e) {
    this.resizeBox.style.background = '#bbbbbb'
    document.removeEventListener('mousedown', this.onMouseDown)
    document.removeEventListener('mousemove', this.onMouseMove)
  }

  getNextElement (element) {
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
