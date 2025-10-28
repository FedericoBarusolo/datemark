# Datemark

Datemark is a Chrome extension that automatically extracts events from web pages and seamlessly adds them to your Google Calendar.

By leveraging generative AI, Datemark intelligently scans any webpage for event information (title, date, time,
location), and allows you to review and edit these details before adding them to your Google Calendar in just a few
clicks.

## Features

- **Automatic Event Detection**: Extracts events and their details from any webpage text
- **Intelligent Parsing**: AI architecture to extract event names, dates, times, and locations
- **Edit Before Adding**: Review and modify event details before calendar insertion
- **Bulk Operations**: Select and add multiple events at once
- **Google Calendar Integration**: Direct insertion into your Google Calendar
- **Usage Tracking**: Built-in usage limits with Firestore tracking
- **Secure Authentication**: OAuth-based user authentication

## Architecture

### Frontend

- Chrome Extension built with JavaScript
- Handles DOM manipulation and event extraction
- Provides intuitive UI for event management
- Communicates with backend API for processing

### Backend

- Python-based API service
- Containerized with Docker
- Deployed on Google Cloud Run
- Handles event parsing and Google Calendar API integration
- Manages secrets via Google Cloud Secret Manager

### Database

- Google Firestore for user data and usage tracking
- Monitors API call limits per user

## Try Datemark

Install the Datemark Chrome extension directly from the Chrome Web Store:

🔗 **[Add to Chrome](https://chromewebstore.google.com/detail/datemark/aoldddfllaacoiihcnjhkhljoaoogabc?authuser=0&hl=it)** *(Chrome Web Store link)*

### Usage

1. Navigate to any webpage containing event information
2. Click the Datemark extension icon
3. Click on the "Extract Events" button
4. Allow Google authentication (for first access)
5. The extension will automatically scan and extract events 
6. Review the detected events in the popup 
7. Edit any details as needed (name, date, time, location)
8. Select one or multiple events 
9. Click "Add Events to Calendar" to insert into Google Calendar

### Usage Limits

Datemark implements usage tracking to ensure fair usage:

- Free tier: 50 event extractions per month
- Usage resets on the 1st of each month at 00:00 CEST
- Upgrade options possibly available in the future

## Acknowledgments

- Google Calendar API for calendar integration
- Chrome Extensions API for browser integration
- Google Cloud Platform for hosting infrastructure

## Support

For issues, questions, or suggestions, please open an issue on GitHub or contact us at infodatemark@gmail.com
