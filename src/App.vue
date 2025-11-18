<script lang="ts" setup>
import {onMounted, onUnmounted, ref, computed} from "vue";
import {useStudentStore, useFilterStore} from "./dataStore";
import {listen, UnlistenFn} from "@tauri-apps/api/event";
import {invoke} from "@tauri-apps/api/core";
import logo from "./assets/Logo.png";
import Notification from "./components/Notification.vue";
import StudentProfile from "./components/StudentProfile.vue";
import Selector from "./components/Selector.vue";

interface Notification {
  id: number;
  message: string;
  type: 'stdout' | 'stderr';
}

const studentStore = useStudentStore();
const filterStore = useFilterStore();

const isLoaded = ref(false);
const isDownloading = ref(false);
const studentListErrorMsg = ref<string | null>(null);
const notifications = ref<Notification[]>([]);
let notificationId = 0;

const studentNameQuery = ref<string>("");

let unlistenStdout: UnlistenFn | undefined;
let unlistenStderr: UnlistenFn | undefined;

const addNotification = (message: string, type: 'stdout' | 'stderr') => {
  notifications.value.push({id: notificationId++, message, type});
};

const removeNotification = (id: number) => {
  notifications.value = notifications.value.filter(n => n.id !== id);
};

const schoolFilteredStudents = computed(() => {
  return studentStore.studentList.filter(student => {
    return filterStore.schoolFilter.includes(student.schoolName)
  });
})

const filteredStudents = computed(() => {
  return schoolFilteredStudents.value.filter(student => {
    const lowercaseName = student.name.toLocaleLowerCase();
    const lowercaseQuery = studentNameQuery.value.toLocaleLowerCase();
    const filterRegion = !filterStore.regionFilter || student.isGlobal;

    return lowercaseName.startsWith(lowercaseQuery) &&
    filterRegion &&
    filterStore.clubFilter.includes(student.clubName) &&
    filterStore.attackFilter.includes(student.attackType) &&
    filterStore.defenceFilter.includes(student.defenceType);
  });
});

const selectedStudents = ref<string[]>([]);

const toggleSelectStudent = (name: string): void => {
  if (isDownloading.value) return;
  if (selectedStudents.value.includes(name)) {
    selectedStudents.value = selectedStudents.value.filter(studentName => studentName != name);
  } else {
    selectedStudents.value.push(name);
  }
}

const toggleStudentList = (event: MouseEvent): void => {
  if (isDownloading.value) return;
  const span = event.currentTarget as HTMLElement;
  const accordion = span.closest('.accordion') as HTMLElement;
  const indicator = span.querySelector('.accordion-indicator');

  if (accordion.classList.contains("active")) {
    accordion.classList.remove("active");
    if (indicator) indicator.innerHTML = "+";
  } else {
    accordion.classList.add("active");
    if (indicator) indicator.innerHTML = "-";
  }
}

const downloadVoice = async () => {
  isDownloading.value = true;
  try {
    const result = await invoke("download_voices", {studentList: selectedStudents.value}) as string;

    if (result) {
      addNotification(result, 'stderr');
    } else {
      selectedStudents.value = [];
    }
  } finally {
    isDownloading.value = false;
  }
}

onMounted(async () => {
  try {
    unlistenStdout = await listen<string>("sidecar-stdout", (event) => {
      addNotification(event.payload, 'stdout');
    });
    unlistenStderr = await listen<string>("sidecar-stderr", (event) => {
      addNotification(event.payload, 'stderr');
    });

    await studentStore.fetchStudentList();
    filterStore.initFilter(studentStore.schoolList, studentStore.clubList);
  } catch (err) {
    if (typeof err === "string") {
      console.error("fetching student list failed:", err);
      studentListErrorMsg.value = err;
      addNotification(err, 'stderr');
    } else {
      studentListErrorMsg.value = "unknown error occurred";
      addNotification("unknown error occurred", 'stderr');
    }
  } finally {
    isLoaded.value = true;
  }
});

