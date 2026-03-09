# Frontend Cursor Prompt: Creator onboarding, username, creator type & social verification

Use this prompt in the **frontend** repo (or frontend folder) to implement the following flows. The backend APIs are already in place; adjust the frontend to call them and guide the user through the correct steps.

---

## 1. Creator registration (no display name)

**Backend change:** Creator registration no longer accepts `display_name`. Only `email` and `password` are required.

- **Endpoint:** `POST /api/v1/auth/register`
- **Request body:**
  ```json
  {
    "email": "creator@example.com",
    "password": "securePassword123"
  }
  ```
- **Remove** any `display_name` (or “name”) field from the creator signup form. Do **not** send `display_name` in the register request.

---

## 2. First-time creator: ask for username before dashboard

When a **creator** user logs in, check if they have set a username. If not, show a **one-time username step** and do **not** show the main dashboard until they set it.

**How to know if username is missing:**

- After login you get tokens. Call `GET /api/v1/auth/me` (or `GET /api/v1/profiles/me`) with the access token.
- For creators, the response includes `username` (user) or `username` (on profile). If `username` is `null` or missing, the creator has not set it yet.

**Flow:**

1. Creator logs in → `POST /api/v1/auth/login` → store tokens.
2. Call `GET /api/v1/profiles/me` (or `GET /api/v1/auth/me`).
3. If `role` is creator and `username` is null/empty:
   - Show a **“Choose your username”** screen/modal (one-time).
   - Form: single field “Username” (required, min 2 characters).
   - On submit: `PATCH /api/v1/profiles/me/username` with body `{ "username": "<value>" }`.
   - On success: store/refresh user state and then show the dashboard.
4. If `username` is already set: go straight to the dashboard.

**API details:**

- **Check profile/username:** `GET /api/v1/profiles/me`  
  - Response for creators can include `username` (from user). Alternatively use `GET /api/v1/auth/me` which returns user with `username`.
- **Set username (one-time):** `PATCH /api/v1/profiles/me/username`  
  - Body: `{ "username": "string" }`  
  - Allowed only for creators and only when current `username` is null. Returns `{ "username": "...", "message": "Username set" }`.

---

## 3. Add social account: creator type (face vs faceless) and face form

When the creator wants to **add a social account**, first ask whether they are a **face** or **faceless** creator. If **face**, show the extra form and submit creator type + face details; then run the existing “add social account” (verification) flow.

**Step 1 – Creator type**

- If creator has **not** set creator type yet, show:
  - “Are you a face creator or faceless creator?” (e.g. two options: **Face** / **Faceless**).
- If they choose **Face**, show the **face creator form** (Step 2).  
- If they choose **Faceless**, call the API to set creator type and then go to “Add social account” (Step 3).

**Step 2 – Face creator form (only when they choose Face)**

Fields (all optional for the form, but you can require what makes sense in UI):

- Name  
- Category  
- Reel price  
- Story price  
- Reel / story price (combined)  
- State  
- City  
- Language  

Submit via:

- **Endpoint:** `PATCH /api/v1/profiles/me/creator-type`
- **Body (face):**
  ```json
  {
    "creator_type": "FACE",
    "name": "...",
    "category": "...",
    "reel_price": 10.5,
    "story_price": 5.0,
    "reel_story_price": 15.0,
    "state": "...",
    "city": "...",
    "language": "..."
  }
  ```
- **Body (faceless):**
  ```json
  {
    "creator_type": "FACELESS"
  }
  ```

**Step 3 – Add social account (existing verification flow)**

After creator type (and face form, if applicable) is saved:

1. User chooses platform (e.g. Instagram, YouTube) and enters **username/handle**.
2. **Initiate verification:** `POST /api/v1/creator/social/accounts/verify/initiate`  
   - Body: `{ "platform": "INSTAGRAM" | "YOUTUBE" | "TIKTOK", "username": "handle" }`  
   - Response: `verification_id`, `verification_code`, `platform`, `username`, `expires_at`, `message`.
3. Show the **verification code** and instructions: “Add this code to your [platform] bio/description and click Continue.”
4. **Complete verification:** `POST /api/v1/creator/social/accounts/verify/complete`  
   - Body: `{ "verification_id": "<id from step 2>" }`.
5. **YouTube:** Response will already have final status (VERIFIED / FAILED / ERROR). Show success or failure.
6. **Instagram:** Response status will be PENDING (worker will verify in background). Poll status until terminal state:
   - **Endpoint:** `GET /api/v1/creator/social/accounts/verify/status/{verification_id}`  
   - Poll until `status` is one of: `VERIFIED`, `FAILED`, `ERROR`, `EXPIRED`. Then show success or failure.
7. On **VERIFIED**, the backend has already created the social account; the creator can see it in “My social accounts” (e.g. `GET /api/v1/creator/social/accounts`).

**Optional – Get creator type before showing the form**

- **Endpoint:** `GET /api/v1/profiles/me/creator-type`  
- Response: `creator_type` (FACE | FACELESS | null), plus face fields if FACE.  
- If `creator_type` is already set, you can skip the “face vs faceless” question and, for “Add social account”, go straight to Step 3 (or prefill the face form for editing if needed).

---

## 4. API summary (base URL e.g. `/api/v1`)

| Purpose | Method | Endpoint | Body / notes |
|--------|--------|----------|--------------|
| Creator register | POST | `/auth/register` | `{ "email", "password" }` — no display_name |
| Login | POST | `/auth/login` | `{ "email", "password" }` |
| Current user | GET | `/auth/me` | Returns user including `username` (null if not set) |
| My profile (creator) | GET | `/profiles/me` | Includes `username`, `creator_type`, `creator_face_details` for creators |
| Set username (one-time) | PATCH | `/profiles/me/username` | `{ "username": "string" }` |
| Get creator type | GET | `/profiles/me/creator-type` | Returns creator_type + face fields |
| Set creator type (+ face form) | PATCH | `/profiles/me/creator-type` | `{ "creator_type": "FACE"|"FACELESS", ...face fields }` |
| Start social verification | POST | `/creator/social/accounts/verify/initiate` | `{ "platform", "username" }` |
| Complete social verification | POST | `/creator/social/accounts/verify/complete` | `{ "verification_id" }` |
| Verification status | GET | `/creator/social/accounts/verify/status/{verification_id}` | Poll for Instagram |
| My social accounts | GET | `/creator/social/accounts` | List connected accounts |

---

## 5. Required frontend changes (checklist)

- [ ] **Registration:** Remove `display_name` from creator signup; send only `email` and `password` to `POST /auth/register`.
- [ ] **First login (creators):** After login, if role is creator and `username` is null, show one-time “Choose your username” screen; call `PATCH /profiles/me/username`; then allow access to dashboard.
- [ ] **Add social account flow:** Before starting verification, if creator type is not set, ask “Face or Faceless?”; if Face, show face form and call `PATCH /profiles/me/creator-type`; then run existing initiate → show code → complete → poll status (Instagram) or show result (YouTube).
- [ ] **Creator type / face form:** Reuse or create form for: name, category, reel price, story price, reel/story price, state, city, language; submit with `creator_type: "FACE"`. For “Faceless” submit only `creator_type: "FACELESS"`.
- [ ] **Verification:** Keep existing verification UI; ensure Instagram uses polling on `GET /creator/social/accounts/verify/status/{verification_id}` until status is VERIFIED/FAILED/ERROR/EXPIRED.

Use this document as the single source of truth when implementing or adjusting the frontend for creator onboarding, username, creator type, and social account verification.
