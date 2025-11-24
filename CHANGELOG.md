## 1.0.2 (2025-11-24)

### Refactor

- update manifest info to optimize extension indexing

## 1.0.1 (2025-11-21)

### Refactor

- **popup.js**: update query placeholders list

## 1.0.0 (2025-11-21)

### Feat

- **extension**: update the extension frontend to allow inserting a user query for filtering
- update backend agent to filter through user query
- **popup.js**: add location to created events

### Fix

- handle errors in filter_events_by_user_query by continuing without filtering

### Refactor

- add rate extension link to the frontend
- extract and use page html instead of inner text

## 0.2.0 (2025-11-14)

### Feat

- validate all events' dates before creation

## 0.1.0 (2025-11-13)

### Feat

- add quota handling through firestore database
- build application frontend
- build application backend
- first commit

### Refactor

- code cleanup and testing
