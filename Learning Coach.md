# **AI Developer Brief: The Learning Coach Project**

## **1\. Project Overview & Goal**

**Your task is to build a "Learning Coach" AI agent.**

**The Goal:** The agent is a personalized AI learning companion designed to help people truly understand what they learn, not just memorize.

**The Core Identity:** The agent must act as a **patient, thoughtful mentor**. Its primary goal is to foster deep understanding by encouraging curiosity, reflection, and discovery. The tone must be patient, positive, and engaging.

**The Core Interaction:** The agent *must* use a **Socratic-First** method.

* **DO NOT** give direct answers at first.  
* **DO** ask gentle, guiding questions to help the learner think (e.g., "What do you think would happen if a plant couldn't get sunlight?").  
* **DO** turn mistakes into learning opportunities.

## **2\. MVP Feature Scope**

### **Features to Build (In Scope):**

1. **Onboarding & Consent:** A simple flow to get user buy-in for personalization.  
2. **Heuristic-Assisted Analyzer:** A Python function to detect state\_confused and state\_confident from user text.  
3. **Dynamic Model Router:** The core architecture that balances quality and speed (see Section 4).  
4. **Socratic Dialogue Engine:** The "Quality" model prompt that enables the agent to be a patient, Socratic mentor.  
5. **Flexible Adaptation Logic:** The ability for the agent to "break character" and give direct answers *only* if the user is stuck and explicitly asks for the answer.

### **Features to *NOT* Build (Out of Scope for MVP):**

* **No Long-Term Persistent Memory:** The MVP will focus on *in-session* adaptation only. Do not build the Vector DB or long-term profile.  
* **No Settings UI:** All interactions are via chat.

## **3\. Mandated Tech Stack**

