# 6G-MAS-Factory Frontend

This is the **Next.js 15** dashboard for the **6G-MAS-Factory** Multi-Agent System. It provides a modern, responsive UI for monitoring and managing the industrial IIoT factory agents.

## Features

- 📊 **Real-time Dashboard**: Live data from backend agents (PM, Energy, Cyber, Safety, PPE)
- 🔄 **Server Actions Integration**: Fetches data from backend APIs using Next.js Server Actions
- 📈 **VChart Visualizations**: Interactive charts and graphs
- 🎨 **Modern UI**: Built with Radix UI and Tailwind CSS
- 🌓 **Dark Mode**: Full dark mode support

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI Components**: Radix UI + shadcn/ui
- **Styling**: Tailwind CSS
- **Charts**: VChart (@visactor/react-vchart)
- **State Management**: Jotai
- **Package Manager**: pnpm

## Quick Start

### 1. Install Dependencies

```bash
pnpm install
# or
npm install
# or
yarn install
```

### 2. Configure Environment Variables

Create a `.env.local` file in the root directory:

```env
ORCHESTRATOR_URL=http://localhost:8000
PM_AGENT_URL=http://localhost:8001
ENERGY_AGENT_URL=http://localhost:8002
CYBER_AGENT_URL=http://localhost:8003
SAFETY_AGENT_URL=http://localhost:8004
PPE_AGENT_URL=http://localhost:8005
```

> You can copy from the example: `cp .env.local.example .env.local`

### 3. Start Development Server

```bash
pnpm dev
# or
npm run dev
# or
yarn dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Backend Integration

The frontend connects to the backend Multi-Agent System via **Next.js Server Actions**. 

### Server Actions

Server Actions are located in `src/app/actions/`:

- **`orchestrator.ts`**: Fetches system-wide state from the Orchestrator
  - `fetchSystemState()`: Returns alerts, decisions, and last_update
- **`agents.ts`**: Fetches data from individual agents
  - `fetchPMStatus()`: PM Agent status and predictions
  - `fetchEnergyStatus()`: Energy Agent status
  - `fetchCyberStatus()`: Cyber Security Agent status
  - `fetchSafetyStatus()`: Safety Agent status
  - `fetchPPEStatus()`: PPE Agent status
  - `fetchAllAgentStatuses()`: Fetches all agents at once

### Example Usage

See `src/components/backend-status-example.tsx` for a complete integration example:

```typescript
import { fetchSystemState } from "@/app/actions/orchestrator";
import { fetchPMStatus } from "@/app/actions/agents";

// In a Client Component
const data = await fetchSystemState();
const pmStatus = await fetchPMStatus();
```

### Type Definitions

TypeScript interfaces for backend data are in `src/types/agent.ts`:
- `SystemState`, `Alert`, `Decision`
- `PMStatus`, `EnergyStatus`, `CyberStatus`, etc.

## Pages

- **`/`** - Main Dashboard (System Overview)
- **`/maintenance`** - Maintenance History & Logs
- **`/machines`** - Machine Status Monitoring
- **`/PPE`** - PPE Compliance Tracking
- **`/backlog`** - Backlog & Incidents
- **`/sensitization`** - Sensitization Data

## Project Structure

```
Frontend/
├── src/
│   ├── app/
│   │   ├── actions/          # Server Actions (Backend API calls)
│   │   ├── (dashboard)/      # Dashboard pages
│   │   ├── maintenance/      # Maintenance page
│   │   ├── machines/         # Machines page
│   │   └── PPE/              # PPE page
│   ├── components/           # React components
│   │   ├── ui/               # shadcn/ui components
│   │   ├── chart-blocks/     # Chart components
│   │   └── nav/              # Navigation components
│   ├── types/                # TypeScript types
│   ├── data/                 # Static data (fallback)
│   ├── lib/                  # Utilities
│   └── style/                # Global styles
├── public/                   # Static assets
├── .env.local.example        # Environment variables example
└── package.json
```

## Running with Backend

To run the full system (Frontend + Backend), see the **[SETUP_GUIDE.md](../SETUP_GUIDE.md)** in the root directory.

### Prerequisites
- Backend services must be running (Orchestrator + Agents)
- MQTT Broker (Mosquitto) must be running
- `.env.local` must be configured with correct backend URLs

## Build for Production

```bash
pnpm build
pnpm start
```

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Radix UI](https://www.radix-ui.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [VChart Documentation](https://www.visactor.io/vchart)

## Deployment

The easiest way to deploy this Next.js app is using [Vercel](https://vercel.com/new):

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/ias_tech_challenge)

For other deployment options, see the [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying).

