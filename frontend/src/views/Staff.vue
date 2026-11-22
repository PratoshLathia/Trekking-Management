<template>
    <Navbar />

    <main class="container py-4">
        <h1 class="mb-1">Staff Dashboard</h1>
        <p class="text-muted mb-4">Welcome, {{ staff.username }}!</p>

        <section v-if="isBlacklisted">
            <h2 class="h4 mb-3">My Profile</h2>
            <dl v-if="profile" class="row">
                <dt class="col-sm-3">Contact Number</dt>
                <dd class="col-sm-9">{{ profile.contactNumber }}</dd>
                <dt class="col-sm-3">Gender</dt>
                <dd class="col-sm-9">{{ profile.gender }}</dd>
                <dt class="col-sm-3">Address</dt>
                <dd class="col-sm-9">{{ profile.address }}</dd>
                <dt class="col-sm-3">Medical Certification</dt>
                <dd class="col-sm-9">{{ profile.medicalCertification }}</dd>
                <dt class="col-sm-3">Experience</dt>
                <dd class="col-sm-9">{{ profile.experience }}</dd>
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
                        <legend class="visually-hidden">Staff profile</legend>

                        <div class="mb-3">
                            <label for="staff-contact" class="form-label">Contact Number</label>
                            <input id="staff-contact" v-model="profileForm.contactNumber" type="text" class="form-control" required>
                        </div>

                        <div class="mb-3">
                            <label for="staff-gender" class="form-label">Gender</label>
                            <select id="staff-gender" v-model="profileForm.gender" class="form-select" required>
                                <option value="Male">Male</option>
                                <option value="Female">Female</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="staff-address" class="form-label">Address</label>
                            <input id="staff-address" v-model="profileForm.address" type="text" class="form-control" required>
                        </div>

                        <div class="mb-3">
                            <label for="staff-certification" class="form-label">Medical Certification</label>
                            <input id="staff-certification" v-model="profileForm.medicalCertification" type="text" class="form-control" required>
                        </div>

                        <div class="mb-3">
                            <label for="staff-experience" class="form-label">Experience</label>
                            <textarea id="staff-experience" v-model="profileForm.experience" class="form-control" required></textarea>
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
                    <dt class="col-sm-3">Gender</dt>
                    <dd class="col-sm-9">{{ profile.gender }}</dd>
                    <dt class="col-sm-3">Address</dt>
                    <dd class="col-sm-9">{{ profile.address }}</dd>
                    <dt class="col-sm-3">Medical Certification</dt>
                    <dd class="col-sm-9">{{ profile.medicalCertification }}</dd>
                    <dt class="col-sm-3">Experience</dt>
                    <dd class="col-sm-9">{{ profile.experience }}</dd>
                </dl>
                <button type="button" class="btn btn-outline-secondary btn-sm mb-4" @click="startEdit">Edit Profile</button>

                <h2 class="h4 mb-3">My Assigned Treks</h2>
                <p class="text-muted">Total assigned treks: {{ myTreks.length }}</p>

                <search class="mb-3 d-block">
                    <label for="trek-search" class="form-label">Search your treks by name or location</label>
                    <input id="trek-search" v-model="searchTerm" type="text" class="form-control search-input">
                </search>

                <p v-if="fetchTreksMessage" role="alert" class="alert alert-danger">{{ fetchTreksMessage }}</p>
                <p v-if="statusMessage" role="alert" class="alert alert-danger">{{ statusMessage }}</p>
                <p v-if="slotsMessage" role="alert" class="alert alert-danger">{{ slotsMessage }}</p>
                <p v-if="stageMessage" role="alert" class="alert alert-danger">{{ stageMessage }}</p>
                <p v-if="difficultyMessage" role="alert" class="alert alert-danger">{{ difficultyMessage }}</p>
                <p v-if="actionMessage" role="alert" class="alert alert-info">{{ actionMessage }}</p>

                <div v-if="filteredTreks.length > 0" class="table-responsive">
                    <table class="table table-striped table-hover align-middle">
                        <caption>Treks currently assigned to you</caption>

                        <thead>
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Name</th>
                                <th scope="col">Location</th>
                                <th scope="col">Duration</th>
                                <th scope="col">Difficulty</th>
                                <th scope="col">Slots</th>
                                <th scope="col">Trekkers</th>
                                <th scope="col">Status</th>
                                <th scope="col">Stage</th>
                                <th scope="col">Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-for="trek in filteredTreks" :key="trek.id">
                                <td>{{ trek.id }}</td>
                                <td>{{ trek.name }}</td>
                                <td>{{ trek.location }}</td>
                                <td>{{ trek.duration }}</td>
                                <td>
                                    <label :for="`difficulty-${trek.id}`" class="visually-hidden">Difficulty</label>
                                    <select :id="`difficulty-${trek.id}`" v-model="trek.difficulty" class="form-select form-select-sm" @change="toggleDifficulty(trek)">
                                        <option value="Easy">Easy</option>
                                        <option value="Moderate">Moderate</option>
                                        <option value="Difficult">Difficult</option>
                                    </select>
                                </td>

                                <td>
                                    <div class="input-group input-group-sm slots-input">
                                        <label :for="`slots-${trek.id}`" class="visually-hidden">Slots</label>
                                        <input :id="`slots-${trek.id}`" v-model.number="trek.slots" type="number" min="1" class="form-control">
                                        <button type="button" class="btn btn-outline-secondary" @click="toggleSlots(trek)">Save</button>
                                    </div>
                                </td>

                                <td>{{ trek.trekkersCount }}</td>

                                <td>
                                    <span class="badge mb-1" :class="trek.status === 'Active' ? 'badge-brand-active' : 'badge-brand-inactive'">
                                        {{ trek.status }}
                                    </span>
                                    <button type="button" class="btn btn-outline-secondary btn-sm d-block" @click="toggleStatus(trek)">
                                        {{ trek.status === "Active" ? "Close" : "Activate" }}
                                    </button>
                                </td>

                                <td>
                                    <label :for="`stage-${trek.id}`" class="visually-hidden">Stage</label>
                                    <select :id="`stage-${trek.id}`" v-model="trek.stage" class="form-select form-select-sm" @change="toggleStage(trek)">
                                        <option value="Upcoming">Upcoming</option>
                                        <option value="Started">Started</option>
                                        <option value="Ongoing">Ongoing</option>
                                        <option value="Completed">Completed</option>
                                    </select>
                                </td>

                                <td>
                                    <button type="button" class="btn btn-sm btn-brand-gold" @click="$router.push(`/trek-bookings/${trek.id}`)">View Bookings</button>
                                </td>
                            </tr>
                        </tbody>
                        
                    </table>
                </div>

                <p v-else-if="myTreks.length > 0">No treks match your search.</p>
                <p v-else>No treks assigned to you yet.</p>
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
            fetchTreksMessage: null,
            staff: [],
            myTreks: [],
            statusMessage: null,
            slotsMessage: null,
            stageMessage: null,
            difficultyMessage: null,
            actionMessage: null,

            profile: null,
            editingProfile: false,
            profileForm: {
                contactNumber: "", gender: "", address: "", medicalCertification: "", experience: ""
            },
            profileMessage: null,
            searchTerm: ""
        };
    },

    mounted() {
        this.staff = JSON.parse(localStorage.getItem("user"));
        this.fetchProfile();
        this.fetchMyTreks();
    },

    computed: {
        isBlacklisted() {
            return this.staff.status !== "Active";
        },
        filteredTreks() {
            const term = this.searchTerm.trim().toLowerCase();
            if (!term) return this.myTreks;

            return this.myTreks.filter(trek =>
                trek.name.toLowerCase().includes(term) ||
                trek.location.toLowerCase().includes(term)
            );
        }
    },

    methods: {
        async fetchProfile() {
            try {
                const response = await apiFetch(`/staff/${this.staff.id}/profile`);
                const data = await response.json();

                if (response.ok) {
                    this.profile = data.profile ? {
                        contactNumber: data.profile.contact_number,
                        gender: data.profile.gender,
                        address: data.profile.address,
                        medicalCertification: data.profile.medical_certification,
                        experience: data.profile.experience
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
                contactNumber: "", gender: "", address: "", medicalCertification: "", experience: ""
            };
            this.editingProfile = true;
        },

        cancelEdit() {
            this.editingProfile = false;
            this.profileMessage = null;
        },

        async saveProfile() {
            try {
                const response = await apiFetch("/staff/profile", {
                    method: "POST",
                    body: JSON.stringify({
                        contact_number: this.profileForm.contactNumber,
                        gender: this.profileForm.gender,
                        address: this.profileForm.address,
                        medical_certification: this.profileForm.medicalCertification,
                        experience: this.profileForm.experience
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

        async fetchMyTreks() {
            try {
                const response = await apiFetch(`/staff/${this.staff.id}/treks`);
                const data = await response.json();

                if (response.ok) {
                    this.myTreks = data.treks.map(trek => ({
                        id: trek.id,
                        name: trek.name,
                        location: trek.location,
                        slots: trek.slots,
                        duration: trek.duration,
                        difficulty: trek.difficulty,
                        status: trek.status,
                        stage: trek.stage,
                        trekkersCount: trek.trekkers_count
                    }));
                    this.fetchTreksMessage = null;
                } else {
                    this.fetchTreksMessage = data.info || "Failed to fetch treks";
                    console.error("Failed to fetch treks:", response.statusText, data);
                }
                
            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error("Error fetching treks:", error);
            }
        },

        async toggleStatus(trek) {
            const newStatus = trek.status === "Active" ? "Closed" : "Active";
            try {
                const response = await apiFetch(`/trek/${trek.id}/status`, {
                    method: "POST",
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await response.json();

                if (response.ok) {
                    this.statusMessage = null;
                    this.actionMessage = data.status_info;
                    await this.fetchMyTreks();
                } else {
                    this.statusMessage = data.status_info || "Failed to change status";
                    console.error(`Failed to change status for Trek ID ${trek.id}:`, response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error(`Error changing status for Trek ID ${trek.id}:`, error);
            }
        },

        async toggleSlots(trek) {
            try {
                const response = await apiFetch(`/trek/${trek.id}/slots`, {
                    method: "POST",
                    body: JSON.stringify({ slots: trek.slots })
                });
                const data = await response.json();

                if (response.ok) {
                    this.slotsMessage = null;
                    this.actionMessage = data.slots_info;
                    await this.fetchMyTreks();
                } else {
                    this.slotsMessage = data.slots_info || "Failed to change slots";
                    console.error(`Failed to change slots for Trek ID ${trek.id}:`, response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error(`Error changing slots for Trek ID ${trek.id}:`, error);
            }
        },

        async toggleStage(trek) {
            try {
                const response = await apiFetch(`/trek/${trek.id}/stage`, {
                    method: "POST",
                    body: JSON.stringify({ stage: trek.stage })
                });
                const data = await response.json();

                if (response.ok) {
                    this.stageMessage = null;
                    this.actionMessage = data.stage_info;
                    await this.fetchMyTreks();
                } else {
                    this.stageMessage = data.stage_info || "Failed to change stage";
                    console.error(`Failed to change stage for Trek ID ${trek.id}:`, response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error(`Error changing stage for Trek ID ${trek.id}:`, error);
            }
        },

        async toggleDifficulty(trek) {
            try {
                const response = await apiFetch(`/trek/${trek.id}/difficulty`, {
                    method: "POST",
                    body: JSON.stringify({ difficulty: trek.difficulty })
                });
                const data = await response.json();

                if (response.ok) {
                    this.difficultyMessage = null;
                    this.actionMessage = data.difficulty_info;
                    await this.fetchMyTreks();
                } else {
                    this.difficultyMessage = data.difficulty_info || "Failed to change difficulty";
                    console.error(`Failed to change difficulty for Trek ID ${trek.id}:`, response.statusText, data);
                }

            } catch (error) {
                alert("Unable to reach the server. Please try again.");
                console.error(`Error changing difficulty for Trek ID ${trek.id}:`, error);
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

.slots-input {
    min-width: 140px;
}

.search-input {
    max-width: 320px;
}
</style>