onUnmounted(() => {
  if (unlistenStdout) {
    unlistenStdout();
  }
  if (unlistenStderr) {
    unlistenStderr();
  }
});
</script>

<template>
  <div class="notification-container">
    <Notification
        v-for="notification in notifications"
        :key="notification.id"
        :duration="5000"
        :message="notification.message"
        :type="notification.type"
        @close="removeNotification(notification.id)"
    />
  </div>
  <main class="container">
    <img :src="logo" alt="Blue Archive Voice Downloader" class="title">
    <p v-if="!isLoaded" class="message">Loading Student List...</p>
    <p v-else-if="studentListErrorMsg" class="error message">오류: {{ studentListErrorMsg }}</p>
    <div v-else>
      <Selector
          :is-downloading="isDownloading"
          :student-name-query="studentNameQuery"
          @update:student-name-query="studentNameQuery = $event"
      />
      <div class="student-profile-list">
        <StudentProfile
            v-for="student in filteredStudents"
            :key="student.name"
            :is-selected="selectedStudents.includes(student.name)"
            :student="student"
            @toggle-select="toggleSelectStudent"
        />
      </div>
    </div>
  </main>
  <div :class="{disabled: isDownloading}" class="accordion active">
    <div class="list-header">
      <span @click="toggleStudentList($event)">Selected Students<span class="accordion-indicator">-</span></span>
    </div>
    <div class="list-content">
      <div class="list-content-inner">
        <span v-for="student in selectedStudents" class="selected-list-item">
          {{ student }}
        </span>
      </div>
    </div>
  </div>
  <button :disabled="isDownloading" class="download" @click="downloadVoice">DOWNLOAD</button>
</template>

<style>
:root {
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

.title {
  display: block;
  margin: auto;
}

.notification-container {
  position: fixed;
  top: 10px;
  right: 10px;
  z-index: 1000;
  width: 300px;
}

.message {
  justify-self: center;
}

.error {
  color: red;
}

.student-profile-list {
  display: grid;
  justify-content: center;
  justify-items: center;
  padding-top: 2em;
}

@media only screen and (max-width: 992px) {
  .title {
    width: 720px;
  }

  .student-profile-list {
    grid-template-columns: auto auto auto auto auto;
    gap: 1em;
  }
}

@media only screen and (min-width: 992px) {
  .title {
    width: 892px;
  }

  .student-profile-list {
    grid-template-columns: auto auto auto auto auto auto auto;
    gap: 1.5em;
  }
}

.accordion {
  position: fixed;
  top: 1.5em;
  left: 1.5em;
  z-index: 1;
  background-color: aliceblue;
  width: 10em;
  border-radius: 0.5em;
  border: 1px solid darkblue;
  padding-left: 0.5em;
  overflow: hidden;
  min-height: 2em;
  align-content: center;
}

.accordion.disabled {
  pointer-events: none;
  opacity: 0.5;
}

.list-header {
  cursor: pointer;
}

.list-header span {
  align-items: center;
  width: 100%;
  font-weight: bold;
}

.list-content {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.3s ease-in-out;
}

.accordion.active .list-content {
  grid-template-rows: 1fr;
}

.list-content-inner {
  overflow: auto;
  max-height: 10em;
  display: flex;
  flex-direction: column;
}

.accordion-indicator {
  font-weight: bold;
}

.selected-list-item {
  font-size: small;
  border-bottom: 1px solid darkblue;
}

.selected-list-item:last-child {
  border-bottom: none;

  .selector {
    justify-self: center;
    margin-top: -1em;
  }
}

.download {
  position: fixed;
  bottom: 2em;
  right: 2em;
  cursor: pointer;
  font-size: large;
  padding: 0.5em;
  box-shadow: 0 2px 6px #0c0c0c;
  background-color: #007bff;
  color: #f0f0f0;
  border: none;
  border-radius: 1em;
  transition: all 50ms ease;
  z-index: 1;
}

.download:hover {
  transform: scale(1.1);
}

.download:disabled {
  .student-name-selector {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1em;
  }

  cursor: not-allowed;
  opacity: 0.5;
}
</style>