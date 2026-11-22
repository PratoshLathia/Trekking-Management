<template>
    <Navbar />

    <main class="container py-4">
        <h1 class="mb-4">Background Jobs AND Reports</h1>

        <section class="mb-5">
            <h2 class="h4 mb-3">Trigger a Job Now</h2>
            <p class="text-muted">
                These jobs normally run automatically on their own schedule via Celery Beat -
                trek reminders every day at 8:00 AM, the activity report on the 1st of each
                month. The buttons below just queue the same job immediately instead of
                waiting, so it can be demoed without waiting for the actual scheduled time.
            </p>
            <br>

            <div class="d-flex gap-2 flex-wrap">
                <button type="button" class="btn btn-brand-gold" @click="runReminders">Send Trek Reminders Now</button>
                <button type="button" class="btn btn-brand-gold" @click="runReport">Generate Monthly Report Now</button>
            </div>

            <p v-if="jobMessage" role="alert" class="alert mt-3" :class="jobSuccess ? 'alert-info' : 'alert-danger'">
                {{ jobMessage }}
            </p>
        </section>

        <section>
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h2 class="h4 mb-0">Generated Reports</h2>
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="fetchReports">Refresh List</button>
            </div>
            <p v-if="fetchReportsMessage" role="alert" class="alert alert-danger">{{ fetchReportsMessage }}</p>
            <ul v-if="reports.length > 0" class="list-group">
                <li v-for="report in reports" :key="report" class="list-group-item d-flex justify-content-between align-items-center">
                    {{ report }}
                    <button type="button" class="btn btn-sm btn-outline-primary" @click="viewReport(report)">View</button>
                </li>
            </ul>
            <p v-else>No reports generated yet.</p>
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
            reports: [],
            fetchReportsMessage: null,
            jobMessage: null,
            jobSuccess: false
        };
    },

    mounted() {
        this.fetchReports();
    },

    methods: {
        async fetchReports() {
            try {
                const response = await apiFetch("/admin/reports");
                const data = await response.json();
                if (response.ok) {
                    this.reports = data.reports;
                    this.fetchReportsMessage = null;
                } else {
                    this.fetchReportsMessage = data.info || "Failed to fetch reports";
                    console.error("Failed to fetch reports:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching reports:", error);
            }
        },

        async runReminders() {
            try {
                const response = await apiFetch("/admin/reminders/run", { method: "POST" });
                const data = await response.json();
                this.jobSuccess = response.ok;
                this.jobMessage = data.info || (response.ok ? "Reminder job queued" : "Failed to queue reminder job");
                if (!response.ok) {
                    console.error("Failed to queue reminder job:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error queueing reminder job:", error);
            }
        },

        async runReport() {
            try {
                const response = await apiFetch("/admin/reports/generate", { method: "POST" });
                const data = await response.json();
                this.jobSuccess = response.ok;
                this.jobMessage = data.info || (response.ok ? "Report job queued" : "Failed to queue report job");
                if (!response.ok) {
                    console.error("Failed to queue report job:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error queueing report job:", error);
            }
        },

        async viewReport(filename) {
            try {
                const response = await apiFetch(`/admin/reports/${encodeURIComponent(filename)}`);
                if (!response.ok) {
                    const data = await response.json();
                    alert("Could not open that report.");
                    console.error("Failed to open report:", response.statusText, data);
                    return;
                }
                const blob = await response.blob();
                const blobUrl = URL.createObjectURL(blob);
                window.open(blobUrl, "_blank");

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error opening report:", error);
            }
        }
    }
};
</script>

<style scoped></style>
