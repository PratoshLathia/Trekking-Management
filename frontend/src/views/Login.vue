<template>
    <main class="container py-5 narrow-form">
        <h1 class="mb-4 text-center">Login</h1>
        <form @submit.prevent="login">
            <fieldset class="border-0 p-0">
                <legend class="visually-hidden">Account credentials</legend>

                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input id="email" v-model="email" type="email" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input id="password" v-model="password" type="password" class="form-control" required>
                </div>
            
            </fieldset>
            
            <button type="submit" class="btn btn-brand-gold w-100">Submit</button>
        </form>
        <p v-if="loginMessage" role="alert" class="alert alert-danger mt-3">{{ loginMessage }}</p>
    </main>
</template>

<script>
import { apiFetch } from "../api.js";

export default {
    data() {
        return {
            email: "",
            password: "",
            loginMessage: null
        };
    },

    methods: {
        async login() {
            try {
                const response = await apiFetch("/login", {
                    method: "POST",
                    body: JSON.stringify({
                        email: this.email,
                        password: this.password
                    })
                });
                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem("token", data.token);
                    localStorage.setItem("user", JSON.stringify(data.user));

                    if (data.user.role === "admin") {
                        this.$router.push("/admin");
                    } else if (data.user.role === "user") {
                        this.$router.push("/user");
                    } else if (data.user.role === "staff") {
                        this.$router.push("/staff");
                    } else {
                        this.loginMessage = data.info || "Unknown role";
                        console.error("Unknown role:", response.statusText, data);
                    }
                } else {
                    this.loginMessage = data.info || "Login failed";
                    console.error("Login failed:", response.statusText, data);
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
