<script setup lang="ts">
import { computed } from "vue";
import type { StudentData } from "../types/student";

const props = defineProps<{
  student: StudentData;
  isSelected: boolean;
}>();

const emit = defineEmits<{
  (e: "toggle-select", name: string): void;
}>();

const formatStudentName = (name: string): { mainName: string; tag: string } => {
  const match = name.match(/(.*)\s(\(.*\))/);
  if (match && match.length === 3) {
    return { mainName: match[1].trim(), tag: match[2].trim() };
  }
  return { mainName: name.trim(), tag: "" };
};

const studentName = computed(() => formatStudentName(props.student.name));

const toggleSelect = () => {
  emit("toggle-select", props.student.name);
};
</script>

<template>
  <div class="student-profile">
    <div class="image-container" :class="{ selected: isSelected }" @click="toggleSelect">
      <img
          :alt="student.name"
          :src="student.imageUrl"
          :title="student.name"
          loading="lazy"
      >
    </div>
    <span class="student-name">
      {{ studentName.mainName }}
    </span>
    <span v-if="studentName.tag" class="student-tag">
      {{ studentName.tag }}
    </span>
  </div>
</template>

<style scoped>
.student-profile {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.student-profile .image-container {
  position: relative;
  overflow: hidden;
  display: inline-block;
}

.student-profile .image-container::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #555;
  opacity: 0;
  transition: opacity 0.1s ease;
  pointer-events: none;
  border-radius: 0.2em;
}

.student-profile .selected::after {
  opacity: 0.7;
}

.student-profile .image-container:hover {
  cursor: pointer;
  outline: 3px solid #007bff;
  outline-offset: 3px;
}

.student-profile .image-container img {
  width: 7em;
  display: block;
}

.student-profile span.student-name {
  font-weight: bold;
  font-size: small;
}

.student-profile span.student-tag {
  font-size: x-small;
  font-weight: normal;
}
</style>
