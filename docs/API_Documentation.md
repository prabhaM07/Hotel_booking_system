# Hotel Booking System API Documentation

**Version:** 1.0.0

**Generated on:** 2025-11-15 19:02:43


---
Secure API with JWT Cookie-based Authentication
---


## `/user/register`

### POST: Register User

**Description:** 

**Tags:** Users


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/user/verify_email`

### POST: Verify Email

**Description:** 

**Tags:** Users


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/user/login`

### POST: Login

**Description:** 

**Tags:** Users


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/user/refresh`

### POST: Refresh Token

**Description:** Get new access token using refresh token from cookie

**Tags:** Users


**Responses:**

- `200` — Successful Response


---


## `/user/logout`

### POST: Logout

**Description:** Logout - Clears authentication cookies

**Tags:** Users


**Responses:**

- `200` — Successful Response


---


## `/user/forget-password`

### PUT: Forget User Password

**Description:** 

**Tags:** Users


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/user/me`

### GET: Get Current User Info

**Description:** 

**Tags:** Users


**Responses:**

- `200` — Successful Response


---


## `/user/users`

### GET: Get All Users

**Description:** Get all users - Protected endpoint (requires cookie or header token)

**Tags:** Users


**Responses:**

- `200` — Successful Response


---


## `/user/user/{user_id}`

### DELETE: Delete User By Id

**Description:** Delete user by ID - Protected endpoint

**Tags:** Users


**Parameters:**

- `user_id` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/user/profile/{user_id}`

### PUT: Update User Profile

**Description:** 

**Tags:** Users


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/user/view`

### GET: View Profile Image

**Description:** 

**Tags:** Users


**Responses:**

- `200` — Successful Response


---


## `/user/search`

### GET: Search Users

**Description:** 

**Tags:** Users


**Parameters:**

- `q` (query) — 

- `page` (query) — 

- `per_page` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/user/filter`

### GET: Filter Users

**Description:** 

**Tags:** Users


**Parameters:**

- `role_id` (query) — Filter by role ID

- `created_from` (query) — Filter users created on or after this datetime

- `created_to` (query) — Filter users created on or before this datetime


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/user/recent-activity`

### GET: Get Recent Activity

**Description:** 

**Tags:** Users


**Parameters:**

- `limit` (query) — 

- `user_id` (query) — 

- `exclude_self` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/floor/add`

### POST: Add Floor

**Description:** 

**Tags:** Floors


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/floor/delete`

### DELETE: Delete Floor

**Description:** 

**Tags:** Floors


**Parameters:**

- `floor_no` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/floor/get`

### GET: Get Floor

**Description:** 

**Tags:** Floors


**Parameters:**

- `floor_id` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/floor/list`

### GET: List Floors

**Description:** 

**Tags:** Floors


**Responses:**

- `200` — Successful Response


---


## `/floor/search`

### GET: Search Floors

**Description:** 

**Tags:** Floors


**Parameters:**

- `q` (query) — 

- `page` (query) — 

- `per_page` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/floor/filter`

### GET: Filter Floors

**Description:** 

**Tags:** Floors


**Parameters:**

- `floor_no` (query) — Filter by floor number

- `min_floor_no` (query) — Minimum floor number

- `max_floor_no` (query) — Maximum floor number

- `created_from` (query) — Filter from creation date

- `created_to` (query) — Filter to creation date


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/feature/add`

### POST: Add Feature

**Description:** 

**Tags:** Features


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/feature/update/image`

### POST: Update Feature Image

**Description:** 

**Tags:** Features


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/feature/delete`

### DELETE: Delete Feature

**Description:** 

**Tags:** Features


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/feature/get`

### GET: Get Feature

**Description:** 

**Tags:** Features


**Parameters:**

- `feature_id` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/feature/list`

### GET: List Feature

**Description:** 

**Tags:** Features


**Responses:**

- `200` — Successful Response


---


## `/feature/search`

### GET: Search Features

**Description:** 

**Tags:** Features


**Parameters:**

- `q` (query) — 

- `page` (query) — 

- `per_page` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/feature/filter`

### GET: Filter Features

**Description:** 

**Tags:** Features


**Parameters:**

- `created_from` (query) — Filter from creation date

- `created_to` (query) — Filter to creation date


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/bedtype/add`

