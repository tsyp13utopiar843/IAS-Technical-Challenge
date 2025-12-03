# 6G-MAS Factory Frontend

This is the **Next.js 15** dashboard for the **6G-MAS-Factory** Multi-Agent System. It provides a modern, responsive UI for monitoring and managing the industrial IIoT factory agents.

## ✨ Features

- 📊 **Real-time Dashboard**: Live data from backend agents (PM, Energy, Cyber, Safety, PPE)
- 🔄 **Server Actions Integration**: Fetches data from backend APIs using Next.js Server Actions
- 📈 **VChart Visualizations**: Interactive charts and graphs for data analysis
- 🎨 **Modern UI**: Built with Radix UI and Tailwind CSS
- 🌓 **Dark Mode**: Full dark mode support with theme toggle
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- 🚀 **Production-Ready**: Configured for Netlify deployment

## 🛠️ Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI Components**: Radix UI + shadcn/ui
- **Styling**: Tailwind CSS
- **Charts**: VChart (@visactor/react-vchart)
- **State Management**: Jotai
- **Package Manager**: pnpm
- **Deployment**: Netlify

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+**
- **pnpm** (or npm/yarn)
- **Backend services running** (see [Backend/README.md](../Backend/README.md))

### Installation

```bash
# Install dependencies
pnpm install

# Create environment file
echo "NEXT_PUBLIC_API_GATEWAY=http://localhost:8080" > .env.local

# Start development server
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## ⚙️ Configuration

### Environment Variables

Create a `.env.local` file in the `Frontend` directory:

```env
# Backend API Gateway URL
# For local development:
NEXT_PUBLIC_API_GATEWAY=http://localhost:8080

