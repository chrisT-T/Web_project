<template>
  <div ref="dragBox" style="display:flex; width: 100%; height:100%">
      <slot></slot>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'

let startX = 0 as number
let curLen = 0 as number
let otherBoxWidth = 0 as number
let resizeBox !: HTMLDivElement
let currentBox !: HTMLDivElement
let rightBox : HTMLDivElement
const dragBox = ref(null) as unknown as HTMLDivElement

onMounted(() => {
  dragControlerDiv()
})

function dragControlerDiv () {
  const resize = document.getElementsByClassName('resize')
  for (const i of resize) {
    i.addEventListener('mousedown', onMouseDown as EventListener)
  }
}

function onMouseDown (e : MouseEvent) {
  resizeBox = e.target as HTMLDivElement & ChildNode
  currentBox = resizeBox.parentNode as HTMLDivElement
  rightBox = (getNextElement(currentBox) as HTMLDivElement)
  if (!rightBox) return
  curLen = currentBox.clientWidth
  otherBoxWidth = (dragBox as HTMLDivElement).clientWidth - curLen - rightBox.clientWidth
  resizeBox.style.background = '#818181'
  startX = e.clientX
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

function onMouseMove (e : MouseEvent) {
  const endX = e.clientX
  const moveLen = endX - startX
  const curBoxLen = curLen + moveLen
  const rightBoxLen = (dragBox as HTMLDivElement).clientWidth - curBoxLen - otherBoxWidth
  // if (curBoxLen <= 200 || rightBoxLen <= 200) return
  currentBox.style.width = curBoxLen + 'px'
  resizeBox.style.left = curBoxLen + 'px'
  if (rightBox) {
    rightBox.style.width = rightBoxLen + 'px'
  }
}

function onMouseUp (e : MouseEvent) {
  resizeBox.style.background = '#bbbbbb'
  document.removeEventListener('mousedown', onMouseDown)
  document.removeEventListener('mousemove', onMouseMove)
}

function getNextElement (element : HTMLElement) {
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

</script>

<style scoped>
</style>