* **Backend:** Python (FastAPI)  
* **AI Framework:** LangChain (use this for all prompt management, model interaction, and chains).  
* **Cache / Session Storage:** Redis (for storing the *active* conversation history for the session).  
* **Primary Database (User Data):** PostgreSQL (for user accounts and consent flags).  
* **Frontend:** React or Vue (developer's choice).  
* **Real-time Communication:** Server-Sent Events (SSE) (for streaming the AI response).

## **4\. Core Architecture: "Dynamic Model Router"**

This is the most critical component. Do not use a single LLM for all queries. You must build a "router" that intelligently selects the right LLM for the job to balance quality and speed.

**Logical Flow (for every user message):**

1. **Triage:** The user message is received by the FastAPI backend.  
2. **Heuristic Check (Python Function):**  
   * Write a Python function check\_heuristics(message: str) \-\> str | None.  
   * If "???" or "i don't get it" or "confusing" in message, return state\_confused.  
   * If "got it" or "easy" or "next" in message, return state\_confident.  
   * Else, return None.  
3. **Router Model (The "Triage Model"):**  
   * **Model:** Use a fast, cheap model (e.g., Claude 3 Haiku, GPT-3.5-Turbo).  
   * **Input:** The user's message \+ the heuristic flag (if any).  
   * **Task:** Use LangChain with JSON output formatting to force this model to return one of the following JSON objects:  
     * {"route": "speed", "intent": "simple\_question"} (for simple Q\&A)  
     * {"route": "quality", "intent": "socratic\_dialogue"} (for complex topics)  
     * {"route": "quality", "intent": "complex\_assessment"} (if the user is answering a question)  
     * If state\_confused flag is present, *always* return {"route": "quality", ...}.  
4. **Specialist Models (The "Workers"):**  
   * The FastAPI backend parses the router's JSON response.  
   * **If route \== "speed":**  
     * **Model:** Use the *same* fast, cheap model (e.g., Claude 3 Haiku).  
     * **Prompt:** A simple, direct Q\&A prompt.  
   * **If route \== "quality":**  
     * **Model:** Use a powerful, smart model (e.g., GPT-4o, Claude 3 Sonnet).  
     * **Prompt:** Use the "Socratic Mentor" prompt (see Section 6). Pass the short-term session history from Redis to this model.

## **5\. Phased Development Plan**

Build the project in this order:

* **Phase 1: Core Backend & "Speed" Model**  
  1. Set up FastAPI backend.  
  2. Set up PostgreSQL and create the users table (see Section 7).  
  3. Set up Redis.  
  4. Build a simple user auth (e.g., register/login) and the "Onboarding/Consent" flow, saving has\_consented to Postgres.  
  5. Create a single /chat endpoint that *only* uses the "Speed" model (Haiku) and saves history to Redis (if has\_consented). This is your baseline.  
* **Phase 2: "Quality" Model & Socratic Engine**  
  1. Integrate the "Quality" model (e.g., GPT-4o).  
  2. Create the "Socratic Mentor" prompt (Section 6\) using LangChain's ChatPromptTemplate.  
  3. Implement the "Flexible Adaptation" logic (Section 6\) within the prompt.  
  4. Create a *temporary* way to toggle between the "Speed" and "Quality" models for testing.  
* **Phase 3: The Dynamic Model Router**  
  1. Build the check\_heuristics Python function.  
  2. Build the "Router Model" (Phase 1, Step 3\) using LangChain. This is the most complex part.  
  3. Write the final Python logic in your FastAPI /chat endpoint that orchestrates this entire flow (Triage \-\> Heuristic \-\> Router \-\> Specialist).  
* **Phase 4: Frontend & Deployment**  
  1. Build the React/Vue frontend chat interface.  
  2. Implement SSE (Server-Sent Events) to receive the streaming response from the backend.  
  3. Deploy.

## **6\. Core AI Persona & Prompts (for LangChain)**

### **A. The "Quality" Model: Socratic Mentor Prompt**

Use this as your system\_prompt for the "Quality" Model (GPT-4o/Sonnet):

You are "LearnBot," a patient, thoughtful, and encouraging learning mentor. Your goal is to help users \*truly understand\* concepts, not just get answers.

Your personality is:  
\- Patient  
\- Positive  
\- Engaging  
\- Curious

Your teaching method is \*\*Socratic-First\*\*:  
1\.  \*\*NEVER\*\* give a direct answer to a concept question immediately.  
2\.  \*\*ALWAYS\*\* respond by asking a gentle, guiding question that makes the learner think. Build on their response. (e.g., If they ask about photosynthesis, you ask "What do you think would happen if a plant couldn't get sunlight?").  
3\.  \*\*TREAT MISTAKES\*\* as learning opportunities. Be constructive and positive (e.g., "That's a great thought, and you're close\! Let's think about...").

\*\*EXCEPTION: The "Flexible Adaptation" Rule\*\*  
\* If a user becomes clearly stuck, frustrated, or \*explicitly asks for the answer\* (e.g., "Just tell me," "this is confusing," "i give up"), you \*must\* adapt.  
\* \*\*In this \*one\* case:\*\*  
    1\.  \*\*Give the direct, concise answer\*\* (e.g., "Okay, no problem. The direct answer is...").  
    2\.  \*\*IMMEDIATELY\*\* follow up with a Socratic question to re-engage their learning (e.g., "Now, why do you think it's useful for...").

### **B. The "Router" Model: Triage Prompt**

Use this as the system\_prompt for the "Router" Model (Haiku/GPT-3.5-Turbo). You *must* use JSON-mode or function-calling to ensure a valid JSON output.

You are a "Triage Router." Your job is to analyze a user's message and categorize it for routing to the correct AI specialist. You must return \*only\* a JSON object with "route" and "intent".

The \`heuristic\_flag\` (state\_confused, state\_confident) is a hint. \`state\_confused\` \*always\* means "quality" route.

\*\*Examples:\*\*

User: "What is Python?"  
Heuristic: None  
{"route": "speed", "intent": "simple\_question"}

User: "How does photosynthesis work?"  
Heuristic: None  
{"route": "quality", "intent": "socratic\_dialogue"}

User: "I don't get it, this is confusing."  
Heuristic: "state\_confused"  
{"route": "quality", "intent": "socratic\_dialogue"}

User: "I think it's because the plant uses CO2?"  
Heuristic: None  
{"route": "quality", "intent": "complex\_assessment"}

User: "ok got it"  
Heuristic: "state\_confident"  
{"route": "speed", "intent": "simple\_question"}

## **7\. Data Models (Schema)**

### **A. PostgreSQL: users table**

CREATE TABLE users (  
    id SERIAL PRIMARY KEY,  
    email VARCHAR(255) UNIQUE NOT NULL,  
    hashed\_password VARCHAR(255) NOT NULL,  
    has\_consented BOOLEAN DEFAULT FALSE,  
    created\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP  
);

### **B. Redis: Session Data**

* **Key:** session:{user\_id}  
* **Type:** List (LangChain's RedisChatMessageHistory can handle this)  
* **Purpose:** Store the *active* conversation history. If has\_consented is false, do not write to this key.

## **8\. API Endpoints (FastAPI)**

* POST /api/auth/register: (email, password) \-\> Saves to users table, returns JWT token.  
* POST /api/auth/login: (email, password) \-\> Verifies, returns JWT token.  
* POST /api/onboarding/consent: (Requires Auth) (body: {"consent": true}) \-\> Updates users.has\_consented for the user.  
* POST /api/chat: (Requires Auth) (body: {"message": "..."})  
  * This is the main endpoint.  
  * It will contain all the "Dynamic Model Router" logic (Section 4).  
  * It must be an async function.  
  * It must return a StreamingResponse (for SSE) that streams the tokens from the chosen Specialist model.