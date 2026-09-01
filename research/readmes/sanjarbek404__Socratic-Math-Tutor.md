# 📚 Socratic Math Tutor

<div align="center">

A compassionate, patient AI-powered math tutoring application that guides you through complex problems step-by-step using the Socratic method. Learn mathematics through guided discovery, not just answers.

[![React](https://img.shields.io/badge/React-19.0.0-61DAFB?logo=react&logoColor=white)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.2-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4.1-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini%203.1%20Pro-API-4285F4?logo=google&logoColor=white)](https://ai.google.dev)

**Author:** [Sanjarbek Otabekov](https://github.com/sanjarbek404)

[Features](#-features) • [Tech Stack](#-tech-stack) • [Getting Started](#-getting-started) • [Development](#-development)

</div>

---

## 🎯 Overview

Socratic Math Tutor is a web-based interactive mathematics tutoring application that leverages Google's Gemini API to provide intelligent, step-by-step guidance through mathematical problems. Instead of providing direct answers, it uses the Socratic method to help students understand the underlying concepts and arrive at solutions independently.

### Why Socratic Method?

The Socratic method is a proven educational technique where the tutor asks carefully chosen questions to guide the learner toward understanding. This approach:
- Builds deep comprehension rather than surface-level memorization
- Develops problem-solving skills and mathematical intuition
- Boosts confidence through guided discovery
- Encourages independent thinking

---

## ✨ Features

### 🖼️ **Image Recognition**
- Upload photos of math problems directly
- OCR-enabled problem extraction
- Support for handwritten and printed problems

### 💬 **Intelligent Chat Interface**
- Real-time conversational tutoring
- Socratic guidance system that breaks down complex problems
- Step-by-step problem decomposition
- Warm, encouraging communication style

### 📐 **Advanced Math Support**
- Native LaTeX rendering for mathematical expressions
- Support for calculus, algebra, trigonometry, and more
- Proper mathematical notation and formatting

### 🎨 **Modern User Interface**
- Responsive design that works on desktop and tablets
- Smooth animations and transitions
- Dark/Light theme support
- Clean, minimalist aesthetic
- Accessibility-first component design

### ⚡ **Real-time Processing**
- Instant response to queries
- Fast image processing
- Optimized for speed with Vite

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend Framework** | React | 19.0.0 |
| **Language** | TypeScript | ~5.8.2 |
| **Build Tool** | Vite | 6.2.0 |
| **Styling** | TailwindCSS | 4.1.14 |
| **UI Components** | shadcn/ui + Base UI | - |
| **Math Rendering** | KaTeX | 0.16.45 |
| **Markdown** | react-markdown + remark-math | - |
| **Animations** | Motion | 12.38.0 |
| **API** | Google Gemini 3.1 Pro | Latest |
| **Notifications** | Sonner | 2.0.7 |
| **Icons** | Lucide React | 0.546.0 |
| **Utilities** | class-variance-authority, clsx | - |

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** >= 18.0.0
- **npm** >= 9.0.0 (or yarn/pnpm)
- **Google Gemini API Key** (get it from [Google AI Studio](https://aistudio.google.com/app/apikeys))

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sanjarbek404/socratic-math-tutor.git
cd socratic-math-tutor
```

### 2️⃣ Install Dependencies

```bash
npm install
```

### 3️⃣ Configure Environment Variables

Create a `.env.local` file in the project root:

```bash
cp .env.example .env.local  # if available
# Or create manually:
echo "GEMINI_API_KEY=your_api_key_here" > .env.local
```

Replace `your_api_key_here` with your actual Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikeys).

### 4️⃣ Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### 5️⃣ Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

---

## 📖 Usage

### Basic Workflow

1. **Ask a Question or Upload an Image**
   - Type your math question in the input field, or
   - Click the upload button to add a photo of a problem

2. **Receive Socratic Guidance**
   - The tutor analyzes your problem
   - Identifies the first logical step
   - Explains it clearly and asks you to try it

3. **Engage in Dialogue**
   - Answer questions about the tutors's guidance
   - Ask "why?" to understand underlying concepts
   - Move to the next step when ready

4. **Learn and Discover**
   - Gain deeper understanding through guided discovery
   - Build problem-solving skills
   - Develop mathematical intuition

### Example Topics Supported

- ✓ Calculus (Integration, Differentiation, Limits)
- ✓ Algebra (Equations, Functions, Polynomials)
- ✓ Trigonometry (Identities, Equations, Functions)
- ✓ Linear Algebra (Matrices, Vectors)
- ✓ Statistics & Probability
- ✓ Geometry & Coordinate Systems

---

## 🔧 Development

### Available Scripts

```bash
# Start development server with hot module replacement
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Type check without emitting
npm run lint

# Clean build artifacts
npm run clean
```

### Project Structure

```
socratic-math-tutor/
├── src/
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   │   ├── badge.tsx
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── scroll-area.tsx
│   │   │   ├── separator.tsx
│   │   │   └── sonner.tsx      # Toast notifications
│   │   ├── ImageUploader.tsx   # Image upload component
│   │   └── MathMessage.tsx     # Math-formatted messages with LaTeX
│   ├── services/
│   │   └── gemini.ts          # Gemini API service & Socratic logic
│   ├── lib/
│   │   └── utils.ts           # Utility functions
│   ├── App.tsx                # Main application component
│   ├── main.tsx               # React entry point
│   └── index.css              # Global styles
├── public/                     # Static assets
├── package.json               # Dependencies & scripts
├── tsconfig.json              # TypeScript configuration
├── vite.config.ts            # Vite configuration
├── components.json            # shadcn/ui config
└── README.md                  # This file
```

### Key Components

#### **App.tsx**
Main application component handling:
- Chat message state management
- User input handling
- Message sending and loading states
- Auto-scroll to latest messages
- Chat reset functionality

#### **gemini.ts**
Service layer for AI integration:
- Google Gemini API client setup
- Socratic method system prompt
- Message history management
- Image processing pipeline
- Error handling

#### **MathMessage.tsx**
Display component for messages:
- LaTeX math expression rendering using KaTeX
- Markdown formatting with react-markdown
- Code syntax highlighting
- Responsive text layout

#### **ImageUploader.tsx**
Image handling component:
- File selection and preview
- Base64 encoding for API transmission
- Clear/reset functionality
- Responsive button UI

---

## 🎨 Customization

### Modifying the Socratic Method Approach

Edit the system prompt in [src/services/gemini.ts](src/services/gemini.ts#L5):

```typescript
const SYSTEM_INSTRUCTION = `You are a compassionate, patient math tutor...`
```

Adjust the prompt to change:
- Teaching style and tone
- Problem-solving approach
- Subject matter focus
- Response length and depth

### Styling & Theme

The project uses TailwindCSS with custom theme configuration:

```bash
# Global styles
src/index.css

# Tailwind config
tailwind.config.js (if exists)
```

To customize colors, spacing, or typography, check your Tailwind configuration or use inline Tailwind classes.

---

## 🔐 Environment Configuration

Create a `.env.local` file with:

```env
# Required: Google Gemini API Key
GEMINI_API_KEY=sk-...your-key-here

# Optional: Development settings
VITE_API_ENDPOINT=http://localhost:3000
DISABLE_HMR=false  # Set to 'true' in constrained environments
```

**Never commit `.env.local` to version control!**

---

## 🚢 Building for Production

### Build the Project

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory with:
- Minified JavaScript and CSS
- Optimized image assets
- Source map generation
- Tree-shaking and code splitting

### Preview Production Build

```bash
npm run preview
```

This serves the production build locally for testing before deployment.

### Deployment

The `dist/` folder can be deployed to any static hosting service:

**Options:**
- Vercel (recommended for Next.js-like projects)
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Firebase Hosting
- Any standard web server

---

## 🤝 Contributing

Contributions are welcome! Here's how to help:

1. **Fork** the repository on [GitHub](https://github.com/sanjarbek404/socratic-math-tutor)
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Guidelines

- Follow existing code style and conventions
- Add comments for complex logic
- Update README if introducing new features
- Test thoroughly before submitting PR

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Sanjarbek Otabekov** - Creator and Project Lead
- **Google Gemini API** - AI backbone for tutoring
- **shadcn/ui** - Beautiful, accessible components
- **React & TypeScript** - Type-safe React development
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **KaTeX** - Professional math typesetting

---

## �‍💻 Author

**Sanjarbek Otabekov**
- 🔗 [GitHub](https://github.com/sanjarbek404)
- 📧 [Email](mailto:sanjarbekotabekov010@gmail.com)
- 💼 [LinkedIn](https://www.linkedin.com/in/sanjarbek-otabekov-0600733bb/)

---

## 📞 Support & Questions

Have questions or run into issues?

- 📧 **Email:** sanjarbekotabekov010@gmail.com
- 🐛 **Issues:** [GitHub Issues](https://github.com/sanjarbek404/socratic-math-tutor/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/sanjarbek404/socratic-math-tutor/discussions)

---

## 🎓 Educational Philosophy

This project is built on the principle that **understanding matters more than answers**. The Socratic method encourages:

- **Critical thinking** over rote memorization
- **Conceptual clarity** over procedural fluency
- **Independent discovery** over passive reception
- **Confidence building** through guided success

Join us in reimagining mathematics education! 🚀

---

<div align="center">

**Made with ❤️ for learners and educators**

Created by **Sanjarbek Otabekov** © 2026

⭐ If this project helped you, consider giving it a star!

</div>