### POST: Add Bed Type

**Description:** Create a new bed type

**Tags:** Bed Types


**Request Body Example:**


**Responses:**

- `201` — Successful Response

- `422` — Validation Error


---


## `/bedtype/delete`

### DELETE: Delete Bed Type

**Description:** Delete a bed type by name

**Tags:** Bed Types


**Parameters:**

- `bed_type_name` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/bedtype/get`

### GET: Get Bed Type

**Description:** Get a single bed type by ID

**Tags:** Bed Types


**Parameters:**

- `bed_type_id` (query) — ID of the bed type


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/bedtype/list`

### GET: List Bed Types

**Description:** Get all bed types with pagination

**Tags:** Bed Types


**Parameters:**

- `page` (query) — Page number

- `per_page` (query) — Items per page


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/bedtype/search`

### GET: Search Bed Types

**Description:** Search bed types with pagination

**Tags:** Bed Types


**Parameters:**

- `q` (query) — Search query

- `page` (query) — Page number

- `per_page` (query) — Items per page


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/bedtype/filter`

### GET: Filter Bedtypes

**Description:** Filter bed types with pagination and statistics

**Tags:** Bed Types


**Parameters:**

- `created_from` (query) — Filter records created after this date

- `created_to` (query) — Filter records created before this date

- `page` (query) — Page number

- `per_page` (query) — Items per page


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/bedtype/bulk-delete`

### DELETE: Bulk Delete Bed Types

**Description:** Delete multiple bed types at once

**Tags:** Bed Types


**Parameters:**

- `bed_type_ids` (query) — List of bed type IDs to delete


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/roomtype/add`

### POST: Add Room Type

**Description:** Add a new room type with images, bed types, and features

**Tags:** Room Types


**Request Body Example:**


**Responses:**

- `201` — Successful Response

- `422` — Validation Error


---


## `/roomtype/update/{room_type_id}`

### PUT: Update Room Type

**Description:** Update existing room type and its related associations

**Tags:** Room Types


**Parameters:**

- `room_type_id` (path) — 


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/roomtype/delete/{room_type_id}`

### DELETE: Delete Room Type

**Description:** Delete a room type and its associations

**Tags:** Room Types


**Parameters:**

- `room_type_id` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/roomtype/get/{room_type_id}`

### GET: Get Room Type

**Description:** Get a single room type with all related data

**Tags:** Room Types


**Parameters:**

- `room_type_id` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/roomtype/list`

### GET: List Room Types

**Description:** List all room types with pagination and optional relations

**Tags:** Room Types


**Parameters:**

- `page` (query) — Page number

- `per_page` (query) — Items per page

- `include_relations` (query) — Include bed types and features


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/roomtype/search`

### GET: Search Room Types

**Description:** Search room types with pagination

**Tags:** Room Types


**Parameters:**

- `q` (query) — Search query

- `page` (query) — Page number

- `per_page` (query) — Items per page


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/roomtype/filter`

### GET: Filter Room Types

**Description:** Filter room types with pagination and statistics

**Tags:** Room Types


**Parameters:**

- `min_room_size` (query) — Minimum size in BHK

- `max_room_size` (query) — Maximum size in BHK

- `min_base_price` (query) — Minimum base price

- `max_base_price` (query) — Maximum base price

- `min_adults` (query) — Minimum number of adults

- `max_adults` (query) — Maximum number of adults

- `min_children` (query) — Minimum number of children

- `max_children` (query) — Maximum number of children

- `created_from` (query) — Created after this date

- `created_to` (query) — Created before this date

- `page` (query) — Page number

- `per_page` (query) — Items per page


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/roomtype/bulk-delete`

### DELETE: Bulk Delete Room Types

**Description:** Delete multiple room types at once

**Tags:** Room Types


**Parameters:**

- `room_type_ids` (query) — List of room type IDs to delete


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/room/add`

### POST: Add Room

**Description:** Add a new room record

**Tags:** Rooms


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/room/update`

### POST: Update Room

**Description:** Update room details

**Tags:** Rooms


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/room/delete`

### DELETE: Delete Room

**Description:** Delete a room record

**Tags:** Rooms


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/room/filter`

