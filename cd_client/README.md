# ChangeDetection.io Web Client

A beautiful web-based client for ChangeDetection.io that allows you to manage your watches with an intuitive interface.

## Features

- Connect to any ChangeDetection.io instance with API support
- View all your watches in a clean, organized sidebar
- Create new watches with custom title and tags
- View and edit watch settings
  - CSS/XPath filters
  - Request method & headers
  - Tags
- Check for changes manually
- View change history
- Preview the monitored page
- Search through your watches
- Responsive design for all device sizes

## Setup

1. Ensure you have a running ChangeDetection.io instance
2. Get your API key from the ChangeDetection.io settings page
3. Open the client in any modern web browser
4. Enter your instance URL and API key to connect

## Usage

- **Connect**: Enter your ChangeDetection.io instance URL and API key
- **Add Watch**: Click the + button in the sidebar to add a new watch
- **View Watch**: Click on any watch in the sidebar to see its details
- **Edit Settings**: Use the Settings tab to customize your watch configuration
- **Check Now**: Trigger an immediate check with the refresh button
- **View History**: See the history of changes in the History tab
- **Delete Watch**: Remove a watch with the delete button (requires confirmation)

## Technical Details

This client uses:
- HTML5, CSS3, and vanilla JavaScript
- Responsive design with CSS Grid and Flexbox
- Font Awesome icons
- The ChangeDetection.io REST API

## Security

- Your API key is stored in localStorage for convenience but never sent to any server other than your specified ChangeDetection.io instance
- All API requests are made directly from your browser to your instance
- The client runs entirely in the browser with no backend requirements

## Browser Support

Works in all modern browsers:
- Chrome/Edge
- Firefox
- Safari
- Opera

## License

MIT License