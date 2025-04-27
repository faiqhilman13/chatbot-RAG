# TNB Internal Agentic Chatbot

A modern, responsive web application for TNB employees to interact with AI agents for document processing, summarization, visualization, and data extraction.

## Features

- **Modern React UI** with responsive design
- **Collapsible sidebar** for easy navigation
- **Document Upload** with drag-and-drop interface
- **Three specialized AI agents**:
  - **Summarization Bot**: Condense documents and extract key points
  - **Visualization Bot**: Generate charts and graphs from data
  - **Extraction Bot**: Extract structured data from documents
- **TNB Brand Colors** and professional design
- **FAQ System** with searchable questions and answers

## Technology Stack

- React.js (bootstrapped with Vite)
- TailwindCSS for styling
- Framer Motion for animations
- React Router for navigation

## Getting Started

### Prerequisites

- Node.js 14.x or higher
- npm or yarn

### Installation

1. Clone the repository
```bash
git clone https://github.com/your-org/tnb-internal-agentic-chatbot.git
cd tnb-internal-agentic-chatbot
```

2. Install dependencies
```bash
npm install
# or
yarn
```

3. Start the development server
```bash
npm run dev
# or
yarn dev
```

4. Open your browser to `http://localhost:5173`

## Building for Production

```bash
npm run build
# or
yarn build
```

The build artifacts will be stored in the `dist/` directory.

## Project Structure

```
tnb-internal-agentic-chatbot/
├── public/              # Static files
├── src/                 # Source code
│   ├── assets/          # Images, fonts, etc.
│   ├── components/      # Reusable components
│   ├── layouts/         # Layout components
│   ├── pages/           # Page components
│   ├── utils/           # Utility functions
│   ├── App.jsx          # Main App component
│   ├── index.css        # Global styles
│   └── main.jsx         # Entry point
├── index.html           # HTML template
├── package.json         # Project dependencies
└── vite.config.js       # Vite configuration
```

## Security Notes

This application is designed for internal TNB use only. All document processing would occur on TNB's secure infrastructure in a production environment.

## License

This project is proprietary and confidential. Unauthorized copying, modification, distribution, or use is strictly prohibited. 