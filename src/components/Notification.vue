<script lang="ts" setup>
import {ref, onMounted} from 'vue';

const props = defineProps<{
  message: string;
  duration?: number;
  type: string;
}>();

const emit = defineEmits(['close']);

const visible = ref(false);

onMounted(() => {
  visible.value = true;
  if (props.duration) {
    setTimeout(() => {
      close();
    }, props.duration);
  }
});

const close = () => {
  visible.value = false;
  setTimeout(() => {
    emit('close');
  }, 300); // wait for fade out animation
};
</script>

<template>
  <div v-if="visible" :class="type" class="notification" @click="close">
    <p>{{ message }}</p>
  </div>
</template>

<style scoped>
.notification {
  background-color: #4caf50;
  color: white;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 5px;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.notification:hover {
  opacity: 0.8;
}

.notification.stderr {
  background-color: #f44336;
}
</style>