<script lang="ts" setup>
import {computed, ref} from "vue";
import {useStudentStore, useFilterStore} from "../dataStore";

defineProps<{
  isDownloading: boolean,
  studentNameQuery: string,
}>();

const emit = defineEmits(['update:studentNameQuery']);

const studentStore = useStudentStore();
const filterStore = useFilterStore();
const globalOnly = ref(false);

const schoolFilteredStudents = computed(() => {
  return studentStore.studentList.filter(student => {
    const filterRegion = !globalOnly || student.isGlobal;
    return filterRegion || filterStore.schoolFilter.includes(student.schoolName)
  });
})

const filteredClubs = computed(() => {
  const clubSet: Set<string> = new Set();
  schoolFilteredStudents.value.map((student) => {
    if (student.clubName !== "") clubSet.add(student.clubName);
  });

  const clubList: string[] = [...clubSet];
  clubList.sort((a, b) => a.localeCompare(b));

  return clubList;
});

const toggleAccordion = (event: Event) => {
  const button = event.currentTarget as HTMLElement;
  const item = button.parentElement as HTMLElement;
  const indicator = button.querySelector('.accordion-indicator');

  if (item.classList.contains("active")) {
    item.classList.remove("active");
    if (indicator) indicator.innerHTML = "+";
  } else {
    item.classList.add("active");
    if (indicator) indicator.innerHTML = "-";
  }
}

const schoolLogoPath = (schoolName: string) => new URL(`../assets/schools/${schoolName}.webp`, import.meta.url).href

const updateStudentNameQuery = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit('update:studentNameQuery', target.value);
}
</script>

<template>
  <div class="selector">
    <div class="student-name-selector">
      <label>Student Name :</label>
      <input
          :disabled="isDownloading"
          :value="studentNameQuery"
          placeholder="Azusa (Swimsuit)"
          type="text"
          @input="updateStudentNameQuery"
      >
    </div>
    <fieldset>
      <div class="school-selector-list">
        <img
            v-for="school in studentStore.schoolList"
            :key="school"
            :alt="school"
            :class="{selected:filterStore.schoolFilter.includes(school), disabled: isDownloading}"
            :src="schoolLogoPath(school)"
            :title="school"
            class="school-selector-item"
            @click="filterStore.toggleSchoolFilter(school)"
        >
        <div class="is-global-selector">
          <button :disabled="isDownloading" class="is-global" :class="{selected:filterStore.regionFilter}" @click="filterStore.toggleRegionFilter">
            Global<br>Only
          </button>
        </div>
      </div>
    </fieldset>
    <div class="accordion-selector">
      <div class="accordion-selector-item">
        <button class="accordion-selector-header" @click="toggleAccordion($event)">
          Select Type
          <span class="accordion-indicator">+</span>
        </button>
        <div class="accordion-selector-content">
          <div class="accordion-selector-inner">
          <div class="type-selector-container">
            <div class="type-selector-list">
              <button
                  v-for="attackType in studentStore.attackList"
                  :class="[attackType, {deselected: !filterStore.attackFilter.includes(attackType)}]"
                  :disabled="isDownloading"
                  class="type-selector-item"
                  @click="filterStore.toggleAttackFilter(attackType)">
                {{ attackType }}
              </button>
            </div>
            <div class="type-selector-list">
              <button
                  v-for="defenceType in studentStore.defenceList"
                  :class="[defenceType, {deselected: !filterStore.defenceFilter.includes(defenceType)}]"
                  :disabled="isDownloading"
                  class="type-selector-item"
                  @click="filterStore.toggleDefenceFilter(defenceType)">
                {{ defenceType }}
              </button>
            </div>
          </div>
          </div>
        </div>

      </div>
      <div class="accordion-selector-item">
        <button class="accordion-selector-header" @click="toggleAccordion($event)">
          Select Club
          <span class="accordion-indicator">+</span>
        </button>
        <div class="accordion-selector-content">
          <div class="accordion-selector-inner">
          <div class="club-selector-list">
            <button
                v-for="club in filteredClubs"
                :key="club"
                :class="{ selected: filterStore.clubFilter.includes(club) }"
                :disabled="isDownloading"
                class="club-button"
                @click="filterStore.toggleClubFilter(club)"
            >
              {{ club }}
            </button>
          </div>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.selector {
  justify-self: center;
  margin-top: -1em;
}

.student-name-selector {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1em;
}

.student-name-selector label {
  font-weight: bold;
  font-size: large;
}

.student-name-selector input {
  width: 50%;
  font-size: large;
}

.school-selector-list {
  display: grid;
  grid-template-columns: auto auto auto auto auto auto auto;
  justify-items: center;
  align-items: center;
}

.school-selector-item {
  width: 3em;
  filter: grayscale(1) brightness(2);
  transition: filter 0.3s ease;
}

.school-selector-item.selected {
  filter: grayscale(0) brightness(1);
}

.school-selector-item:hover {
  cursor: pointer;
  outline: 3px solid #007bff;
}

.school-selector-item.disabled {
  pointer-events: none;
  opacity: 0.5;
}

.is-global {
  background-color: #fcfcfc;
  border-radius: 0.5em;
  border-width: 1px;
  transition: all 0.1s ease;
}

.is-global:hover {
  transform: scale(1.1);
}

.is-global.selected {
  background-color: #007bff;
  color: #f0f0f0;
}

.accordion-selector {
  margin-top: 1em;
}

.accordion-selector-item {
  border: 1px solid #ccc;
  margin-bottom: 0.5em;
  border-radius: 5px;
}

.accordion-selector-header {
  width: 100%;
  padding: 0.7em;
  text-align: left;
  font-weight: bold;
  cursor: pointer;
  font-size: large;
  transition: background-color 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.accordion-selector-header:hover {
  background-color: #e0e0e0;
}

.accordion-selector-content {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.3s ease-in-out;
}

.accordion-selector-item.active .accordion-selector-content {
  grid-template-rows: 1fr;
}

.accordion-selector-inner {
  overflow: hidden;
}

.type-selector-container {
  padding: 1em;
}

.accordion-indicator {
  font-size: 1.5em;
  font-weight: bold;
}

.type-selector-list {
  display: flex;
  justify-content: space-evenly;
  padding: 0.5em;
}

.type-selector-item {
  width: 7em;
  height: 3em;
  color: #fcfcfc;
  font-weight: bold;
  transition: background-color 0.2s ease;
}

.explosive {
  background-color: #920008;
}

.penetration {
  background-color: #bc6f02;
}

.mystic {
  background-color: #1f6095;
}

.sonic {
  background-color: #9a45a8;
}

.light {
  background-color: #920008;
}

.heavy {
  background-color: #bc6f02;
}

.special {
  background-color: #1f6095;
}

.elastic {
  background-color: #9a45a8;
}

.type-selector-item.deselected {
  background-color: #f0f0f0;
  color: black;
}

.club-selector-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5em;
  justify-content: center;
  padding: 1em;
}

.club-button {
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 0.5em 1em;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
}

.club-button:hover {
  background-color: #e0e0e0;
}

.club-button.selected {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

@media only screen and (max-width: 992px) {
  .selector {
    width: 35em;
  }

  .school-selector-list {
    column-gap: 1em;
    row-gap: 0.5em;
  }
}

@media only screen and (min-width: 992px) {
  .selector {
    width: 40em;
  }

  .school-selector-list {
    column-gap: 2em;
    row-gap: 0.7em;
  }
}
</style>