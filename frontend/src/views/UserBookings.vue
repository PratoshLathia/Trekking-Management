<template>
    <Navbar />

    <main class="container py-4">
        <h1 class="mb-4">My Bookings</h1>

        <p><router-link to="/user" class="btn btn-outline-secondary btn-sm">← Back to Dashboard</router-link></p>
        <br>

        <p v-if="bookingMessage" role="alert" class="alert alert-danger">{{ bookingMessage }}</p>

        <section class="mb-4">
            <button v-if="exportState === 'idle'" type="button" class="btn btn-outline-secondary btn-sm" @click="startExport">
                Export as CSV
            </button>
            <p v-if="exportState === 'pending'" class="text-muted">Preparing your export...</p>
            <button v-if="exportState === 'ready'" type="button" class="btn btn-brand-gold btn-sm" @click="downloadExport">
                Download CSV
            </button>
            <p v-if="exportState === 'failed'" role="alert" class="alert alert-danger">Export failed - please try again.</p>
        </section>

        <div v-if="bookings.length > 0" class="table-responsive">
            <table class="table table-striped table-hover align-middle">
                <caption>Every trek you've ever booked, including past cancellations</caption>
                
                <thead>
                    <tr>
                        <th scope="col">Trek Name</th>
                        <th scope="col">Booking Date</th>
                        <th scope="col">Status</th>
                        <th scope="col">Payment Status</th>
                        <th scope="col">Action</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="booking in bookings" :key="booking.bookingId">
                        <td>{{ booking.trekName }}</td>
                        <td>{{ booking.bookingDate }}</td>
                        <td>{{ booking.status }}</td>
                        <td>{{ booking.paymentStatus }}</td>
                        <td>
                            <button v-if="booking.status === 'Booked'" type="button" class="btn btn-sm btn-outline-danger" @click="cancelBooking(booking)">
                                Cancel Booking
                            </button>
                        </td>
                    </tr>
                </tbody>

            </table>
        </div>
        
        <p v-else>You haven't booked any treks yet.</p>
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
            user: [],
            bookings: [],
            bookingMessage: null,

            exportState: "idle",
            exportTaskId: null
        };
    },

    mounted() {
        this.user = JSON.parse(localStorage.getItem("user"));
        this.fetchMyBookings();
    },

    methods: {
        async fetchMyBookings() {
            try {
                const response = await apiFetch(`/user/${this.user.id}/bookings`);
                const data = await response.json();

                if (response.ok) {
                    this.bookings = data.bookings.map(booking => ({
                        bookingId: booking.booking_id,
                        trekId: booking.trek_id,
                        trekName: booking.trek_name,
                        bookingDate: booking.booking_date,
                        status: booking.status,
                        paymentStatus: booking.payment_status
                    }));
                    this.bookingMessage = null;
                } else {
                    this.bookingMessage = data.booking_info || "Failed to fetch bookings";
                    console.error("Failed to fetch bookings:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching bookings:", error);
            }
        },

        async cancelBooking(booking) {
            try {
                const response = await apiFetch(`/booking/${booking.bookingId}/cancel`, {
                    method: "POST"
                });
                const data = await response.json();

                if (response.ok) {
                    this.fetchMyBookings();
                } else {
                    this.bookingMessage = data.booking_info || "Failed to cancel booking";
                    console.error("Failed to cancel booking:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error cancelling booking:", error);
            }
        },

        async startExport() {
            try {
                const response = await apiFetch("/booking/export", { method: "POST" });
                const data = await response.json();

                if (!response.ok) {
                    this.exportState = "failed";
                    console.error("Failed to start export:", response.statusText, data);
                    return;
                }

                this.exportTaskId = data.task_id;
                this.exportState = "pending";
                this.pollExportStatus();

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error starting export:", error);
            }
        },

        async pollExportStatus() {
            try {
                const response = await apiFetch(`/booking/export/${this.exportTaskId}/status`);
                const data = await response.json();

                if (!response.ok) {
                    this.exportState = "failed";
                    console.error("Failed to check export status:", response.statusText, data);
                    return;
                }

                if (data.ready) {
                    this.exportState = data.state === "SUCCESS" ? "ready" : "failed";
                    return;
                }

                setTimeout(() => this.pollExportStatus(), 2000);

            } catch (error) {
                this.exportState = "failed";
                console.error("Error checking export status:", error);
            }
        },

        async downloadExport() {
            try {
                const response = await apiFetch(`/booking/export/${this.exportTaskId}/download`);
                if (!response.ok) {
                    const data = await response.json();
                    alert("Could not download the export.");
                    console.error("Failed to download export:", response.statusText, data);
                    return;
                }

                const blob = await response.blob();
                const blobUrl = URL.createObjectURL(blob);

                const link = document.createElement("a");
                link.href = blobUrl;
                link.download = "my_bookings.csv";
                link.click();

                URL.revokeObjectURL(blobUrl);
                this.exportState = "idle";
                this.exportTaskId = null;

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error downloading export:", error);
            }
        }
    }
};
</script>

<style scoped></style>
