import { defineStore } from 'pinia';
import { ref } from 'vue';
import { invoke } from "@tauri-apps/api/core";
import { StudentData } from './types/student';

export const useStudentStore = defineStore('students', () => {
    const studentList = ref<StudentData[]>([]);
    const schoolList = ref<string[]>([]);
    const clubList = ref<string[]>([]);
    const attackList = ["explosive","penetration","mystic","sonic"];
    const defenceList = ["light", "heavy", "special", "elastic"];
    const isLoaded = ref(false);

    async function fetchStudentList() {
        if (isLoaded.value) return;

        const result = await invoke("fetch_student_list") as StudentData[];
        studentList.value = result;

        const allSchoolList: string[] = result.reduce((acc, currentStudent) => {
            const value: string = currentStudent.schoolName;

            if (!acc.seen.has(value)) {
                acc.seen.add(value);
                acc.keys.push(value);
            }

            return acc;
        }, {seen: new Set<string>(), keys: [] as string[]}).keys;
        
        const allClubList: string[] = result.reduce((acc, currentStudent) => {
            const value: string = currentStudent.clubName;

            if (!acc.seen.has(value)) {
                acc.seen.add(value);
                acc.keys.push(value);
            }

            return acc;
        }, {seen: new Set<string>(), keys: [] as string[]}).keys;

        schoolList.value = allSchoolList;
        clubList.value = allClubList;

        isLoaded.value = true;
    }

    return {studentList, schoolList, clubList, attackList, defenceList, fetchStudentList};
});

export const useFilterStore = defineStore('filter', () => {
    const schoolFilter = ref<string[]>([]);
    const clubFilter = ref<string[]>([]);
    const attackFilter = ref<string[]>(["explosive", "penetration", "mystic", "sonic"]);
    const defenceFilter = ref<string[]>(["light", "heavy", "special", "elastic"]);
    const regionFilter =ref(false);

    const isLoaded = ref(false);

    function initFilter(allSchoolList: string[], allClubList: string[]) {
        if (isLoaded.value) return;

        schoolFilter.value = [...allSchoolList];
        clubFilter.value = [...allClubList];

        isLoaded.value = true
    }

    function toggleSchoolFilter(schoolName: string) {
        const index = schoolFilter.value.indexOf(schoolName);
        if (index > -1) {
            schoolFilter.value.splice(index, 1);
        } else {
            schoolFilter.value.push(schoolName);
        }
    }

    function toggleClubFilter(clubName: string) {
        const index = clubFilter.value.indexOf(clubName);
        if (index > -1) {
            clubFilter.value.splice(index, 1);
        } else {
            clubFilter.value.push(clubName);
        }
    }

    function toggleAttackFilter(attackType: string) {
        const index = attackFilter.value.indexOf(attackType);
        if (index > -1) {
            attackFilter.value.splice(index, 1);
        } else {
            attackFilter.value.push(attackType);
        }
    }

    function toggleDefenceFilter(defenceType: string) {
        const index = defenceFilter.value.indexOf(defenceType);
        if (index > -1) {
            defenceFilter.value.splice(index, 1);
        } else {
            defenceFilter.value.push(defenceType);
        }
    }

    function toggleRegionFilter() {
        regionFilter.value = !regionFilter.value;
    }

    return {
        schoolFilter, clubFilter, attackFilter, defenceFilter, regionFilter,
        toggleSchoolFilter, toggleClubFilter, toggleAttackFilter, toggleDefenceFilter, toggleRegionFilter,
        initFilter,
    };
})