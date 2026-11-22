<template>
    <Navbar />

    <main class="container py-4">
        <h1 class="mb-4">Manage Staff</h1>

        <search class="mb-3 d-block">
            <label for="staff-search" class="form-label">Search staff by name or ID</label>
            <input id="staff-search" v-model="searchTerm" type="text" class="form-control search-input">
        </search>

        <div v-if="fetchStaffMessage" role="alert" class="alert alert-danger">{{ fetchStaffMessage }}</div>
        
        <div v-else-if="filteredStaff.length > 0" class="table-responsive">
            <table class="table table-striped table-hover align-middle">
                <caption>Trek Staff accounts</caption>
                
                <thead>
                    <tr>
                        <th scope="col">ID</th>
                        <th scope="col">Name</th>
                        <th scope="col">Email</th>
                        <th scope="col">Status</th>
                        <th scope="col">Action</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="staff in filteredStaff" :key="staff.id">
                        <td>{{ staff.id }}</td>
                        <td>{{ staff.username }}</td>
                        <td>{{ staff.email }}</td>
                        <td>
                            <span class="badge" :class="staff.status === 'Active' ? 'badge-brand-active' : 'badge-brand-inactive'">
                                {{ staff.status }}
                            </span>
                        </td>
                        <td>
                            <button type="button" class="btn btn-sm btn-outline-secondary" @click="toggleStatus(staff)">
                                {{ staff.status === "Active" ? "Blacklist" : "Unblacklist" }}
                            </button>
                        </td>
                    </tr>
                </tbody>

            </table>
        </div>

        <p v-else>No staff match your search.</p>
        <p v-if="statusMessage" role="alert" class="alert alert-danger">{{ statusMessage }}</p>
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
            fetchStaffMessage: null,
            allStaff: [],
            statusMessage: null,
            searchTerm: ""
        };
    },

    computed: {
        filteredStaff() {
            const term = this.searchTerm.trim().toLowerCase();
            if (!term) return this.allStaff;

            return this.allStaff.filter(staff =>
                staff.username.toLowerCase().includes(term) ||
                String(staff.id) === term
            );
        }
    },

    mounted() {
        this.fetchStaff();
    },

    methods: {
        async fetchStaff() {
            try {
                const response = await apiFetch("/staff/all");
                const data = await response.json();

                if (response.ok) {
                    this.allStaff = data.staff;
                    this.fetchStaffMessage = null;
                } else {
                    this.fetchStaffMessage = data.info || "Failed to fetch staff";
                    console.error("Failed to fetch staff:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching staff:", error);
            }
        },

        async toggleStatus(staff) {
            const newStatus = staff.status === "Active" ? "Blacklisted" : "Active";

            try {
                const response = await apiFetch(`/staff/${staff.id}/status`, {
                    method: "POST",
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await response.json();

                if (response.ok) {
                    staff.status = newStatus;
                    this.statusMessage = null;
                } else {
                    this.statusMessage = data.status_info || "Failed to change status";
                    console.error(`Failed to change status for Staff ID ${staff.id}:`, response.statusText, data);
                }
                
            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error(`Error changing status for Staff ID ${staff.id}:`, error);
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
