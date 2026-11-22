<template>
    <Navbar />

    <main class="container py-4">
        <h1 class="mb-4">Trekking Statistics</h1>

        <p v-if="fetchStatsMessage" role="alert" class="alert alert-danger">{{ fetchStatsMessage }}</p>
        <div class="row row-cols-1 row-cols-md-3 g-3">

            <div class="col">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <p class="display-6 mb-0">{{ stats.totalUsers }}</p>
                        <p class="text-muted mb-0">Total Users</p>
                    </div>
                </div>
            </div>

            <div class="col">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <p class="display-6 mb-0">{{ stats.totalStaff }}</p>
                        <p class="text-muted mb-0">Total Staff</p>
                    </div>
                </div>
            </div>

            <div class="col">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <p class="display-6 mb-0">{{ stats.totalTreks }}</p>
                        <p class="text-muted mb-0">Total Treks</p>
                    </div>
                </div>
            </div>

            <div class="col">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <p class="display-6 mb-0">{{ stats.totalBookings }}</p>
                        <p class="text-muted mb-0">Total Bookings</p>
                    </div>
                </div>
            </div>

            <div class="col">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <p class="display-6 mb-0">{{ stats.activeTreks }}</p>
                        <p class="text-muted mb-0">Open Treks</p>
                    </div>
                </div>
            </div>

            <div class="col">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <p class="display-6 mb-0">{{ stats.closedTreks }}</p>
                        <p class="text-muted mb-0">Closed Treks</p>
                    </div>
                </div>
            </div>

            <div class="col">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <p class="display-6 mb-0">{{ stats.completedTreks }}</p>
                        <p class="text-muted mb-0">Completed Treks</p>
                    </div>
                </div>
            </div>

        </div>
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
            stats: {},
            fetchStatsMessage: null
        };
    },

    mounted() {
        this.fetchStats();
    },

    methods: {
        async fetchStats() {
            try {
                const response = await apiFetch("/stats");
                const data = await response.json();

                if (response.ok) {
                    this.stats = {
                        totalUsers: data.stats.total_users,
                        totalStaff: data.stats.total_staff,
                        totalTreks: data.stats.total_treks,
                        totalBookings: data.stats.total_bookings,
                        activeTreks: data.stats.active_treks,
                        closedTreks: data.stats.closed_treks,
                        completedTreks: data.stats.completed_treks
                    };
                    this.fetchStatsMessage = null;
                } else {
                    this.fetchStatsMessage = data.info || "Failed to fetch statistics";
                    console.error("Failed to fetch stats:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching stats:", error);
            }
        }
    }
};
</script>

<style scoped></style>