# For production (Netlify):
# NEXT_PUBLIC_API_GATEWAY=https://mas-backend-production.up.railway.app
```

**Important**: 
- The `NEXT_PUBLIC_` prefix is required for Next.js to expose the variable to the browser
- For production, set this in Netlify's environment variables dashboard
- The gateway URL should point to your deployed backend's Nginx gateway (port 8080)

### API Gateway Architecture

The frontend uses a **single API gateway URL** (`NEXT_PUBLIC_API_GATEWAY`) to communicate with all backend services. The Nginx reverse proxy routes requests to the appropriate agent:

- `/api/orchestrator/*` → Orchestrator service
- `/api/pm/*` → PM Agent
- `/api/energy/*` → Energy Agent
- `/api/cyber/*` → Cyber Agent
- `/api/safety/*` → Safety Agent
- `/api/ppe/*` → PPE Agent

This eliminates the need for multiple environment variables and simplifies deployment.

## 🔌 Backend Integration

The frontend connects to the backend Multi-Agent System via **Next.js Server Actions**.

### Server Actions

Server Actions are located in `src/app/actions/`:

#### `orchestrator.ts`
- `fetchSystemState()`: Returns alerts, decisions, and last_update from the Orchestrator
- `fetchOrchestratorStatus()`: Returns orchestrator health status

#### `agents.ts`
- `fetchPMStatus()`: PM Agent status and predictions
- `fetchEnergyStatus()`: Energy Agent status
- `fetchCyberStatus()`: Cyber Security Agent status
- `fetchSafetyStatus()`: Safety Agent status
- `fetchPPEStatus()`: PPE Agent status
- `fetchAllAgentStatuses()`: Fetches all agents at once (parallel)
- `fetchPMHistory()`, `fetchEnergyHistory()`, etc.: Fetch prediction history

### Example Usage

```typescript
// In a Server Component
import { fetchSystemState } from "@/app/actions/orchestrator";
import { fetchPMStatus } from "@/app/actions/agents";

export default async function DashboardPage() {
  const systemState = await fetchSystemState();
  const pmStatus = await fetchPMStatus();
  
  return (
    <div>
      <h1>Alerts: {systemState?.alerts.length}</h1>
      <p>PM Health: {pmStatus?.health_score}%</p>
    </div>
  );
}
```

### Type Definitions

TypeScript interfaces for backend data are in `src/types/agent.ts`:
- `SystemState`, `Alert`, `Decision`
- `PMStatus`, `EnergyStatus`, `CyberStatus`, `SafetyStatus`, `PPEStatus`
- `HistoryResponse`

## 📄 Pages

- **`/`** - Main Dashboard (System Overview)
- **`/maintenance`** - Maintenance History & Logs
- **`/machines`** - Machine Status Monitoring
- **`/PPE`** - PPE Compliance Tracking
- **`/backlog`** - Backlog & Incidents
- **`/sensitization`** - Sensitization Data

## 📁 Project Structure

```
Frontend/
├── src/
│   ├── app/
│   │   ├── actions/              # Server Actions (Backend API calls)
│   │   │   ├── orchestrator.ts   # Orchestrator API
│   │   │   └── agents.ts         # Agent APIs
│   │   ├── (dashboard)/          # Dashboard pages
│   │   ├── maintenance/          # Maintenance page
│   │   ├── machines/             # Machines page
│   │   ├── PPE/                  # PPE page
│   │   ├── backlog/              # Backlog page
│   │   └── sensitization/        # Sensitization page
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── chart-blocks/         # Chart components
│   │   ├── nav/                  # Navigation components
│   │   └── backend-status-example.tsx
│   ├── types/
│   │   ├── agent.ts              # Backend data types
│   │   └── types.ts              # General types
│   ├── data/                     # Static data (fallback)
│   ├── lib/                      # Utilities
│   └── style/                    # Global styles
├── public/                       # Static assets
├── netlify.toml                  # Netlify configuration
├── .env.local.example            # Environment variables example
└── package.json
```

## 🏗️ Build for Production

```bash
# Build the application
pnpm build

# Start production server (for testing)
pnpm start
```

## 🌐 Deployment

### Netlify Deployment

The frontend is configured for deployment on Netlify:

1. **Connect GitHub Repository** to Netlify
2. **Configure Build Settings**:
   - **Base directory**: `Frontend`
   - **Build command**: `pnpm build` (or `npm run build`)
   - **Publish directory**: `.next`
3. **Set Environment Variables**:
   - `NEXT_PUBLIC_API_GATEWAY`: Your backend gateway URL (e.g., `https://mas-backend-production.up.railway.app`)
4. **Deploy!**

The `netlify.toml` file is already configured with the correct settings.

### Other Platforms

The frontend can also be deployed on:
- **Vercel**: Similar setup to Netlify
- **AWS Amplify**: Configure build settings
- **Self-hosted**: Use `pnpm build` and serve the `.next` directory

## 🔧 Development

### Running with Backend

To run the full system (Frontend + Backend):

1. **Start Backend Services** (see [Backend/README.md](../Backend/README.md)):
   ```bash
   # Using Docker Compose
   docker-compose up -d
   
   # Or manually start all services
   ```

2. **Start Frontend**:
   ```bash
   cd Frontend
   pnpm dev
   ```

3. **Access Dashboard**: [http://localhost:3000](http://localhost:3000)

### Prerequisites

- Backend services must be running (Orchestrator + Agents)
- MQTT Broker (Mosquitto) must be running
- `.env.local` must be configured with correct backend gateway URL

### Troubleshooting

**API Connection Failed**:
- Verify backend services are running: `curl http://localhost:8080/api/orchestrator/status`
- Check `.env.local` has correct `NEXT_PUBLIC_API_GATEWAY` value
- Check browser console (F12) for CORS errors

**No Data Loading**:
- Ensure Publisher is running to generate data
- Check backend logs for errors
- Verify MQTT broker is accessible

**Build Errors**:
- Clear `.next` directory: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && pnpm install`
- Check Node.js version: `node --version` (should be 18+)

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Radix UI](https://www.radix-ui.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [VChart Documentation](https://www.visactor.io/vchart)
- [shadcn/ui](https://ui.shadcn.com/)

## 🧪 Testing

Frontend testing can be added using:
- **Jest** or **Vitest** for unit tests
- **React Testing Library** for component tests
- **Playwright** or **Cypress** for E2E tests

(Testing setup not yet implemented)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Built with ❤️ for Industrial IIoT**

*Next.js 15 • TypeScript • Modern UI • Production-Ready*

