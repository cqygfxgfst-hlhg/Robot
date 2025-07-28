# PathOn AI - Robotics Policy Training Job Manager

A comprehensive machine learning training job management system that orchestrates AI model training workflows using AWS ECS, Modal, and Supabase.

## 🎦Demo

[Watch Demo Video](https://youtu.be/2Vr293b0XF0)

[Source Code](https://github.com/cqygfxgfst-hlhg/Robot)



## 🏹Core Features

### Job Creation

- Intuitive form for creating training jobs
- Parameter validation and JSON formatting
- Real-time feedback and error handling
- Responsive Dashboard: Modern, responsive UI built with Next.js and Tailwind CSS

### Dashboard

- Real-time job status updates
- Comprehensive job information display
- Retry functionality for failed jobs
- Error log viewing for debugging

### Training Pipeline

- Automated job queuing via SQS
- Distributed training on Modal
- Progress tracking and status updates
- Error handling and recovery

### User Management

- Secure authentication with Clerk
- User-specific job isolation
- Session management and security
- Authentication errors are centrally handled with meaningful API responses

### Deployment

- Dockerized FastAPI backend container
- Stateless API service deployed via AWS Fargate
- Application Load Balancer (ALB) for routing and health checks
- Environment-variable-based secure token injection (e.g., Modal auth)
- CloudWatch logging for container stdout/stderr
- Task role–based access to AWS services (SQS, Supabase)
- Separate long-running worker service consuming SQS queue
- Decoupled microservice architecture with queue-based messaging





## 🏠Architecture Decisions

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Training      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Modal)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Clerk Auth    │    │   AWS SQS       │    │   Supabase DB   │
│   (Identity)    │    │   Clerk Auth    │    │   AWS SQS       │
│                 │    │   Supabase DB   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Frontend:** Built with `Next.js` and `Tailwind CSS`, deployed on Vercel. The interface includes a task creation form and a real-time dashboard for job status updates. UI components are built using `shadcn/ui` for consistency and responsiveness.

**Authentication:** Implemented with `Clerk`, enabling secure login and user session management with minimal backend configuration. Clerk handles JWT issuance and user context.

**Backend API:** Powered by `FastAPI`, providing RESTful endpoints for job submission and status querying. Deployed via Docker to AWS ECS behind an HTTPS load balancer.

**Job Queue:** Integrated with `AWS SQS` to decouple job submission from processing. This allows asynchronous job execution and future scalability.

**Job Execution:** Implemented using `Modal`, a serverless platform for running training jobs. Modal simplifies infrastructure setup while supporting Python-based ML workflows.

**Database:** `Supabase` is used for storing job metadata, status updates, retry history, and user association. PostgreSQL’s relational structure helps maintain clear job-user relationships.

**Status Tracking:** The dashboard polls the backend to retrieve job statuses, which are updated asynchronously by the worker.

## 🏭Tech Stack

### Frontend
- **Framework**: Next.js 15.4.4 (Page Router)
- **Styling**: Tailwind CSS 4
- **UI Components**: shadcn/ui
- **Authentication**: Clerk
- **Language**: TypeScript

### Backend
- **Framework**: FastAPI
- **Deployment**: AWS ECS Fargate
- **Container**: Docker
- **Language**: Python 3.11

### Infrastructure
- **Queue**: AWS SQS

- **Database**: Supabase (PostgreSQL)

- **Training**: Modal Labs

- **Authentication**: Clerk

- **Monitoring**: CloudWatch Logs

  

## ⚙Installation & Setup

The backend API is already deployed on AWS ECS and is publicly accessible.
Therefore, you only need to run the frontend (Next.js) locally — it will communicate directly with the deployed backend without requiring local setup of the FastAPI server.

Although the backend is already deployed on AWS ECS, the repository includes the backend source code and deployment scripts for the following reasons:

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker
- AWS CLI configured
- Modal account
- Supabase project
- Clerk application

### Frontend Setup

create ".env.local" in "frontend" directory

```ts
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

#### Local Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Docker Deployment
```bash
cd backend
docker build -t pathon-backend .
docker run -p 8000:8000 --env-file .env pathon-backend
```

#### AWS ECS Deployment
```bash
cd backend
./deploy-to-ecs.sh
```

#### Backend (.env)
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-2
SQS_QUEUE_URL=https://sqs.us-east-2.amazonaws.com/your-account-id/your-queue-name

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key

# Clerk Configuration
CLERK_JWKS_URL=https://clerk.your-domain.com/.well-known/jwks.json
CLERK_API_KEY=your_clerk_api_key
CLERK_ISSUER=https://clerk.your-domain.com

# Modal Configuration
MODAL_TOKEN_ID=your_modal_token_id
MODAL_TOKEN_SECRET=your_modal_token_secret
```



## 📚Database Schema

### Jobs Table
```sql
create table public.jobs (
  id uuid not null,
  model_name text not null,
  dataset_url text not null,
  parameters jsonb null,
  status text not null default 'pending'::text,
  created_at timestamp with time zone null default now(),
  updated_at timestamp with time zone null default now(),
  completed_at timestamp with time zone null,
  failed_at timestamp with time zone null,
  sqs_message_id text null,
  retry_from uuid null,
  retry_count integer null default 0,
  error_log text null,
  user_id character varying(255) not null default 'anonymous'::character varying,
  constraint jobs_pkey primary key (id),
  constraint jobs_retry_from_fkey foreign KEY (retry_from) references jobs (id),
  constraint jobs_status_check check (
    (
      status = any (
        array[
          'pending'::text,
          'queued'::text,
          'running'::text,
          'completed'::text,
          'failed'::text
        ]
      )
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_jobs_status on public.jobs using btree (status) TABLESPACE pg_default;

create index IF not exists idx_jobs_created_at on public.jobs using btree (created_at desc) TABLESPACE pg_default;

create index IF not exists idx_jobs_retry_from on public.jobs using btree (retry_from) TABLESPACE pg_default;

create index IF not exists idx_jobs_retry_count on public.jobs using btree (retry_count) TABLESPACE pg_default;

create index IF not exists idx_jobs_user_id on public.jobs using btree (user_id) TABLESPACE pg_default;
```



##  🔌API Endpoints

### Jobs API
- `POST /jobs` - Create new training job
- `GET /jobs` - List user's jobs
- `GET /jobs/{job_id}` - Get job details
- `POST /jobs/{job_id}/retry` - Retry failed job
- `GET /jobs/{job_id}/error-log` - Get error logs

### Authentication
All endpoints above require valid Clerk JWT token in Authorization header.




## ⌨Author

**Zining Cen**
- GitHub: [cqygfxgfst-hlhg (iioo)](https://github.com/cqygfxgfst-hlhg)
- LinkedIn: [Zining Cen | LinkedIn](https://www.linkedin.com/in/zining-cen-8a1a2a304/)



## 🍃Acknowledgments

- [Modal Labs](https://modal.com) for cloud training infrastructure
- [Clerk](https://clerk.com) for authentication
- [Supabase](https://supabase.com) for database
- [shadcn/ui](https://ui.shadcn.com) for UI components