### GET: Filter Room

**Description:** Filter rooms based on criteria

**Tags:** Rooms


**Parameters:**

- `room_no` (query) — 

- `status` (query) — 

- `created_from` (query) — 

- `created_to` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/room/search`

### GET: Search Rooms

**Description:** Search rooms with pagination

**Tags:** Rooms


**Parameters:**

- `q` (query) — Search query

- `page` (query) — Page number

- `per_page` (query) — Items per page


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/room/whole/filter`

### GET: Filter Advanced

**Description:** Advanced filtering with multiple criteria

**Tags:** Rooms


**Parameters:**

- `room_price` (query) — 

- `floor_no` (query) — 

- `min_room_size` (query) — Minimum size in BHK

- `max_room_size` (query) — Maximum size in BHK

- `no_of_child` (query) — 

- `no_of_adult` (query) — 

- `room_type_name` (query) — 

- `ratings` (query) — 

- `feature_ids` (query) — 

- `bed_type_ids` (query) — 

- `check_in` (query) — 

- `check_out` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/room/{room_id}`

### GET: Get Room By Id

**Description:** Get a specific room by ID

**Tags:** Rooms


**Parameters:**

- `room_id` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/room/`

### GET: Get All Rooms

**Description:** Get all rooms with pagination

**Tags:** Rooms


**Parameters:**

- `skip` (query) — 

- `limit` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/addon/add`

### POST: Add Addon

**Description:** 

**Tags:** Addons


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/addon/update/image`

### POST: Update Addon Image

**Description:** 

**Tags:** Addons


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/addon/update/details`

### POST: Update Addon Details

**Description:** 

**Tags:** Addons


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/addon/delete`

### DELETE: Delete Addon

**Description:** 

**Tags:** Addons


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/addon/get`

### GET: Get Addon

**Description:** 

**Tags:** Addons


**Parameters:**

- `addon_id` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/addon/search`

### GET: Search Rooms

**Description:** 

**Tags:** Addons


**Parameters:**

- `q` (query) — 

- `page` (query) — 

- `per_page` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/addon/filter`

### GET: Filter Addons

**Description:** 

**Tags:** Addons


**Parameters:**

- `base_price_min` (query) — Minimum base price

- `base_price_max` (query) — Maximum base price

- `created_from` (query) — Filter from creation date

- `created_to` (query) — Filter to creation date


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/booking/add`

### POST: Book Room

**Description:** Book a new room record

**Tags:** Bookings


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/booking/cancel`

### POST: Cancel Booking

**Description:** 

**Tags:** Bookings


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/booking/checkAvailability`

### POST: Availabile Date Of Room

**Description:** 

**Tags:** Bookings


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/booking/reschedule`

### POST: Reschdule Bookings

**Description:** 

**Tags:** Bookings


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/booking/search`

### GET: Search Bookings

**Description:** Search bookings with pagination and fallback to fuzzy search

**Tags:** Bookings


**Parameters:**

- `q` (query) — Search term

- `page` (query) — Page number

- `per_page` (query) — Items per page


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/booking/filter`

### GET: Filter Bookings

**Description:** Filter bookings with pagination

**Tags:** Bookings


**Parameters:**

- `user_id` (query) — Filter by user ID

- `room_id` (query) — Filter by room ID

- `booking_status` (query) — Filter by booking status

- `payment_status` (query) — Filter by payment status

- `check_in_from` (query) — Filter bookings with check-in on or after this date

- `check_in_to` (query) — Filter bookings with check-in on or before this date

- `check_out_from` (query) — Filter bookings with check-out on or after this date

- `check_out_to` (query) — Filter bookings with check-out on or before this date

- `min_total_amount` (query) — Minimum total booking amount

- `max_total_amount` (query) — Maximum total booking amount

- `created_from` (query) — Filter from creation datetime

- `created_to` (query) — Filter to creation datetime

- `page` (query) — Page number

- `per_page` (query) — Items per page


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/booking/list`

### GET: List Bookings

**Description:** List all bookings with pagination

**Tags:** Bookings


**Parameters:**

- `page` (query) — Page number

- `per_page` (query) — Items per page


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/General/Query/create`

### POST: Create Query

**Description:** 

**Tags:** Contact By General User


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/General/Query/response`

