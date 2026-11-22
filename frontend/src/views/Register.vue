<template>
    <main class="container py-5 narrow-form">
        <h1 class="mb-4 text-center">Register</h1>
        <form @submit.prevent="register">
            <fieldset class="border-0 p-0">
                <legend class="visually-hidden">New trekker account</legend>

                <div class="mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input id="username" v-model="username" type="text" class="form-control" required>
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
            
            <button type="submit" class="btn btn-brand-gold w-100">Register</button>
        </form>
        <p v-if="registerMessage" role="alert" class="alert alert-danger mt-3">{{ registerMessage }}</p>
    </main>
</template>

<script>
import { apiFetch } from "../api.js";

export default {
    data() {
        return {
            username: "",
            email: "",
            password: "",
            registerMessage: null
        };
    },

    methods: {
        async register() {
            try {
                const response = await apiFetch("/register", {
                    method: "POST",
                    body: JSON.stringify({
                        username: this.username,
                        email: this.email,
                        password: this.password
                    })
                });
                const data = await response.json();

                if (response.ok) {
                    this.$router.push("/login");
                } else {
                    this.registerMessage = data.info || "Registration failed";
                    console.error("Registration failed:", response.statusText, data);
                }
                
            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Request failed:", error);
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
