<template>
    <Navbar />

    <main class="container py-4">
        <h1 class="mb-4">Booking Records</h1>
        <div v-if="fetchBookingsMessage" role="alert" class="alert alert-danger">{{ fetchBookingsMessage }}</div>
        
        <div v-else-if="allBookings.length > 0" class="table-responsive">
            <table class="table table-striped table-hover align-middle">
                <caption>Every booking ever made, across all treks</caption>

                <thead>
                    <tr>
                        <th scope="col">Booking ID</th>
                        <th scope="col">Username</th>
                        <th scope="col">Email</th>
                        <th scope="col">Trek</th>
                        <th scope="col">Booking Date</th>
                        <th scope="col">Booking Status</th>
                        <th scope="col">Payment Status</th>
                        <th scope="col">Trek Status</th>
                        <th scope="col">Trek Stage</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="booking in allBookings" :key="booking.id">
                        <td>{{ booking.id }}</td>
                        <td>{{ booking.username }}</td>
                        <td>{{ booking.email }}</td>
                        <td>{{ booking.trekName }}</td>
                        <td>{{ booking.bookingDate }}</td>
                        <td>{{ booking.bookingStatus }}</td>
                        <td>{{ booking.paymentStatus }}</td>
                        <td>{{ booking.trekStatus }}</td>
                        <td>{{ booking.trekStage }}</td>
                    </tr>
                </tbody>

            </table>
        </div>

        <p v-else>No booking records found.</p>
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
            allBookings: [],
            fetchBookingsMessage: null
        };
    },

    mounted() {
        this.fetchAllBookings();
    },

    methods: {
        async fetchAllBookings() {
            try {
                const response = await apiFetch("/booking/all");
                const data = await response.json();

                if (response.ok) {
                    this.allBookings = data.all_bookings.map(booking => ({
                        id: booking.id,
                        username: booking.username,
                        email: booking.email,
                        trekName: booking.trek_name,
                        bookingDate: booking.booking_date,
                        bookingStatus: booking.booking_status,
                        paymentStatus: booking.payment_status,
                        trekStatus: booking.trek_status,
                        trekStage: booking.trek_stage
                    }));
                    this.fetchBookingsMessage = null;
                } else {
                    this.fetchBookingsMessage = data.info || "Failed to fetch bookings";
                    console.error("Failed to fetch bookings:", response.statusText, data);
                }
                
            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching bookings:", error);
            }
        }
    }
};
</script>

<style scoped></style>