### PUT: Respond Query

**Description:** 

**Tags:** Contact By General User


**Parameters:**

- `query_id` (query) — 


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/General/Query/get`

### GET: Get All Queries

**Description:** 

**Tags:** Contact By General User


**Responses:**

- `200` — Successful Response


---


## `/Query/chat`

### GET: Open Chat Page

**Description:** 

**Tags:** Contact By Booked User


**Responses:**

- `200` — Successful Response


---


## `/Query/user/detail`

### GET: Get Cur User Detail

**Description:** 

**Tags:** Contact By Booked User


**Responses:**

- `200` — Successful Response


---


## `/Query/user/online`

### GET: Get Online Connection

**Description:** 

**Tags:** Contact By Booked User


**Responses:**

- `200` — Successful Response


---


## `/Query/history/{user_id}`

### GET: Get User Chat

**Description:** 

**Tags:** Contact By Booked User


**Parameters:**

- `user_id` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---

### DELETE: Del User Chat

**Description:** 

**Tags:** Contact By Booked User


**Parameters:**

- `user_id` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/Query/user/all`

### GET: Get All Users

**Description:** Get all users with their online status

**Tags:** Contact By Booked User


**Responses:**

- `200` — Successful Response


---


## `/Query/participants`

### GET: Get All Participants

**Description:** 

**Tags:** Contact By Booked User


**Responses:**

- `200` — Successful Response


---


## `/content_management/terms_conditions/update`

### PUT: Update Terms Conditions

**Description:** Update or insert Terms and Conditions in MongoDB content management collection.

**Tags:** Content Management


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/terms_conditions`

### GET: Get Terms Conditions

**Description:** Retrieve the latest Terms and Conditions document from MongoDB.

**Tags:** Content Management


**Responses:**

- `200` — Successful Response


---


## `/content_management/ask_terms`

### GET: Ask Terms

**Description:** 

**Tags:** Content Management


**Parameters:**

- `question` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/carousel/add`

### POST: Add Carousel Image

**Description:** 

**Tags:** Content Management


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/carousel/`

### GET: Get All Carousel Images

**Description:** 

**Tags:** Content Management


**Responses:**

- `200` — Successful Response


---


## `/content_management/carousel/update/{carousel_id}`

### PATCH: Update Carousel Image

**Description:** 

**Tags:** Content Management


**Parameters:**

- `carousel_id` (path) — 


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/carousel/delete/{carousel_id}`

### DELETE: Delete Carousel Image

**Description:** 

**Tags:** Content Management


**Parameters:**

- `carousel_id` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/management/add`

### POST: Add Management Member

**Description:** 

**Tags:** Content Management


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/management/`

### GET: Get All Management Members

**Description:** 

**Tags:** Content Management


**Responses:**

- `200` — Successful Response


---


## `/content_management/management/update/{member_id}`

### PATCH: Update Management Member

**Description:** 

**Tags:** Content Management


**Parameters:**

- `member_id` (path) — 


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/management/delete/{member_id}`

### DELETE: Delete Management Member

**Description:** 

**Tags:** Content Management


**Parameters:**

- `member_id` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/contact/add`

### POST: Add Contact Details

**Description:** 

**Tags:** Content Management


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/contact/`

### GET: Get All Contact Details

**Description:** 

**Tags:** Content Management


**Responses:**

- `200` — Successful Response


---


## `/content_management/contact/update/{contact_id}`

### PATCH: Update Contact Details

**Description:** 

**Tags:** Content Management


**Parameters:**

- `contact_id` (path) — 


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/contact/delete/{contact_id}`

### DELETE: Delete Contact Details

**Description:** 

**Tags:** Content Management


**Parameters:**

- `contact_id` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/founder/add`

### POST: Add Founder Info

**Description:** 

**Tags:** Content Management


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/founder/`

### GET: Get All Founders

**Description:** 

**Tags:** Content Management


**Responses:**

- `200` — Successful Response


---


## `/content_management/founder/update/{founder_id}`

### PATCH: Update Founder Info

**Description:** 

**Tags:** Content Management


**Parameters:**

