<div align="right">
  <span>[<a href="./README.md">English</a>]<span>
  </span>[<a href="./README_CN.md">简体中文</a>]</span>
</div>  

<div align="center">

  <img src="./assets/logo.png" alt="ChatTutor" width="150" height="150" />

  <h1>ChatTutor</h1>

  <p>Visual and Interactive AI Tutor</p>
  
  <div align="center">
    <img src="https://img.shields.io/github/package-json/v/HugeCatLab/ChatTutor" alt="Version" />
    <img src="https://img.shields.io/github/license/HugeCatLab/ChatTutor" alt="License" />
    <img src="https://img.shields.io/github/stars/HugeCatLab/ChatTutor?style=social" alt="Stars" />
    <img src="https://img.shields.io/github/forks/HugeCatLab/ChatTutor?style=social" alt="Forks" />
    <img src="https://img.shields.io/github/last-commit/HugeCatLab/ChatTutor" alt="Last Commit" />
    <img src="https://img.shields.io/github/issues/HugeCatLab/ChatTutor" alt="Issues" />
  </div>
  
</div>

---

> [!NOTE]
>
> Online Website: ChatTutor is available at [https://chattutor.app](https://chattutor.app), please set your own API key and models in the settings. ([https://chattutor.app/settings](https://chattutor.app/settings))

ChatTutor is an AI teacher equipped with the ability to use an electronic whiteboard.

Traditional chatbots interact with users primarily through text, which is sufficient in most scenarios. However, with the development of LLM in recent years, more and more people are using AI to assist their learning. In a real-world classroom, teachers have many teaching tools—chalk, computers, blackboards, and other teaching aids—that help students better understand knowledge. But for a chatbot, text can convey very limited information, especially in STEM subjects.

ChatTutor effectively solves this problem by bringing all the teaching tools used in real-world educational scenarios to the forefront, allowing users to interact with them through electronic devices. We've empowered AI with the ability to use these tools, enabling AI to become a truly hands-on teacher.

## Features

##### Math Canvas
<table>
  <tr>
    <td>
      <img src="./assets/demo-math-1.png" alt="Math Canvas" width="100%" />
    </td>
    <td>
      <img src="./assets/demo-math-2.png" alt="Math Canvas" width="100%" />
    </td>
  </tr>
  <tr>
    <td>
      <img src="./assets/demo-math-3.png" alt="Math Canvas" width="100%" />
    </td>
    <td>
      <img src="./assets/demo-math-4.png" alt="Math Canvas" width="100%" />
    </td>
  </tr>
</table>

##### Mindmap
<table>
  <tr>
    <td>
      <img src="./assets/demo-mermaid-1.png" alt="Mindmap" width="100%" />
    </td>
    <td>
      <img src="./assets/demo-mermaid-2.png" alt="Mindmap" width="100%" />
    </td>
  </tr>
</table>

## Quick Start

<details><summary>Environment Variables</summary>

### Database Configuration
- `DATABASE_URL`: PostgreSQL connection string

### Server & Client
- `VITE_API_BASE_URL`: Base URL for the API server (e.g., `http://localhost:8002`)
- `CLINET_BASE_URL`: Base URL for the client application (e.g., `http://localhost:8001`)

### AI Configuration
- `MODEL_API_KEY`: Your API key for the AI service (e.g., `your_api_key_here`)
- `MODEL_BASE_URL`: Base URL for the AI service (optional, defaults to OpenAI)
- `AGENT_MODEL`: Model for the main agent that chats with users (e.g., `gpt-4`)
- `AGENT_MODEL_PROVIDER`: Model provider (options: refer to [Provider Enum](#provider-enum))
- `TITLE_MODEL`: Model for generating chat titles (optional, defaults to `AGENT_MODEL`)
- `TITLE_MODEL_PROVIDER`: Model provider for title generation (optional, defaults to `AGENT_MODEL_PROVIDER`, refer to [Provider Enum](#provider-enum))

#### Provider Enum
- OpenAI: `openai`
- Anthropic: `anthropic`
- DeepSeek: `deepseek`

### OSS Configuration
- `OSS_ENDPOINT`: OSS endpoint URL (if not set, image upload will be unavailable)
- `OSS_ACCESS_KEY`: OSS access key
- `OSS_SECRET_KEY`: OSS secret key
- `OSS_BUCKET`: OSS bucket name
- `OSS_REGION`: OSS region

</details>

<details><summary>Run with Docker</summary>

### Environment

> - Docker >= 24.0.0
> - Docker Compose >= 2.22.0

### Setup

```bash
git clone https://github.com/HugeCatLab/ChatTutor.git
cd ChatTutor
cp .env.example .env
```

### Run

```bash
cd docker
docker compose up -d
```
</details>

<details><summary>Run with Node & Bun</summary>

### Environment

> - Node.js >= 20
> - Bun >= 1.2
> - pnpm >= 9.1.0

### Setup

```bash
git clone https://github.com/HugeCatLab/ChatTutor.git
cd ChatTutor
pnpm i
```

### Development

```bash
pnpm dev
```

Or:

```bash
pnpm client:dev
pnpm web:dev
```

### Build

```bash
pnpm build
pnpm client:start
pnpm web:start
```

</details>


## Tech Stacks

- [Geogebra](https://www.geogebra.org/)
- [Vue](https://vuejs.org/)
- [Vite](https://vitejs.dev)
- [ElysiaJs](https://https://elysiajs.com/)
- [AI SDK](https://ai-sdk.dev/)

## Sponsors
Our sponsors are listed as follows (in no particular order):

- [AiHubMix](https://aihubmix.com/): Open model hub for AI.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=HugeCatLab/ChatTutor&type=date&legend=top-left)](https://www.star-history.com/#HugeCatLab/ChatTutor&type=date&legend=top-left)

---
**AGPL v3 License**

*Copyright (c) 2025 Acbox, All rights reserved.*