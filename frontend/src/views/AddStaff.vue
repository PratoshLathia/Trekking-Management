<template>
    <Navbar />

    <main class="container py-4 narrow-form">
        <h1 class="mb-4">Add Staff</h1>
        <form @submit.prevent="addStaff">
            <fieldset class="border-0 p-0">
                <legend class="visually-hidden">New staff account</legend>

                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input id="name" v-model="name" type="text" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input id="email" v-model="email" type="email" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input id="password" v-model="password" type="password" class="form-control" required>
                </div>
                
            </fieldset>

            <button type="submit" class="btn btn-brand-gold">Submit</button>
        </form>
        <p v-if="formMessage" role="alert" class="alert mt-3" :class="formSuccess ? 'alert-success' : 'alert-danger'">
            {{ formMessage }}
        </p>
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
            name: "",
            email: "",
            password: "",
            formMessage: null,
            formSuccess: false
        };
    },

    methods: {
        async addStaff() {
            try {
                const response = await apiFetch("/staff/add", {
                    method: "POST",
                    body: JSON.stringify({
                        username: this.name,
                        email: this.email,
                        password: this.password
                    })
                });
                const data = await response.json();

                this.formSuccess = response.ok;
                if (response.ok) {
                    this.formMessage = data.info;
                } else {
                    this.formMessage = data.info || "An error occurred while adding staff.";
                    console.error("Error adding staff:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error adding staff:", error);
            }
        }
    }
};
</script>

<style scoped>
.narrow-form {
    margin: 0 auto;
    max-width: 480px;
}
</style>
