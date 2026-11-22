<template>
    <Navbar />

    <main class="container py-4">
        <h1 class="mb-4">Admin Dashboard</h1>

        <nav aria-label="Admin actions">
            <ul class="list-unstyled d-flex flex-wrap gap-2">
                <li><router-link to="/add-trek" class="btn btn-brand-gold">Add Trek</router-link></li>
                <li><router-link to="/add-staff" class="btn btn-brand-gold">Add Staff</router-link></li>
                <li><router-link to="/user-management" class="btn btn-outline-secondary">Manage Users</router-link></li>
                <li><router-link to="/staff-management" class="btn btn-outline-secondary">Manage Staff</router-link></li>
                <li><router-link to="/trek-management" class="btn btn-outline-secondary">Manage Treks</router-link></li>
                <li><router-link to="/all-bookings" class="btn btn-outline-secondary">View Bookings</router-link></li>
                <li><router-link to="/statistics" class="btn btn-outline-secondary">View Statistics</router-link></li>
                <li><router-link to="/reports" class="btn btn-outline-secondary">Reports &amp; Jobs</router-link></li>
            </ul>
        </nav>

        <section aria-labelledby="featured-heading" class="container py-5">
            <h2 id="featured-heading" class="text-center mb-4">Featured Treks</h2>

            <p v-if="loading" class="text-center">Loading treks...</p>
            <p v-else-if="error" class="text-center alert alert-danger">Could not load treks right now.</p>
            <p v-else-if="treks.length === 0" class="text-center">No treks available yet.</p>

            <ul v-else class="row list-unstyled">
                <li v-for="trek in treks.slice(0, 6)" :key="trek.id" class="col-md-4 mb-4">
                    <article class="card h-100 shadow-sm">
                        <div class="card-body">
                            <h3 class="card-title h5">{{ trek.name }}</h3>
                            <p class="card-text mb-1">{{ trek.location }}</p>
                            <p class="card-text mb-1">{{ trek.duration }}</p>
                            <p class="card-text"><span class="badge text-bg-secondary">{{ trek.stage }}</span></p>
                            <br>
                            <button type="button" class="btn btn-sm btn-brand-gold" @click="$router.push(`/trek-bookings/${trek.id}`)">View Bookings</button>
                        </div>
                    </article>
                </li>
            </ul>
        </section>

        <section aria-labelledby="pending-changes-heading" class="container py-3">
            <h2 id="pending-changes-heading" class="mb-3">Pending Trek Change Requests</h2>

            <p v-if="requestsMessage" role="alert" class="alert alert-danger">{{ requestsMessage }}</p>
            <p v-else-if="pendingRequests.length === 0">No pending change requests.</p>

            <div v-else class="table-responsive">
                <table class="table table-striped table-hover align-middle">
                    <caption>Trek changes waiting for admin approval</caption>

                    <thead>
                        <tr>
                            <th scope="col">Trek</th>
                            <th scope="col">Staff</th>
                            <th scope="col">Field</th>
                            <th scope="col">Old Value</th>
                            <th scope="col">New Value</th>
                            <th scope="col">Action</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="req in pendingRequests" :key="req.id">
                            <td>{{ req.trek_name }}</td>
                            <td>{{ req.staff_name }}</td>
                            <td>{{ req.field }}</td>
                            <td>{{ req.old_value }}</td>
                            <td>{{ req.new_value }}</td>
                            <td class="d-flex gap-1 flex-wrap">
                                <button type="button" class="btn btn-sm btn-brand-gold" @click="approveRequest(req.id)">Approve</button>
                                <button type="button" class="btn btn-sm btn-outline-danger" @click="rejectRequest(req.id)">Reject</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>
        
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
            treks: [],
            loading: true,
            error: false,
            pendingRequests: [],
            requestsMessage: null
        };
    },

    mounted() {
        this.fetchTreks();
        this.fetchPendingRequests();
    },

    methods: {
        async fetchTreks() {
            try {
                const response = await apiFetch("/trek/all");
                const data = await response.json();

                if (response.ok) {
                    this.treks = data.treks;
                } else if (response.status === 404) {
                    this.treks = [];
                } else {
                    this.error = true;
                    console.error("Failed to fetch treks:", response.statusText, data);
                }

            } catch (error) {
                this.error = true;
                console.error("Error fetching treks:", error);
            } finally {
                this.loading = false;
            }
        },

        async fetchPendingRequests() {
            try {
                const response = await apiFetch("/trek/change_requests");
                const data = await response.json();

                if (response.ok) {
                    this.pendingRequests = data.requests;
                    this.requestsMessage = null;
                } else {
                    this.requestsMessage = data.info || "Failed to fetch pending change requests";
                    console.error("Failed to fetch change requests:", response.statusText, data);
                }

            } catch (error) {
                this.requestsMessage = "Unable to reach the server. Please try again.";
                console.error("Error fetching change requests:", error);
            }
        },

        async approveRequest(requestId) {
            try {
                const response = await apiFetch(`/trek/change_requests/${requestId}/approve`, {
                    method: "POST"
                });
                const data = await response.json();

                if (response.ok) {
                    await this.fetchPendingRequests();
                    await this.fetchTreks();
                } else {
                    this.requestsMessage = data.info || "Failed to approve request";
                    console.error("Failed to approve request:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error approving request:", error);
            }
        },

        async rejectRequest(requestId) {
            try {
                const response = await apiFetch(`/trek/change_requests/${requestId}/reject`, {
                    method: "POST"
                });
                const data = await response.json();

                if (response.ok) {
                    await this.fetchPendingRequests();
                } else {
                    this.requestsMessage = data.info || "Failed to reject request";
                    console.error("Failed to reject request:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error rejecting request:", error);
            }
        }
    }
};
</script>

<style scoped></style>
