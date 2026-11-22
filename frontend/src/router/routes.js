import { createRouter, createWebHistory } from "vue-router";

import Home from "../views/Home.vue";


const routes = [
    {
        path: "/",
        component: Home
    },
    {
        path: "/register",
        component: () => import("../views/Register.vue")
    },
    {
        path: "/login",
        component: () => import("../views/Login.vue")
    },
    {
        path: "/admin",
        component: () => import("../views/Admin.vue"),
        meta: { requiresAuth: true, roles: ["admin"] }
    },
    {
        path: "/user",
        component: () => import("../views/User.vue"),
        meta: { requiresAuth: true, roles: ["user"] }
    },
    {
        path: "/staff",
        component: () => import("../views/Staff.vue"),
        meta: { requiresAuth: true, roles: ["staff"] }
    },
    {
        path: "/staff-management",
        component: () => import("../views/StaffManagement.vue"),
        meta: { requiresAuth: true, roles: ["admin"] }
    },
    {
        path: "/user-management",
        component: () => import("../views/UserManagement.vue"),
        meta: { requiresAuth: true, roles: ["admin"] }
    },
    {
        path: "/trek-management",
        component: () => import("../views/TrekManagement.vue"),
        meta: { requiresAuth: true, roles: ["admin"] }
    },
    {
        path: "/add-staff",
        component: () => import("../views/AddStaff.vue"),
        meta: { requiresAuth: true, roles: ["admin"] }
    },
    {
        path: "/add-trek",
        component: () => import("../views/AddTrek.vue"),
        meta: { requiresAuth: true, roles: ["admin"] }
    },
    {
        path: "/trek-bookings/:trekId",
        component: () => import("../views/TrekBookings.vue"),
        props: true,
        meta: { requiresAuth: true, roles: ["admin", "staff"] }
    },
    {
        path: "/user-bookings",
        component: () => import("../views/UserBookings.vue"),
        meta: { requiresAuth: true, roles: ["user"] }
    },
    {
        path: "/all-bookings",
        component: () => import("../views/AllBookings.vue"),
        meta: { requiresAuth: true, roles: ["admin"] }
    },
    {
        path: "/statistics",
        component: () => import("../views/Statistics.vue"),
        meta: { requiresAuth: true, roles: ["admin"] }
    },
    {
        path: "/reports",
        component: () => import("../views/Reports.vue"),
        meta: { requiresAuth: true, roles: ["admin"] }
    }
];


const router = createRouter({
    history: createWebHistory(),
    routes
});


router.beforeEach((to, from, next) => {
    const token = localStorage.getItem("token");
    const user = JSON.parse(localStorage.getItem("user") || "null");

    if (to.meta.requiresAuth && !token) {
        return next("/login");
    }

    if (to.meta.roles && user && !to.meta.roles.includes(user.role)) {
        return next("/");
    }

    next();
});

export default router;
