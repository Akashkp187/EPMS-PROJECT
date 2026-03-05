# EPMS – Roles: Admin, Manager, Employee

This document explains the difference between the three user roles in the Employee Performance Management System (EPMS).

---

## Overview

| Role      | Who uses it           | Main purpose                                      |
|-----------|------------------------|---------------------------------------------------|
| **Admin**   | HR / System administrators | Full system control: departments, training, KPIs, all employees |
| **Manager** | Team leads, supervisors   | Manage direct reports: reviews, 1:1s, view their team only     |
| **Employee**| Individual contributors   | Own goals, feedback, profile, view own reviews and meetings    |

---

## Admin

- **Access:** Full access to the application.
- **Can do:**
  - **Departments** – Create, edit, and manage departments. Only admins see the “Create department” action and can modify department list.
  - **Training** – View all training; create and manage training (if the app exposes create/edit to admin). All users can view and enroll in training; admin has management rights.
  - **KPI** – Define and manage KPIs and targets. KPI management pages are restricted to admins.
  - **Employees** – See all employees across the organization (no filter by manager).
  - **Reviews** – Create and manage performance reviews (same as Manager).
  - **1:1 Meetings** – Schedule and manage meetings (same as Manager).
  - **Goals, Feedback, Notifications, Analytics, Profile, Settings** – Same as other roles where applicable.
- **Nav:** Sees all links: Dashboard, Employees, Goals, Reviews, Feedback, 1:1 Meetings, **Departments**, **Training**, **KPI**, Analytics.

---

## Manager

- **Access:** Same as Admin **except** Departments, Training, and KPI management. Managers focus on people and performance of their direct reports.
- **Can do:**
  - **Employees** – See only **direct reports** (employees whose `manager_id` is the current user). Cannot see other teams.
  - **Reviews** – Create and conduct performance reviews (for their reports).
  - **1:1 Meetings** – Schedule and manage 1:1s with their reports.
  - **Goals, Feedback, Notifications, Analytics, Profile, Settings** – Same as Employee for their own data; can interact with reports where the app allows (e.g. giving feedback, viewing goals).
- **Cannot do:**
  - Create or edit **Departments** (admin only).
  - Manage **Training** (create/edit training; admin only). Can still view training and enroll like any user if the app allows.
  - Create or edit **KPIs** (admin only).
  - See employees who are not their direct reports.
- **Nav:** Sees Dashboard, Employees, Goals, Reviews, Feedback, 1:1 Meetings, Departments, Training, KPI, Analytics. Clicking Departments / Training / KPI may show read-only or redirect depending on implementation; only Admin can perform create/edit there.

---

## Employee

- **Access:** Own data and participation in reviews/meetings only. No access to org-wide management.
- **Can do:**
  - **Dashboard** – Own stats, goals, upcoming meetings, notifications.
  - **Goals** – Create, edit, and track own goals.
  - **Reviews** – View reviews about themselves; cannot create reviews for others.
  - **Feedback** – Give and receive 360° feedback.
  - **1:1 Meetings** – View and attend meetings they are part of (cannot create meetings for others).
  - **Training** – View training and enroll (if the app allows).
  - **Notifications** – View and manage own notifications.
  - **Profile & Settings** – Edit own profile, avatar, password.
  - **Analytics** – View organization-wide analytics if the app exposes it to all users.
- **Cannot do:**
  - Access **Employees** list to see other employees (or only a limited view if the app allows).
  - Create or manage **Departments**, **Training**, or **KPI**.
  - Create performance reviews or 1:1 meetings for others (manager-only).
- **Nav:** Sees Dashboard, Employees, Goals, Reviews, Feedback, 1:1 Meetings, Analytics. Does **not** see Departments, Training, or KPI in the nav.

---

## Summary

- **Admin** = Full control: departments, training, KPIs, and all employees.
- **Manager** = People management for **direct reports only**: reviews, 1:1s, employee list filtered to their team; no departments/KPI/training management.
- **Employee** = **Own** goals, feedback, profile, and participation in reviews/meetings/training; no management of others or org-wide settings.

In code, roles are enforced with:

- `@admin_required` – e.g. departments, KPI, training management.
- `@manager_required` – e.g. reviews, 1:1 meetings (and often implies admin can do it too via `is_manager()`).
- `current_user.can_manage_user(other)` – True for admin, or for manager when `other.manager_id == current_user.id`.