- `founder_id` (path) — 


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/founder/delete/{founder_id}`

### DELETE: Delete Founder Info

**Description:** 

**Tags:** Content Management


**Parameters:**

- `founder_id` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/content_management/content-management/`

### GET: Get Content Management

**Description:** Retrieve the current website content configuration.

**Tags:** Content Management


**Responses:**

- `200` — Successful Response


---

### POST: Create Or Update Content Management

**Description:** Create or update the website content (only one document allowed).

**Tags:** Content Management


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---

### DELETE: Delete Content Management

**Description:** Delete the current website content (and logo file).

**Tags:** Content Management


**Responses:**

- `200` — Successful Response


---


## `/ratings_reviews/add`

### POST: Create Ratings Reviews

**Description:** 

**Tags:** Ratings Reviews


**Parameters:**

- `booking_id` (query) — 


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/ratings_reviews/{id}`

### GET: Get Ratings Reviews

**Description:** 

**Tags:** Ratings Reviews


**Parameters:**

- `ratings_reviews_id` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/ratings_reviews/delete`

### DELETE: Delete Ratings Reviews

**Description:** 

**Tags:** Ratings Reviews


**Parameters:**

- `id` (query) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/postgress/backup-restore/backup`

### POST: Create Backup

**Description:** FastAPI route to trigger database backup.

**Tags:** Postgress Backup Restore


**Responses:**

- `200` — Successful Response


---


## `/postgress/backup-restore/backup/download/{filename}`

### GET: Download Backup

**Description:** Download a specific backup file.

**Tags:** Postgress Backup Restore


**Parameters:**

- `filename` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/postgress/backup-restore/restore`

### POST: Restore Backup Route

**Description:** Upload a backup file and restore the database.

**Tags:** Postgress Backup Restore


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/mongo/backup-restore/backup`

### POST: Create Backup

**Description:** Trigger MongoDB backup and create a ZIP file.

**Tags:** Mongo Backup Restore


**Responses:**

- `200` — Successful Response


---


## `/mongo/backup-restore/backup/list`

### GET: List Backups Route

**Description:** List available MongoDB backup ZIP files.

**Tags:** Mongo Backup Restore


**Responses:**

- `200` — Successful Response


---


## `/mongo/backup-restore/restore`

### POST: Restore Backup Route

**Description:** Restore MongoDB from uploaded ZIP backup file.

**Tags:** Mongo Backup Restore


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/mongo/backup-restore/backup/{filename}`

### DELETE: Delete Backup

**Description:** Delete a specific backup ZIP file.

**Tags:** Mongo Backup Restore


**Parameters:**

- `filename` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/dashboard/analytics`

### GET: Analytics

**Description:** 

**Tags:** Dashboard


**Parameters:**

- `date_from` (query) — Filter analytics with date on or after this date

- `date_to` (query) — Filter bookings with check-out on or before this date


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/dashboard/cancelled_booking_analysis`

### GET: Plot Against Cancelled Booking

**Description:** Generate and save a professional bar plot comparing booked vs cancelled bookings.
Applies optional date filters and saves plot under /static/plots/.

**Tags:** Dashboard


**Parameters:**

- `date_from` (query) — Filter bookings created on or after this date

- `date_to` (query) — Filter bookings created on or before this date


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/dashboard/refund_revenue_loss_analysis`

### GET: Refund Revenue Loss Analysis

**Description:** 

**Tags:** Dashboard


**Parameters:**

- `date_from` (query) — Filter refunds created on or after this date

- `date_to` (query) — Filter refunds created on or before this date


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/dashboard/room_type`

### GET: Room Type Analytics

**Description:** 

**Tags:** Dashboard


**Parameters:**

- `date_from` (query) — Filter Bookings created on or after this date

- `date_to` (query) — Filter Bookings created on or before this date


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/dashboard/user`

### GET: User Analytics

**Description:** 

**Tags:** Dashboard


**Parameters:**

- `date_from` (query) — Filter Bookings created on or after this date

- `date_to` (query) — Filter Bookings created on or before this date


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/`

### GET: Read Root

**Description:** Root endpoint - API health check

**Tags:** Root


**Responses:**

- `200` — Successful Response


---


## `/health`

### GET: Health Check

**Description:** Health check endpoint

**Tags:** Root


**Responses:**

- `200` — Successful Response


---
