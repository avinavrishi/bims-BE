# Frontend: OTP-based registration flow

Use this with Cursor (or any AI) to implement the registration UI that talks to the bims-BE OTP APIs.

## Backend API summary

Base URL: `{API_BASE}/api/v1/auth` (e.g. `http://localhost:8000/api/v1/auth`).

### Flow (3 steps)

1. **Request OTP** – user enters email only.
2. **Verify OTP** – user enters 6-digit OTP from email; backend returns a short-lived `registration_token`.
3. **Complete registration** – user sets password and display name (username); send request with `registration_token` in `Authorization` header.

---

## Endpoints

### 1. POST `/register/request-otp`

- **Request body:** `{ "email": "user@example.com" }`
- **Response (200):** `{ "message": "OTP sent to your email", "expires_in_minutes": 10 }`
- **Errors:**
  - `400`: "Email already registered"
  - `503`: "Failed to send OTP email. Check server SMTP configuration."

**Frontend:** On success, show a screen asking for the 6-digit OTP (e.g. input or 6 boxes). Optionally show “Resend OTP” and a countdown/timer for ~10 minutes.

---

### 2. POST `/register/verify-otp`

- **Request body:** `{ "email": "user@example.com", "otp": "123456" }`
- **Response (200):** `{ "registration_token": "<jwt>", "expires_in": 900 }` (expires_in in seconds)
- **Errors:**
  - `400`: "No OTP found for this email. Request one first."
  - `400`: "OTP already used. Request a new one."
  - `400`: "OTP expired. Please request a new one."
  - `400`: "Invalid OTP."

**Frontend:** Store `registration_token` (e.g. in memory or short-lived sessionStorage). Navigate to “Complete registration” step (password + display name). On “OTP expired” or “Invalid OTP”, show the message and offer “Resend OTP”.

---

### 3. POST `/register/resend-otp`

- **Request body:** `{ "email": "user@example.com" }`
- **Response (200):** `{ "message": "New OTP sent to your email", "expires_in_minutes": 10 }`
- **Errors:**
  - `400`: "Email already registered."
  - `503`: "Failed to send OTP email. Check server SMTP configuration."

**Frontend:** Call after “Request OTP” or when user hits “Resend OTP” (e.g. after “OTP expired”). Reuse the same “Enter OTP” UI; optionally reset timer to 10 minutes.

---

### 4. POST `/register/complete`

- **Headers:** `Authorization: Bearer <registration_token>` (from verify-otp response)
- **Request body:** `{ "password": "secret", "display_name": "MyUsername" }`
- **Response (201):** User object (e.g. `{ "id", "email", "username", "role", "status", "created_at", "updated_at" }`)
- **Errors:**
  - `401`: "Invalid or expired registration token. Verify OTP again."
  - `400`: "Email already registered." / "OTP expired or already used. Please verify OTP again."

**Frontend:** Only call when you have a valid `registration_token` from step 2. Collect password and display name (username), send with the token. On success, redirect to login or auto-login if you have a login endpoint that returns tokens.

---

## UI flow suggestion

1. **Step 1 – Email**
   - Single field: email.
   - Submit → call `POST /register/request-otp`.
   - On success → go to Step 2; show “Resend OTP” (calls `POST /register/resend-otp`) and a 10-minute countdown.

2. **Step 2 – OTP**
   - 6-digit OTP input (single field or 6 boxes).
   - Submit → call `POST /register/verify-otp` with same email + otp.
   - On success → save `registration_token`, go to Step 3.
   - On “OTP expired” or “Invalid OTP” → show message; “Resend OTP” → call resend, then stay on Step 2.

3. **Step 3 – Password & username**
   - Fields: password, confirm password, display name (username).
   - Submit → call `POST /register/complete` with `Authorization: Bearer <registration_token>` and body `{ password, display_name }`.
   - On success → redirect to login or dashboard.

Keep `email` in component state or URL so you can pass it to request-otp, verify-otp, and resend-otp. Store `registration_token` only for the completion request; do not use it as the main app auth token (use login to get access/refresh tokens).
