<template>
    <Navbar />

    <main class="container py-4">
        <h1 class="mb-4">Bookings for {{ trekName }}</h1>
        <p v-if="user.role === 'staff'">
            <router-link to="/staff" class="btn btn-outline-secondary btn-sm">← Back to Dashboard</router-link>
        </p>
        <p v-if="user.role === 'admin'">
            <router-link to="/admin" class="btn btn-outline-secondary btn-sm">← Back to Dashboard</router-link>
        </p>
        <br>

        <p v-if="bookingsMessage" role="alert" class="alert alert-danger">{{ bookingsMessage }}</p>

        <div v-if="bookings.length > 0" class="table-responsive">
            <table class="table table-striped table-hover align-middle">
                <caption>Trekkers currently booked on this trek</caption>
                
                <thead>
                    <tr>
                        <th scope="col">User ID</th>
                        <th scope="col">Username</th>
                        <th scope="col">Email</th>
                        <th scope="col">Booking Date</th>
                        <th scope="col">Booking Status</th>
                        <th scope="col">Payment Status</th>
                        <th scope="col">Action</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="booking in bookings" :key="booking.bookingId">
                        <td>{{ booking.userId }}</td>
                        <td>{{ booking.username }}</td>
                        <td>{{ booking.email }}</td>
                        <td>{{ booking.booking_date }}</td>
                        <td>{{ booking.status }}</td>
                        <td>{{ booking.paymentStatus }}</td>
                        <td>
                            <button type="button" class="btn btn-sm btn-outline-danger" @click="removeBooking(booking.bookingId)">Remove</button>
                        </td>
                    </tr>
                </tbody>

            </table>
        </div>

        <p v-else>No registered users for this trek.</p>
    </main>
</template>

<script>
import Navbar from "../components/Navbar.vue";
import { apiFetch } from "../api.js";

export default {
    components: {
        Navbar
    },

    props: {
        trekId: {
            type: [String, Number],
            required: true
        }
    },

    data() {
        return {
            user: [],
            trekName: "",
            bookings: [],
            bookingsMessage: null
        };
    },

    mounted() {
        this.user = JSON.parse(localStorage.getItem("user"));
        this.fetchBookings();
    },

    methods: {
        async fetchBookings() {
            try {
                const response = await apiFetch(`/trek/${this.trekId}/bookings`);
                const data = await response.json();

                if (response.ok) {
                    this.trekName = data.trek_name;
                    this.bookings = data.bookings.map(booking => ({
                        bookingId: booking.booking_id,
                        userId: booking.user_id,
                        username: booking.username,
                        email: booking.email,
                        booking_date: booking.booking_date,
                        status: booking.status,
                        paymentStatus: booking.payment_status
                    }));
                    this.bookingsMessage = null;
                } else {
                    this.bookingsMessage = data.booking_info || "Failed to fetch participants";
                    console.error("Failed to fetch participants:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching participants:", error);
            }
        },

        async removeBooking(bookingId) {
            try {
                const response = await apiFetch(`/booking/${bookingId}/remove`, {
                    method: "POST"
                });
                const data = await response.json();

                if (response.ok) {
                    this.bookingsMessage = null;
                    this.fetchBookings();
                } else {
                    this.bookingsMessage = data.booking_info || "Failed to remove participant";
                    console.error(`Failed to remove booking ID ${bookingId}:`, response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error removing participant:", error);
            }
        }
    }
};
</script>

<style scoped></style>
