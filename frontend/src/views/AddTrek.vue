<template>
    <Navbar />

    <main class="container py-4 narrow-form">
        <h1 class="mb-4">Add Trek</h1>
        <form @submit.prevent="addTrek">
            <fieldset class="border-0 p-0">
                <legend class="visually-hidden">Trek details</legend>

                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input id="name" v-model="name" placeholder="Enter trek name" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label for="location" class="form-label">Location</label>
                    <input id="location" v-model="location" placeholder="Enter trek location" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label for="duration" class="form-label">Duration</label>
                    <input id="duration" v-model="duration" placeholder="Enter trek duration" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label for="difficulty" class="form-label">Difficulty</label>
                    <select id="difficulty" v-model="difficulty" class="form-select" required>
                        <option value="Easy">Easy</option>
                        <option value="Moderate">Moderate</option>
                        <option value="Difficult">Difficult</option>
                    </select>
                </div>

                <div class="mb-3">
                    <label for="slots" class="form-label">Slots available</label>
                    <input id="slots" v-model.number="slots" type="number" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label for="startDate" class="form-label">Start date</label>
                    <input id="startDate" v-model="startDate" type="date" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label for="endDate" class="form-label">End date</label>
                    <input id="endDate" v-model="endDate" type="date" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label for="staffId" class="form-label">Assigned staff</label>
                    <select id="staffId" v-model="staffId" class="form-select" required>
                        <option value="" hidden>Select a staff member</option>
                        <option v-for="staff in activeStaff" :key="staff.id" :value="staff.id">
                            {{ staff.username }}
                        </option>
                    </select>
                </div>
                
            </fieldset>

            <button type="submit" class="btn btn-brand-gold">Add Trek</button>
        </form>
        <p v-if="formMessage" role="alert" class="alert mt-3" :class="formSuccess ? 'alert-success' : 'alert-danger'">
            {{ formMessage }}
        </p>
    </main>
</template>

<script>
import Navbar from "../components/Navbar.vue";
import { apiFetch } from "../api.js";

export default {
    components: {
        Navbar
    },

    data() {
        return {
            formMessage: null,
            formSuccess: false,
            name: "",
            location: "",
            duration: "",
            difficulty: "",
            slots: "",
            startDate: "",
            endDate: "",
            staffId: "",
            allStaff: []
        };
    },

    mounted() {
        this.fetchStaff();
    },

    computed: {
        activeStaff() {
            return this.allStaff.filter(staff => staff.status === "Active");
        },
    },

    methods: {
        async fetchStaff() {
            try {
                const response = await apiFetch("/staff/all");
                const data = await response.json();

                if (response.ok) {
                    this.allStaff = data.staff;
                    this.formMessage = null;
                } else {
                    this.formSuccess = false;
                    this.formMessage = data.info || "Failed to fetch staff";
                    console.error("Failed to fetch staff:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching staff:", error);
            }
        },

        async addTrek() {
            try {
                const response = await apiFetch("/trek/add", {
                    method: "POST",
                    body: JSON.stringify({
                        name: this.name,
                        location: this.location,
                        duration: this.duration,
                        difficulty: this.difficulty,
                        slots: this.slots,
                        start_date: this.startDate || null,
                        end_date: this.endDate || null,
                        staff_id: this.staffId
                    })
                });
                const data = await response.json();

                this.formSuccess = response.ok;
                if (response.ok) {
                    this.formMessage = data.info;
                } else {
                    this.formMessage = data.info || "Failed to add trek";
                    console.error("Failed to add trek:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error adding trek:", error);
            }
        }
    }
};
</script>

<style scoped>
.narrow-form {
    margin: 0 auto;
    max-width: 560px;
}
</style>
