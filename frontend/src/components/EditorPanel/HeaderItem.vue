<template>
    <div :class=" 'editor-header-item' + ' ' + (focus ? 'background-focus' : '') ">
      <p class="editor-header-item-title" @click="emit('toFocus')">
        {{ title }}
      </p>
      <div class="editor-header-item-operation" @click="emit('close')">
        <div v-if="modified" :class=" 'editor-header-item-save' + ' ' + ( focus ? 'save-focus' : '')">
          <!-- modified -->
        </div>
        <div v-else :class=" 'editor-header-item-close' + ' ' + ( focus ? 'close-focus' : '')">
          <!-- not modified -->
        </div>
      </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, defineProps, defineEmits } from 'vue'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  title: String,
  focus: Boolean,
  modified: Boolean
})

const closeOperatorSize = ref('15px')
const saveOperatorSize = ref('10px')

// on focus, set by parent node
// watch(() => props.focus, (newFocus) => {
//   if (newFocus) {
//     console.log('focus')
//   } else {
//     console.log('stop focus')
//   }
// })

const emit = defineEmits(['toFocus', 'close'])

</script>

<style scoped>
.editor-header-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #66b1ff;
  width: min-content;
  min-width: 50px;
  padding: 5px 5px;
  color: #eeeeee;
  user-select: none;
}

/* focus 之后的背景色  ?  还有前面的字*/
.background-focus {
  background-color:   #3375b9;
  color: #FFFFFF !important;
}

.save-focus {
  background-color: #fff !important;
}

/* focus 之后的前景色 */
.close-foucs::before, .close-foucs::after {
  background-color: #fff !important;
}

p {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  text-align: left;
}
.editor-header-item-close {
    position: relative;
    border-radius: v-bind(closeOperatorSize);
    width: v-bind(closeOperatorSize);
    height: v-bind(closeOperatorSize);
    margin: 2px;
}

.editor-header-item-close:hover {
    position: relative;
    width: v-bind(closeOperatorSize);
    height: v-bind(closeOperatorSize);
    background-color: #555555;
    border-radius: 3px;
}

/* 关闭叉子 */
.editor-header-item-close::before,
.editor-header-item-close::after {
    position: absolute;
    content: ' ';
    background-color: #cccccc;
    width: 1px;
    height: v-bind(closeOperatorSize);
}
.editor-header-item-close::before {
    transform: rotate(45deg);
}
.editor-header-item-close::after {
    transform: rotate(-45deg);
}

/* 半透明的圆点 */
.editor-header-item-save {
  position: relative;
  border-radius: 50%;
  width: v-bind(saveOperatorSize);
  height: v-bind(saveOperatorSize);
  margin: 2px;
  background-color: #888;
}
</style>
