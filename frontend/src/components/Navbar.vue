<template>
    <nav class="navbar navbar-dark navbar-brand-theme">
        <div class="container-fluid px-4">
            <span class="navbar-brand mb-0">TrekMate</span>

            <section v-if="loggedIn()" class="d-flex flex-wrap align-items-center gap-3">
                <ul v-if="role() === 'admin'" class="navbar-nav flex-row flex-wrap gap-3 mb-0">
                    <li class="nav-item"><router-link class="nav-link" to="/">Home</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/admin">Admin Dashboard</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/user-management">Users</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/staff-management">Staff</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/trek-management">Treks</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/all-bookings">Bookings</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/statistics">Statistics</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/reports">Reports</router-link></li>
                </ul>
                <ul v-if="role() === 'staff'" class="navbar-nav flex-row flex-wrap gap-3 mb-0">
                    <li class="nav-item"><router-link class="nav-link" to="/">Home</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/staff">Staff Dashboard</router-link></li>
                </ul>
                <ul v-if="role() === 'user'" class="navbar-nav flex-row flex-wrap gap-3 mb-0">
                    <li class="nav-item"><router-link class="nav-link" to="/">Home</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/user">Dashboard</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/user-bookings">My Bookings</router-link></li>
                </ul>
                <button type="button" class="btn btn-brand-outline-light btn-sm" @click="logOut">Logout</button>
            </section>
            <section v-else>
                <ul class="navbar-nav flex-row gap-3 mb-0">
                    <li class="nav-item"><router-link class="nav-link" to="/login">Login</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/register">Register</router-link></li>
                </ul>
            </section>
        </div>
    </nav>
</template>

<script>
export default {
    methods: {
        // Logging out is purely a client-side concept for this app - there's
        // no server-side session to invalidate, so clearing the saved JWT
        // and redirecting to /login is all that's needed.
        logOut() {
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            this.$router.push("/login");
        },

        loggedIn() {
            return localStorage.getItem("token");
        },

        role() {
            const user = JSON.parse(localStorage.getItem("user"));
            return user?.role;
        }
    }
};
</script>

<style scoped></style>
