<template>
    <Navbar />

    <main class="container py-4">
        <h1 class="mb-4">Manage Users</h1>

        <search class="mb-3 d-block">
            <label for="user-search" class="form-label">Search users by name or ID</label>
            <input id="user-search" v-model="searchTerm" type="text" class="form-control search-input">
        </search>

        <div v-if="fetchUsersMessage" role="alert" class="alert alert-danger">{{ fetchUsersMessage }}</div>

        <div v-else-if="filteredUsers.length > 0" class="table-responsive">
            <table class="table table-striped table-hover align-middle">
                <caption>Trekker accounts</caption>

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
                    <tr v-for="user in filteredUsers" :key="user.id">
                        <td>{{ user.id }}</td>
                        <td>{{ user.username }}</td>
                        <td>{{ user.email }}</td>
                        <td>
                            <span class="badge" :class="user.status === 'Active' ? 'badge-brand-active' : 'badge-brand-inactive'">
                                {{ user.status }}
                            </span>
                        </td>
                        <td>
                            <button type="button" class="btn btn-sm btn-outline-secondary" @click="toggleStatus(user)">
                                {{ user.status === "Active" ? "Blacklist" : "Unblacklist" }}
                            </button>
                        </td>
                    </tr>
                </tbody>

            </table>
        </div>

        <p v-else>No users match your search.</p>
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
            fetchUsersMessage: null,
            allUsers: [],
            statusMessage: null,
            searchTerm: ""
        };
    },

    computed: {
        filteredUsers() {
            const term = this.searchTerm.trim().toLowerCase();
            if (!term) return this.allUsers;

            return this.allUsers.filter(user =>
                user.username.toLowerCase().includes(term) ||
                String(user.id) === term
            );
        }
    },

    mounted() {
        this.fetchUsers();
    },

    methods: {
        async fetchUsers() {
            try {
                const response = await apiFetch("/user/all");
                const data = await response.json();

                if (response.ok) {
                    this.allUsers = data.users;
                    this.fetchUsersMessage = null;
                } else {
                    this.fetchUsersMessage = data.info || "Failed to fetch users";
                    console.error("Failed to fetch users:", response.statusText, data);
                }
            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching users:", error);
            }
        },

        async toggleStatus(user) {
            const newStatus = user.status === "Active" ? "Blacklisted" : "Active";

            try {
                const response = await apiFetch(`/user/${user.id}/status`, {
                    method: "POST",
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await response.json();

                if (response.ok) {
                    user.status = newStatus;
                    this.statusMessage = null;
                } else {
                    this.statusMessage = data.status_info || "Failed to change status";
                    console.error(`Failed to change status for User ID ${user.id}:`, response.statusText, data);
                }
            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error(`Error changing status for User ID ${user.id}:`, error);
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
