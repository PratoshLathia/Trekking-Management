<template>
    <div class="d-flex flex-column min-vh-100">

        <nav class="navbar navbar-dark navbar-brand-theme">
            <div class="container-fluid px-4">
                <router-link to="/" class="navbar-brand mb-0">TrekMate</router-link>
                <ul class="navbar-nav flex-row gap-2 mb-0">
                    <li class="nav-item"><router-link to="/login" class="btn btn-brand-outline-light btn-sm">Login</router-link></li>
                    <li class="nav-item"><router-link to="/register" class="btn btn-brand-gold btn-sm">Register</router-link></li>
                </ul>
            </div>
        </nav>

        <header class="hero-trek text-center">
            <div class="container">
                <h1 class="display-4 fw-bold">Find Your Next Trail</h1>
                <p class="lead">Discover, book, and manage treks — all in one place.</p>
                <router-link to="/register" class="btn btn-brand-gold btn-lg mt-3">Start Exploring</router-link>
            </div>
        </header>

        <section aria-labelledby="stats-heading" class="stats-band py-5">
            <div class="container">
                <h2 id="stats-heading" class="visually-hidden">By the Numbers</h2>
                <dl class="row text-center mb-0">
                    <div class="col-md-4">
                        <dt class="display-6 fw-bold">{{ treks.length }}</dt>
                        <dd>Treks Available</dd>
                    </div>
                    <div class="col-md-4">
                        <dt class="display-6 fw-bold">100%</dt>
                        <dd>Easy Booking</dd>
                    </div>
                    <div class="col-md-4">
                        <dt class="display-6 fw-bold">24/7</dt>
                        <dd>Staff Support</dd>
                    </div>
                </dl>
            </div>
        </section>

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
                        </div>
                    </article>
                </li>
            </ul>
        </section>

        <footer class="navbar-brand-theme text-center text-white py-3 mt-auto">
            <p class="mb-0">&copy; 2026 TrekMate. Built for adventurers.</p>
        </footer>
        
    </div>
</template>

<script>
import { apiFetch } from "../api.js";

export default {
    data() {
        return {
            treks: [],
            loading: true,
            error: false
        };
    },

    mounted() {
        this.fetchTreks();
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
        }
    }
};
</script>

<style scoped>
.hero-trek {
    background:
        linear-gradient(rgba(10, 30, 20, 0.55), rgba(10, 30, 20, 0.65)),
        url('../assets/hero-trek.jpg') center / cover no-repeat,
        linear-gradient(160deg, #2f5744 0%, #1c3f2d 55%, #0f2a1e 100%);
    color: #ffffff;
    min-height: 70vh;
    display: flex;
    align-items: center;
    padding: 3rem 1rem;
}

.hero-trek h1 {
    color: #ffffff;
}

.hero-trek .lead {
    color: #e8e4d8;
}

.stats-band {
    background-color: #f5f0e6;
}
</style>
