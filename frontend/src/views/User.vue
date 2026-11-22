<template>
    <Navbar />

    <main class="container py-4">
        <h1 class="mb-1">User Dashboard</h1>
        <p class="text-muted mb-4">Welcome, {{ user.username }}!</p>

        <section v-if="isBlacklisted">
            <h2 class="h4 mb-3">My Profile</h2>
            <dl v-if="profile" class="row">
                <dt class="col-sm-3">Contact Number</dt>
                <dd class="col-sm-9">{{ profile.contactNumber }}</dd>
                <dt class="col-sm-3">Age</dt>
                <dd class="col-sm-9">{{ profile.age }}</dd>
                <dt class="col-sm-3">Gender</dt>
                <dd class="col-sm-9">{{ profile.gender }}</dd>
                <dt class="col-sm-3">Address</dt>
                <dd class="col-sm-9">{{ profile.address }}</dd>
                <dt class="col-sm-3">Medical Conditions</dt>
                <dd class="col-sm-9">{{ profile.medicalConditions || "None" }}</dd>
                <dt class="col-sm-3">Emergency Contact</dt>
                <dd class="col-sm-9">{{ profile.emergencyContactName }} ({{ profile.emergencyContactNumber }})</dd>
            </dl>
            <p role="alert" class="alert alert-danger"><strong>You are blacklisted. Contact admin.</strong></p>
        </section>

        <template v-else>

            <section v-if="!profile && !editingProfile">
                <h2 class="h4 mb-3">Complete Your Profile</h2>
                <p>Please complete your profile to access your dashboard.</p>
                <br>
                <button type="button" class="btn btn-brand-gold" @click="startEdit">Complete Profile</button>
            </section>

            <section v-if="editingProfile" class="narrow-form">
                <h2 class="h4 mb-3">{{ profile ? "Edit Profile" : "Complete Profile" }}</h2>
                <form @submit.prevent="saveProfile">

                    <fieldset class="border-0 p-0">
                        <legend class="visually-hidden">Trekker profile</legend>

                        <div class="mb-3">
                            <label for="user-contact" class="form-label">Contact Number</label>
                            <input id="user-contact" v-model="profileForm.contactNumber" type="text" class="form-control" required>
                        </div>

                        <div class="mb-3">
                            <label for="user-age" class="form-label">Age</label>
                            <input id="user-age" v-model.number="profileForm.age" type="number" class="form-control" required>
                        </div>

                        <div class="mb-3">
                            <label for="user-gender" class="form-label">Gender</label>
                            <select id="user-gender" v-model="profileForm.gender" class="form-select" required>
                                <option value="Male">Male</option>
                                <option value="Female">Female</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="user-address" class="form-label">Address</label>
                            <input id="user-address" v-model="profileForm.address" type="text" class="form-control" required>
                        </div>

                        <div class="mb-3">
                            <label for="user-medical" class="form-label">Medical Conditions (if any)</label>
                            <textarea id="user-medical" v-model="profileForm.medicalConditions" class="form-control"></textarea>
                        </div>

                        <div class="mb-3">
                            <label for="user-emergency-name" class="form-label">Emergency Contact Name</label>
                            <input id="user-emergency-name" v-model="profileForm.emergencyContactName" type="text" class="form-control" required>
                        </div>

                        <div class="mb-3">
                            <label for="user-emergency-number" class="form-label">Emergency Contact Number</label>
                            <input id="user-emergency-number" v-model="profileForm.emergencyContactNumber" type="text" class="form-control" required>
                        </div>

                    </fieldset>

                    <button type="submit" class="btn btn-brand-gold">Save Profile</button>
                    <button v-if="profile" type="button" class="btn btn-outline-secondary" @click="cancelEdit">Cancel</button>
                </form>
                <p v-if="profileMessage" role="alert" class="alert alert-danger mt-3">{{ profileMessage }}</p>
            </section>

            <section v-if="profile && !editingProfile">
                <h2 class="h4 mb-3">My Profile</h2>
                <dl class="row">
                    <dt class="col-sm-3">Contact Number</dt>
                    <dd class="col-sm-9">{{ profile.contactNumber }}</dd>
                    <dt class="col-sm-3">Age</dt>
                    <dd class="col-sm-9">{{ profile.age }}</dd>
                    <dt class="col-sm-3">Gender</dt>
                    <dd class="col-sm-9">{{ profile.gender }}</dd>
                    <dt class="col-sm-3">Address</dt>
                    <dd class="col-sm-9">{{ profile.address }}</dd>
                    <dt class="col-sm-3">Medical Conditions</dt>
                    <dd class="col-sm-9">{{ profile.medicalConditions || "None" }}</dd>
                    <dt class="col-sm-3">Emergency Contact</dt>
                    <dd class="col-sm-9">{{ profile.emergencyContactName }} ({{ profile.emergencyContactNumber }})</dd>
                </dl>
                <button type="button" class="btn btn-outline-secondary btn-sm mb-4" @click="startEdit">Edit Profile</button>

                <h2 class="h4 mb-3">Available Treks</h2>
                <p v-if="bookingMessage" role="alert" class="alert" :class="bookingSuccess ? 'alert-success' : 'alert-danger'">
                    {{ bookingMessage }}
                </p>

                <p><router-link to="/user-bookings" class="btn btn-outline-secondary btn-sm">View My Bookings</router-link></p>
                <br>
                
                <search class="d-flex flex-wrap gap-3 align-items-end mb-3">
                    <div>
                        <label for="filter-location" class="form-label">Filter by location</label>
                        <input id="filter-location" v-model="locationFilter" type="text" class="form-control">
                    </div>
                    <div>
                        <label for="filter-duration" class="form-label">Filter by duration</label>
                        <input id="filter-duration" v-model="durationFilter" type="text" class="form-control">
                    </div>
                    <div>
                        <label for="filter-difficulty" class="form-label">Filter by difficulty</label>
                        <select id="filter-difficulty" v-model="difficultyFilter" class="form-select">
                            <option value="">All difficulties</option>
                            <option value="Easy">Easy</option>
                            <option value="Moderate">Moderate</option>
                            <option value="Difficult">Difficult</option>
                        </select>
                    </div>
                </search>

                <div v-if="filteredTreks.length > 0" class="table-responsive">
                    <table class="table table-striped table-hover align-middle">
                        <caption>Treks currently open for booking</caption>

                        <thead>
                            <tr>
                                <th scope="col">Name</th>
                                <th scope="col">Location</th>
                                <th scope="col">Duration</th>
                                <th scope="col">Difficulty</th>
                                <th scope="col">Slots Left</th>
                                <th scope="col">Staff</th>
                                <th scope="col">Action</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-for="trek in filteredTreks" :key="trek.id">
                                <td>{{ trek.name }}</td>
                                <td>{{ trek.location }}</td>
                                <td>{{ trek.duration }}</td>
                                <td>{{ trek.difficulty }}</td>
                                <td>{{ trek.slots }}</td>
                                <td>{{ trek.staffName }}</td>
                                <td>
                                    <button v-if="!isBooked(trek.id)" type="button" class="btn btn-sm btn-brand-gold" :disabled="trek.slots <= 0" @click="bookTrek(trek)">
                                        {{ trek.slots <= 0 ? "Full" : "Book" }}
                                    </button>
                                    <span v-else class="badge badge-brand-active">Booked</span>
                                </td>
                            </tr>
                        </tbody>

                    </table>
                </div>

                <p v-else>No treks match your search right now.</p>
            </section>
        </template>
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
            profile: null,
            editingProfile: false,
            profileForm: {
                contactNumber: "", age: "", gender: "", address: "",
                medicalConditions: "", emergencyContactName: "", emergencyContactNumber: ""
            },
            profileMessage: null,

            activeTreks: [],
            bookedTrekIds: [],
            bookingMessage: null,
            bookingSuccess: false,

            locationFilter: "",
            durationFilter: "",
            difficultyFilter: ""
        };
    },

    computed: {
        isBlacklisted() {
            return this.user.status !== "Active";
        },

        filteredTreks() {
            return this.activeTreks.filter(trek => {
                const matchesLocation = trek.location
                    .toLowerCase()
                    .includes(this.locationFilter.trim().toLowerCase());
                const matchesDuration = trek.duration
                    .toLowerCase()
                    .includes(this.durationFilter.trim().toLowerCase());
                const matchesDifficulty = !this.difficultyFilter || trek.difficulty === this.difficultyFilter;
                return matchesLocation && matchesDuration && matchesDifficulty;
            });
        }
    },

    mounted() {
        this.user = JSON.parse(localStorage.getItem("user"));
        this.fetchProfile();
        this.fetchTreks();
        this.fetchMyBookings();
    },

    methods: {
        async fetchProfile() {
            try {
                const response = await apiFetch(`/user/${this.user.id}/profile`);
                const data = await response.json();

                if (response.ok) {
                    this.profile = data.profile ? {
                        contactNumber: data.profile.contact_number,
                        age: data.profile.age,
                        gender: data.profile.gender,
                        address: data.profile.address,
                        medicalConditions: data.profile.medical_conditions,
                        emergencyContactName: data.profile.emergency_contact_name,
                        emergencyContactNumber: data.profile.emergency_contact_number
                    } : null;
                } else {
                    console.error("Failed to fetch profile:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching profile:", error);
            }
        },

        startEdit() {
            this.profileForm = this.profile ? { ...this.profile } : {
                contactNumber: "", age: "", gender: "", address: "",
                medicalConditions: "", emergencyContactName: "", emergencyContactNumber: ""
            };
            this.editingProfile = true;
        },

        cancelEdit() {
            this.editingProfile = false;
            this.profileMessage = null;
        },

        async saveProfile() {
            try {
                const response = await apiFetch("/user/profile", {
                    method: "POST",
                    body: JSON.stringify({
                        contact_number: this.profileForm.contactNumber,
                        age: this.profileForm.age,
                        gender: this.profileForm.gender,
                        address: this.profileForm.address,
                        medical_conditions: this.profileForm.medicalConditions,
                        emergency_contact_name: this.profileForm.emergencyContactName,
                        emergency_contact_number: this.profileForm.emergencyContactNumber
                    })
                });
                const data = await response.json();

                if (response.ok) {
                    this.profile = { ...this.profileForm };
                    this.editingProfile = false;
                    this.profileMessage = null;
                } else {
                    this.profileMessage = data.info || "Failed to save profile";
                    console.error("Failed to save profile:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error saving profile:", error);
            }
        },

        async fetchTreks() {
            try {
                const response = await apiFetch("/trek/all");
                const data = await response.json();

                if (response.ok) {
                    this.activeTreks = data.treks
                        .filter(trek => trek.status === "Active")
                        .map(trek => ({
                            id: trek.id,
                            name: trek.name,
                            location: trek.location,
                            duration: trek.duration,
                            difficulty: trek.difficulty,
                            slots: trek.slots,
                            staffName: trek.staff_name,
                            stage: trek.stage,
                            status: trek.status
                        }));
                } else {
                    console.error("Failed to fetch treks:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching treks:", error);
            }
        },

        async fetchMyBookings() {
            try {
                const response = await apiFetch(`/user/${this.user.id}/bookings`);
                const data = await response.json();

                if (response.ok) {
                    this.bookedTrekIds = data.bookings
                        .filter(booking => booking.status === "Booked")
                        .map(booking => booking.trek_id);
                } else {
                    console.error("Failed to fetch bookings:", response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching bookings:", error);
            }
        },

        isBooked(trekId) {
            return this.bookedTrekIds.includes(trekId);
        },

        async bookTrek(trek) {
            try {
                const response = await apiFetch(`/trek/${trek.id}/book`, {
                    method: "POST"
                });
                const data = await response.json();

                this.bookingSuccess = response.ok;
                if (response.ok) {
                    this.bookedTrekIds.push(trek.id);
                    trek.slots -= 1;
                    this.bookingMessage = data.booking_info;
                } else {
                    this.bookingMessage = data.booking_info || "Failed to book trek";
                    console.error(`Failed to book Trek ID ${trek.id}:`, response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error booking trek:", error);
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

.search-input {
    max-width: 320px;
}
</style>
