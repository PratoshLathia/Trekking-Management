<template>
    <Navbar />

    <main class="container py-4">
        <h1 class="mb-4">Manage Treks</h1>

        <search class="mb-3 d-block">
            <label for="trek-search" class="form-label">Search treks by name or ID</label>
            <input id="trek-search" v-model="searchTerm" type="text" class="form-control search-input">
        </search>

        <div v-if="fetchTreksMessage" role="alert" class="alert alert-danger">{{ fetchTreksMessage }}</div>
        <div v-else-if="deleteMessage" role="alert" class="alert alert-danger">{{ deleteMessage }}</div>
        
        <div v-else-if="filteredTreks.length > 0" class="table-responsive">
            <table class="table table-striped table-hover align-middle">
                <caption>All treks</caption>

                <thead>
                    <tr>
                        <th scope="col">ID</th>
                        <th scope="col">Name</th>
                        <th scope="col">Location</th>
                        <th scope="col">Duration</th>
                        <th scope="col">Difficulty</th>
                        <th scope="col">Slots</th>
                        <th scope="col">Status</th>
                        <th scope="col">Stage</th>
                        <th scope="col">Staff</th>
                        <th scope="col">Start Date</th>
                        <th scope="col">End Date</th>
                        <th scope="col">Action</th>
                    </tr>
                </thead>

                <tbody>
                    <template v-for="trek in filteredTreks" :key="trek.id">

                        <tr v-if="editingTrekId !== trek.id">
                            <td>{{ trek.id }}</td>
                            <td>{{ trek.name }}</td>
                            <td>{{ trek.location }}</td>
                            <td>{{ trek.duration }}</td>
                            <td>{{ trek.difficulty }}</td>
                            <td>{{ trek.slots }}</td>
                            <td>
                                <span class="badge" :class="trek.status === 'Active' ? 'badge-brand-active' : 'badge-brand-inactive'">
                                    {{ trek.status }}
                                </span>
                            </td>
                            <td>{{ trek.stage }}</td>
                            <td>{{ trek.staffName ? trek.staffName : "Not Assigned" }}</td>
                            <td>{{ trek.startDate }}</td>
                            <td>{{ trek.endDate }}</td>
                            <td class="d-flex gap-1 flex-wrap">
                                <button type="button" class="btn btn-sm btn-outline-secondary" @click="toggleStatus(trek)">
                                    {{ trek.status === "Active" ? "Close" : "Activate" }}
                                </button>
                                <button type="button" class="btn btn-sm btn-outline-secondary" @click="startEdit(trek)">Edit</button>
                                <button type="button" class="btn btn-sm btn-outline-danger" @click="deleteTrek(trek.id)">Delete</button>
                            </td>
                        </tr>

                        <tr v-else>
                            <td>{{ trek.id }}</td>
                            <td>
                                <input v-model="editForm.name" aria-label="Trek name" class="form-control form-control-sm">
                            </td>
                            <td>
                                <input v-model="editForm.location" aria-label="Trek location" class="form-control form-control-sm">
                            </td>
                            <td>
                                <input v-model="editForm.duration" aria-label="Trek duration" class="form-control form-control-sm">
                            </td>
                            <td>
                                <select v-model="editForm.difficulty" aria-label="Trek difficulty" class="form-select form-select-sm">
                                    <option value="Easy">Easy</option>
                                    <option value="Moderate">Moderate</option>
                                    <option value="Difficult">Difficult</option>
                                </select>
                            </td>
                            
                            <td>
                                <div class="input-group input-group-sm slots-input">
                                    <label :for="`slots-${trek.id}`" class="visually-hidden">Slots</label>
                                    <input :id="`slots-${trek.id}`" v-model.number="trek.slots" type="number" class="form-control">
                                    <button type="button" class="btn btn-outline-secondary" @click="toggleSlots(trek)">Save</button>
                                </div>
                            </td>

                            <td>
                                <span class="badge mb-1" :class="trek.status === 'Active' ? 'badge-brand-active' : 'badge-brand-inactive'">
                                    {{ trek.status }}
                                </span>
                                <button type="button" class="btn btn-outline-secondary btn-sm d-block" @click="toggleStatus(trek)">
                                        {{ trek.status === "Active" ? "Close" : "Activate" }}
                                </button>
                            </td>

                            <td>
                                <label :for="`stage-${trek.id}`" class="visually-hidden">Stage</label>
                                <select :id="`stage-${trek.id}`" v-model="trek.stage" class="form-select form-select-sm" @change="toggleStage(trek)">
                                    <option value="Upcoming">Upcoming</option>
                                    <option value="Started">Started</option>
                                    <option value="Ongoing">Ongoing</option>
                                    <option value="Completed">Completed</option>
                                </select>
                            </td>

                            <td>
                                <select v-model="editForm.staffId" aria-label="Assigned staff" class="form-select form-select-sm">
                                    <option v-for="staffMember in allStaff" :key="staffMember.id" :value="staffMember.id">
                                        {{ staffMember.username }}
                                    </option>
                                </select>
                            </td>

                            <td>
                                <input v-model="editForm.startDate" type="date" aria-label="Trek start date" class="form-control form-control-sm">
                            </td>
                            <td>
                                <input v-model="editForm.endDate" type="date" aria-label="Trek end date" class="form-control form-control-sm">
                            </td>
                            <td class="d-flex gap-1 flex-wrap">
                                <button type="button" class="btn btn-sm btn-brand-gold" @click="saveEdit(trek)">Save</button>
                                <button type="button" class="btn btn-sm btn-outline-secondary" @click="cancelEdit">Cancel</button>
                            </td>
                        </tr>

                    </template>
                </tbody>

            </table>
        </div>

        <p v-else>No treks match your search.</p>
        <p v-if="statusMessage" role="alert" class="alert alert-danger">{{ statusMessage }}</p>
        <p v-if="editMessage" role="alert" class="alert alert-danger">{{ editMessage }}</p>
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
            fetchTreksMessage: null,
            allTreks: [],
            allStaff: [],
            statusMessage: null,
            slotsMessage: null,
            stageMessage: null,
            deleteMessage: null,
            searchTerm: "",

            editingTrekId: null,
            editForm: { 
                name: "", 
                location: "", 
                duration: "", 
                difficulty: "",
                startDate: "",
                endDate: "",
                staffId: null 
            },
            editMessage: null
        };
    },

    computed: {
        filteredTreks() {
            const term = this.searchTerm.trim().toLowerCase();
            if (!term) return this.allTreks;

            return this.allTreks.filter(trek =>
                trek.name.toLowerCase().includes(term) ||
                String(trek.id) === term
            );
        }
    },

    mounted() {
        this.fetchTreks();
        this.fetchStaff();
    },

    methods: {
        async fetchTreks() {
            try {
                const response = await apiFetch("/trek/all");
                const data = await response.json();

                if (response.ok) {
                    this.allTreks = data.treks.map(trek => ({
                        id: trek.id,
                        name: trek.name,
                        location: trek.location,
                        duration: trek.duration,
                        difficulty: trek.difficulty,
                        slots: trek.slots,
                        staffId: trek.staff_id,
                        staffName: trek.staff_name,
                        startDate: trek.start_date,
                        endDate: trek.end_date,
                        stage: trek.stage,
                        status: trek.status
                    }));
                    this.fetchTreksMessage = null;
                } else {
                    this.fetchTreksMessage = data.info || "Failed to fetch treks";
                    console.error("Failed to fetch treks:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching treks:", error);
            }
        },

        async fetchStaff() {
            try {
                const response = await apiFetch("/staff/all");
                const data = await response.json();

                if (response.ok) {
                    this.allStaff = data.staff;
                } else {
                    console.error("Failed to fetch staff:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching staff:", error);
            }
        },

        async toggleStatus(trek) {
            const newStatus = trek.status === "Active" ? "Closed" : "Active";

            try {
                const response = await apiFetch(`/trek/${trek.id}/status`, {
                    method: "POST",
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await response.json();

                if (response.ok) {
                    trek.status = newStatus;
                    this.statusMessage = null;
                } else {
                    this.statusMessage = data.status_info || "Failed to change status";
                    console.error(`Failed to change status for Trek ID ${trek.id}:`, response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error(`Error changing status for Trek ID ${trek.id}:`, error);
            }
        },

        async toggleSlots(trek) {
            try {
                const response = await apiFetch(`/trek/${trek.id}/slots`, {
                    method: "POST",
                    body: JSON.stringify({ slots: trek.slots })
                });
                const data = await response.json();

                if (response.ok) {
                    this.slotsMessage = null;
                } else {
                    this.slotsMessage = data.slots_info || "Failed to change slots";
                    console.error(`Failed to change slots for Trek ID ${trek.id}:`, response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error(`Error changing slots for Trek ID ${trek.id}:`, error);
            }
        },

        async toggleStage(trek) {
            try {
                const response = await apiFetch(`/trek/${trek.id}/stage`, {
                    method: "POST",
                    body: JSON.stringify({ stage: trek.stage })
                });
                const data = await response.json();

                if (response.ok) {
                    this.stageMessage = null;
                    await this.fetchTreks();
                } else {
                    this.stageMessage = data.stage_info || "Failed to change stage";
                    console.error(`Failed to change stage for Trek ID ${trek.id}:`, response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error(`Error changing stage for Trek ID ${trek.id}:`, error);
            }
        },

        startEdit(trek) {
            this.editingTrekId = trek.id;
            this.editForm = {
                name: trek.name,
                location: trek.location,
                duration: trek.duration,
                difficulty: trek.difficulty,
                startDate: trek.startDate || "",
                endDate: trek.endDate || "",
                staffId: trek.staffId
            };
            this.editMessage = null;
        },

        cancelEdit() {
            this.editingTrekId = null;
        },

        async saveEdit(trek) {
            try {
                const response = await apiFetch(`/trek/${trek.id}/update`, {
                    method: "POST",
                    body: JSON.stringify({
                        name: this.editForm.name,
                        location: this.editForm.location,
                        duration: this.editForm.duration,
                        difficulty: this.editForm.difficulty,
                        start_date: this.editForm.startDate || null,
                        end_date: this.editForm.endDate || null
                    })
                });
                const data = await response.json();

                if (!response.ok) {
                    this.editMessage = data.info || "Failed to update trek";
                    console.error(`Failed to update Trek ID ${trek.id}:`, response.statusText, data);
                    return;
                }

                const assignResponse = await apiFetch(`/trek/${trek.id}/assign_staff`, {
                    method: "POST",
                    body: JSON.stringify({ staff_id: this.editForm.staffId })
                });
                const assignData = await assignResponse.json();

                if (!assignResponse.ok) {
                    this.editMessage = assignData.assign_info || "Trek updated, but staff reassignment failed";
                    console.error(`Failed to reassign staff for Trek ID ${trek.id}:`, assignResponse.statusText, assignData);
                    return;
                }
                this.editingTrekId = null;
                this.editMessage = null;
                await this.fetchTreks();

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error(`Error updating Trek ID ${trek.id}:`, error);
            }
        },

        async deleteTrek(trekId) {
            try {
                const response = await apiFetch(`/trek/${trekId}`, {
                    method: "DELETE"
                });
                const data = await response.json();

                if (response.ok) {
                    this.deleteMessage = null;
                    this.fetchTreks();
                } else {
                    this.deleteMessage = data.delete_info || "Failed to delete trek";
                    console.error(`Failed to delete trek with ID ${trekId}:`, response.statusText, data);
                }
            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error(`Error deleting trek with ID ${trekId}:`, error);
            }
        }
    }
};
</script>

<style scoped>
.search-input {
    max-width: 320px;
}
</style>
